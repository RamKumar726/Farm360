"""Durable work-order assignment worker; run as a separate production process.

Usage: python -m app.services.work_order_scheduler
"""
import logging
import time
import uuid
from datetime import date, timedelta
from sqlalchemy import and_, or_

from app.database import SessionLocal
from app.models.work_orders import WorkOrder, WorkOrderStatus, WorkOrderType
from app.models.projects import Project, ProjectType, ProjectStatus
from app.models.leads import Lead, LeadType, LeadSource, LeadStatus
from app.models.users import User, UserRole
from app.services.notification_service import notify_work_order_created
from app.services.notification_service import notify_payment_due, notify_new_lead

logger = logging.getLogger("farm360.work_order_scheduler")


def assign_due_work_orders(db, today=None):
    today = today or date.today()
    cutoff = today + timedelta(days=4)
    query = db.query(WorkOrder).filter(
        WorkOrder.is_deleted == False,
        or_(
            WorkOrder.status == WorkOrderStatus.pending,
            and_(
                WorkOrder.type == WorkOrderType.monitoring,
                WorkOrder.agri_officer_id != None,
                WorkOrder.status == WorkOrderStatus.assigned,
            ),
        ),
        WorkOrder.assigned_employee_id == None,
        WorkOrder.farm_employee_id == None,
        WorkOrder.outsourcing_partner_id == None,
        WorkOrder.start_date != None,
        WorkOrder.start_date <= cutoff,
    ).order_by(WorkOrder.start_date).with_for_update(skip_locked=True)
    assigned_ids = []
    for work_order in query.all():
        lead = db.query(Lead).filter(Lead.id == work_order.lead_id).first() if work_order.lead_id else None
        project = db.query(Project).filter(Project.id == work_order.project_id).first() if work_order.project_id else None
        employee_id = (lead.assigned_employee_id or lead.employee_id) if lead else None
        employee = db.query(User).filter(User.id == employee_id, User.role == UserRole.employee, User.is_deleted == False).first() if employee_id else None
        branch_id = lead.branch_id if lead and lead.branch_id else (project.posted_by_user.branch_id if project and project.posted_by_user else None)
        zone_id = lead.zone_id if lead and lead.zone_id else (project.posted_by_user.zone_id if project and project.posted_by_user else None)
        if not employee:
            employee_query = db.query(User).filter(User.role == UserRole.employee, User.is_available == True, User.is_deleted == False)
            if branch_id:
                employee_query = employee_query.filter(User.branch_id == branch_id)
            elif zone_id:
                employee_query = employee_query.filter(User.zone_id == zone_id)
            employee = employee_query.order_by(User.created_at.asc()).first()
        if employee:
            work_order.assigned_employee_id = employee.id
            # AO monitoring visits are already assigned to their officer. The
            # employee is the internal reviewer for the submitted proof, so
            # retain the task's assigned state and AO owner.
            if work_order.status == WorkOrderStatus.pending:
                work_order.status = WorkOrderStatus.assigned
            db.flush()
            notify_work_order_created(employee.id, work_order.id, db)
            assigned_ids.append(work_order.id)
    if assigned_ids:
        db.commit()
    return assigned_ids


def create_due_subscription_renewals(db, today=None):
    today = today or date.today()
    cutoff = today + timedelta(days=3)
    projects = db.query(Project).filter(
        Project.type == ProjectType.managing_farm,
        Project.status == ProjectStatus.active,
        Project.customer_id != None,
        Project.subscription_end != None,
        Project.subscription_end <= cutoff,
    ).with_for_update(skip_locked=True).all()
    created = []
    for project in projects:
        renewal_date = project.subscription_end
        exists = db.query(Lead.id).filter(
            Lead.existing_project_id == project.id,
            Lead.renewal_for_date == renewal_date,
            Lead.type == LeadType.farm_manage,
        ).first()
        if exists:
            continue
        lead = Lead(
            id=str(uuid.uuid4()), type=LeadType.farm_manage,
            source=LeadSource.customer_app, status=LeadStatus.payment,
            customer_id=project.customer_id,
            assigned_ao_id=project.assigned_ao_id, is_opportunity=True,
            existing_project_id=project.id, renewal_for_date=renewal_date,
            farm_details=f"30-day farm management renewal for project {project.name}",
            price_to_complete=project.total_amount, final_amount=project.total_amount,
            sent_to_client=True,
            branch_id=(project.lead.branch_id if project.lead and project.lead.branch_id else project.posted_by_user.branch_id if project.posted_by_user else None),
            zone_id=(project.lead.zone_id if project.lead and project.lead.zone_id else project.posted_by_user.zone_id if project.posted_by_user else None),
        )
        from app.routers.leads import _assign_lead_owner
        _assign_lead_owner(lead, db)
        db.add(lead)
        db.flush()
        if lead.assigned_employee_id:
            notify_new_lead(lead.assigned_employee_id, f"Farm management renewal due for {project.name}", db)
        notify_payment_due(project.customer_id, project.total_amount, renewal_date, db)
        created.append(lead.id)
    if created:
        db.commit()
    return created


def run_forever(interval_seconds=300):
    logging.basicConfig(level=logging.INFO)
    logger.info("Farm360 work-order assignment worker started")
    while True:
        db = SessionLocal()
        try:
            assigned = assign_due_work_orders(db)
            if assigned:
                logger.info("Assigned %s due work orders", len(assigned))
            renewals = create_due_subscription_renewals(db)
            if renewals:
                logger.info("Created %s management renewals", len(renewals))
        except Exception:
            db.rollback()
            logger.exception("Work-order assignment cycle failed")
        finally:
            db.close()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_forever()
