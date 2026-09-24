import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from app.database import get_db
from app.models.work_orders import WorkOrder, WorkOrderType, WorkOrderStatus, PaymentStatus
from app.models.leads import Lead, LeadStatus
from app.models.users import User, UserRole
from app.models.work_partners import WorkPartner, WorkPartnerStatus
from app.models.proofs import Proof
from app.auth.dependencies import get_current_user, require_roles
from app.services.work_assignment_service import auto_assign_farm_employee
from app.services.notification_service import notify_work_order_created, notify_work_order_completed

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class WorkOrderCreate(BaseModel):
    farm_id: Optional[str] = None
    project_id: Optional[str] = None
    lead_id: Optional[str] = None
    type: WorkOrderType
    agri_officer_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class AssignPartner(BaseModel):
    partner_id: str


class AssignEmployee(BaseModel):
    employee_id: str


class StatusUpdate(BaseModel):
    status: WorkOrderStatus
    payment_status: Optional[PaymentStatus] = None


class WorkOrderClose(BaseModel):
    completion_notes: Optional[str] = None


def wo_to_dict(w: WorkOrder):
    return {
        "id": w.id, "farm_id": w.farm_id, "project_id": w.project_id, "lead_id": w.lead_id, "type": w.type.value if hasattr(w.type, 'value') else w.type,
        "status": w.status.value if hasattr(w.status, 'value') else w.status,
        "agri_officer_id": w.agri_officer_id,
        "start_date": str(w.start_date) if w.start_date else None,
        "end_date": str(w.end_date) if w.end_date else None,
        "outsourcing_partner_id": w.outsourcing_partner_id,
        "farm_employee_id": w.farm_employee_id,
        "assigned_employee_id": w.assigned_employee_id,
        "payment_status": w.payment_status.value if hasattr(w.payment_status, 'value') else w.payment_status,
        "notes": w.notes,
        "is_schedule_change_requested": w.is_schedule_change_requested,
        "schedule_change_reason": w.schedule_change_reason,
        "proposed_date": str(w.proposed_date) if w.proposed_date else None,
        "schedule_change_approval_status": w.schedule_change_approval_status,
        "proof_urls": w.proof_urls,
        "proofs": [{"id": proof.id, "image_url": proof.image_url, "note": proof.note,
                    "submitted_by": proof.submitted_by, "submitted_at": str(proof.submitted_at),
                    "reviewed_by": proof.reviewed_by, "reviewed_at": str(proof.reviewed_at) if proof.reviewed_at else None,
                    "review_status": proof.review_status} for proof in w.proofs],
        "proof_submitted_at": str(w.proof_submitted_at) if w.proof_submitted_at else None,
        "started_at": str(w.started_at) if w.started_at else None,
        "is_verified_by_employee": w.is_verified_by_employee,
        "is_accepted_by_customer": w.is_accepted_by_customer,
        "created_at": str(w.created_at),
    }


@router.get("")
def list_work_orders(
    page: int = Query(1, ge=1), page_size: int = Query(50),
    status: Optional[WorkOrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_roles = {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee, UserRole.customer, UserRole.work_partner}
    if current_user.role not in allowed_roles:
        raise HTTPException(403, "You cannot access work orders")
    query = db.query(WorkOrder).filter(WorkOrder.is_deleted == False)
    if current_user.role == UserRole.agri_officer:
        query = query.filter(WorkOrder.agri_officer_id == current_user.id)
    elif current_user.role == UserRole.farm_employee:
        query = query.filter(WorkOrder.farm_employee_id == current_user.id)
    elif current_user.role == UserRole.employee:
        query = query.filter((WorkOrder.assigned_employee_id == current_user.id) | (WorkOrder.created_by == current_user.id))
    elif current_user.role == UserRole.work_partner:
        from app.models.work_partners import WorkPartner, WorkPartnerStatus
        partner = db.query(WorkPartner).filter(WorkPartner.user_id == current_user.id, WorkPartner.status == WorkPartnerStatus.active).first()
        query = query.filter(WorkOrder.outsourcing_partner_id == (partner.id if partner else ""))
    elif current_user.role == UserRole.zone_admin:
        from app.models.projects import Project
        from app.models.farms import Farm
        scoped_leads = db.query(Lead.id)
        if current_user.branch_id:
            scoped_leads = scoped_leads.filter(Lead.branch_id == current_user.branch_id)
        elif current_user.zone_id:
            scoped_leads = scoped_leads.filter(Lead.zone_id == current_user.zone_id)
        else:
            scoped_leads = scoped_leads.filter(Lead.branch_id.is_(None), Lead.zone_id.is_(None))
        scoped_employees = db.query(User.id)
        if current_user.branch_id:
            scoped_employees = scoped_employees.filter(User.branch_id == current_user.branch_id)
        elif current_user.zone_id:
            scoped_employees = scoped_employees.filter(User.zone_id == current_user.zone_id)
        else:
            scoped_employees = scoped_employees.filter(User.id == current_user.id)
        scoped_projects = db.query(Project.id).filter(or_(
            Project.lead_id.in_(scoped_leads), Project.posted_by.in_(scoped_employees),
        ))
        scoped_farms = db.query(Farm.id).filter(Farm.zone_id == current_user.zone_id) if current_user.zone_id else db.query(Farm.id).filter(False)
        query = query.filter(or_(
            WorkOrder.created_by == current_user.id,
            WorkOrder.assigned_employee_id.in_(scoped_employees),
            WorkOrder.lead_id.in_(scoped_leads),
            WorkOrder.project_id.in_(scoped_projects),
            WorkOrder.farm_id.in_(scoped_farms),
        ))
    elif current_user.role == UserRole.customer:
        from sqlalchemy import or_
        from app.models.farms import Farm
        from app.models.customers import Customer
        from app.models.leads import Lead
        from app.models.projects import Project
        query = query.outerjoin(Farm, Farm.id == WorkOrder.farm_id).outerjoin(Customer, Customer.id == Farm.customer_id)
        query = query.outerjoin(Lead, Lead.id == WorkOrder.lead_id).outerjoin(Project, Project.id == WorkOrder.project_id)
        query = query.filter(or_(Customer.user_id == current_user.id, Lead.customer_id == current_user.id, Project.customer_id == current_user.id))
    if status:
        query = query.filter(WorkOrder.status == status)
    total = query.count()
    items = query.order_by(WorkOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [wo_to_dict(w) for w in items]})


@router.post("")
def create_work_order(
    body: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer)),
):
    assigned_ao_id = body.agri_officer_id or (current_user.id if current_user.role == UserRole.agri_officer else None)
    if body.type == WorkOrderType.monitoring:
        if not assigned_ao_id:
            raise HTTPException(400, "Assign an Agriculture Officer to an inspection task")
        officer = db.query(User).filter(
            User.id == assigned_ao_id, User.role == UserRole.agri_officer,
            User.is_deleted == False,
        ).first()
        if not officer:
            raise HTTPException(400, "Assigned Agriculture Officer must be active")
        if current_user.role == UserRole.agri_officer and officer.id != current_user.id:
            raise HTTPException(403, "An Agriculture Officer can only assign a visit to themselves")
        if body.farm_id:
            from app.models.farms import Farm
            farm = db.query(Farm).filter(Farm.id == body.farm_id).first()
            if not farm:
                raise HTTPException(404, "Farm not found")
            if farm.zone_id and officer.zone_id != farm.zone_id:
                raise HTTPException(400, "Agriculture Officer must belong to the farm's zone")
    elif assigned_ao_id:
        raise HTTPException(400, "Agriculture Officer assignment is reserved for inspection tasks")

    if body.project_id:
        from app.models.projects import Project
        project = db.query(Project).filter(Project.id == body.project_id).first()
        if not project:
            raise HTTPException(404, "Project not found")
        if body.farm_id and project.farm_id != body.farm_id:
            raise HTTPException(400, "Farm must belong to the selected project")
        if current_user.role in {UserRole.employee, UserRole.zone_admin}:
            from app.routers.finance import _can_manage_project
            if not _can_manage_project(project, current_user):
                raise HTTPException(404, "Project not found")
        if current_user.role == UserRole.agri_officer and project.assigned_ao_id != current_user.id:
            raise HTTPException(404, "Project not found")
        if project.farm_id and body.farm_id and project.farm_id != body.farm_id:
            raise HTTPException(400, "Farm must belong to the selected project")

    if body.lead_id:
        lead = db.query(Lead).filter(Lead.id == body.lead_id, Lead.is_deleted == False).first()
        if not lead:
            raise HTTPException(404, "Lead not found")
        from app.routers.leads import _authorize_lead
        _authorize_lead(lead, current_user, allow_unassigned=True)
        if body.project_id and lead.project_id and lead.project_id != body.project_id:
            raise HTTPException(400, "Lead and project must refer to the same deal")

    farm = None
    if body.farm_id:
        from app.models.farms import Farm
        farm = db.query(Farm).filter(Farm.id == body.farm_id).first()
        if not farm:
            raise HTTPException(404, "Farm not found")
        if current_user.role in {UserRole.employee, UserRole.zone_admin} and farm.zone_id != current_user.zone_id:
            raise HTTPException(404, "Farm not found")

    wo = WorkOrder(
        id=str(uuid.uuid4()),
        farm_id=body.farm_id, project_id=body.project_id, lead_id=body.lead_id, type=body.type,
        agri_officer_id=assigned_ao_id,
        start_date=body.start_date, end_date=body.end_date,
        notes=body.notes,
        status=WorkOrderStatus.assigned if assigned_ao_id else WorkOrderStatus.pending,
        payment_status=PaymentStatus.pending,
        created_by=current_user.id,
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    if assigned_ao_id:
        notify_work_order_created(assigned_ao_id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Work order created")


@router.get("/{wo_id}")
def get_work_order(wo_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.is_deleted == False).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    _authorize_work_order(wo, current_user, db)
    return success(data=wo_to_dict(wo))


@router.post("/{wo_id}/assign-partner")
def assign_partner(
    wo_id: str, body: AssignPartner,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.is_deleted == False).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    if wo.status not in {WorkOrderStatus.pending, WorkOrderStatus.assigned, WorkOrderStatus.partner_accepted}:
        raise HTTPException(400, "Outsourcing can only be assigned before work starts")
    if wo.type == WorkOrderType.monitoring:
        raise HTTPException(400, "Agriculture Officer visit tasks cannot be assigned to an outsourcing provider")
    partner = db.query(WorkPartner).filter(WorkPartner.id == body.partner_id, WorkPartner.status == WorkPartnerStatus.active).first()
    if not partner or not partner.user_id:
        raise HTTPException(404, "Active outsourcing partner with a linked portal account not found")
    if partner.work_types and wo.type.value not in partner.work_types:
        raise HTTPException(400, "Outsourcing partner is not approved for this work type")
    farm = None
    if wo.farm_id:
        from app.models.farms import Farm
        farm = db.query(Farm).filter(Farm.id == wo.farm_id).first()
        if not farm:
            raise HTTPException(404, "Farm not found")
        if farm and farm.zone_id and farm.zone_id != partner.zone_id:
            raise HTTPException(400, "Outsourcing partner is outside the farm's zone")
    wo.outsourcing_partner_id = body.partner_id
    if wo.status != WorkOrderStatus.partner_accepted:
        wo.status = WorkOrderStatus.assigned
    db.commit()
    if partner.user_id:
        notify_work_order_created(partner.user_id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Partner assigned")


@router.post("/{wo_id}/assign-farm-employee")
def assign_farm_employee(
    wo_id: str, body: AssignEmployee,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.is_deleted == False).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if wo.type == WorkOrderType.monitoring:
        raise HTTPException(400, "Agriculture Officer visit tasks cannot be assigned to a farm employee")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    if wo.status not in {WorkOrderStatus.pending, WorkOrderStatus.assigned, WorkOrderStatus.partner_accepted}:
        raise HTTPException(400, "A farm employee can only be assigned before work starts")
    employee = db.query(User).filter(User.id == body.employee_id, User.role == UserRole.farm_employee, User.is_available == True, User.is_deleted == False).first()
    if not employee:
        raise HTTPException(404, "Active farm employee not found")
    if wo.farm_id:
        from app.models.farms import Farm
        farm = db.query(Farm).filter(Farm.id == wo.farm_id).first()
    if farm and farm.zone_id and employee.zone_id != farm.zone_id:
        raise HTTPException(400, "Farm employee must be assigned to the farm's zone")
    wo.farm_employee_id = body.employee_id
    if wo.status not in {WorkOrderStatus.partner_accepted, WorkOrderStatus.in_progress}:
        wo.status = WorkOrderStatus.assigned
    db.commit()
    notify_work_order_created(employee.id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Farm employee manually assigned")


@router.post("/{wo_id}/assign-business-employee")
def assign_business_employee(
    wo_id: str, body: AssignEmployee,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.is_deleted == False).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    employee = db.query(User).filter(User.id == body.employee_id, User.role == UserRole.employee, User.is_deleted == False).first()
    if not employee:
        raise HTTPException(404, "Active business employee not found")
    wo.assigned_employee_id = employee.id
    if wo.status == WorkOrderStatus.pending:
        wo.status = WorkOrderStatus.assigned
    db.commit()
    db.refresh(wo)
    return success(data=wo_to_dict(wo), message="Business employee assigned")


@router.post("/{wo_id}/request-schedule-change")
def request_schedule_change(
    wo_id: str,
    reason: str = Query(...),
    proposed_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo: raise HTTPException(404, "Work order not found")
    if wo.agri_officer_id != current_user.id:
        raise HTTPException(403, "Only the assigned Agriculture Officer can change this schedule")
    if wo.status not in {WorkOrderStatus.pending, WorkOrderStatus.assigned, WorkOrderStatus.partner_accepted}:
        raise HTTPException(400, "The schedule can only be changed before work starts")
    if proposed_date < date.today():
        raise HTTPException(400, "The proposed work date cannot be in the past")
    wo.is_schedule_change_requested = True
    wo.schedule_change_reason = reason
    wo.proposed_date = proposed_date
    days_until_due = (wo.start_date - date.today()).days if wo.start_date else 99999
    if days_until_due < 4:
        wo.start_date = proposed_date
        wo.end_date = proposed_date
        wo.schedule_change_approval_status = "auto_approved"
        _reset_partner_for_date_confirmation(wo, db)
        assigned = None
        if wo.type != WorkOrderType.monitoring and not wo.farm_employee_id and not wo.outsourcing_partner_id:
            assigned = auto_assign_farm_employee(wo, db)
            if assigned:
                wo.status = WorkOrderStatus.assigned
        wo.is_schedule_change_requested = False
        db.commit()
        if assigned:
            notify_work_order_created(assigned.id, wo.id, db)
        _notify_schedule_assignees(wo, "Work schedule updated", db)
        return success(data=wo_to_dict(wo), message="Urgent change applied and assignment updated immediately")
    wo.schedule_change_approval_status = "pending"
    db.commit()
    _notify_schedule_approvers(wo, current_user.name, db)
    return success(data=wo_to_dict(wo), message="Urgent schedule change requested, sent to Zone Admin for approval")


@router.post("/{wo_id}/approve-schedule-change")
def approve_schedule_change(
    wo_id: str,
    approved: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.zone_admin, UserRole.founder)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo: raise HTTPException(404, "Work order not found")
    if current_user.role == UserRole.zone_admin:
        _authorize_work_order(wo, current_user, db)
    if wo.schedule_change_approval_status != "pending":
        raise HTTPException(400, "There is no pending schedule change for this work order")
    if not wo.proposed_date or wo.proposed_date < date.today():
        raise HTTPException(400, "The proposed schedule date is missing or has passed")
    assigned = None
    if approved and wo.proposed_date:
        wo.start_date = wo.proposed_date
        wo.end_date = wo.proposed_date
        wo.schedule_change_approval_status = "approved"
        _reset_partner_for_date_confirmation(wo, db)
        if wo.type != WorkOrderType.monitoring and not wo.farm_employee_id and not wo.outsourcing_partner_id:
            assigned = auto_assign_farm_employee(wo, db)
            if assigned:
                wo.status = WorkOrderStatus.assigned
    else:
        wo.schedule_change_approval_status = "rejected"
    wo.is_schedule_change_requested = False
    db.commit()
    if approved:
        if assigned:
            notify_work_order_created(assigned.id, wo.id, db)
        _notify_schedule_assignees(wo, "Approved schedule change", db)
    return success(data=wo_to_dict(wo), message=f"Schedule change approval status updated ({wo.schedule_change_approval_status})")


def _reset_partner_for_date_confirmation(wo: WorkOrder, db: Session) -> None:
    """A provider must explicitly confirm the replacement date after a change."""
    if wo.outsourcing_partner_id and wo.status == WorkOrderStatus.partner_accepted:
        wo.status = WorkOrderStatus.assigned


def _notify_schedule_assignees(wo: WorkOrder, message: str, db: Session) -> None:
    recipient_ids = {value for value in (wo.assigned_employee_id, wo.farm_employee_id, wo.agri_officer_id) if value}
    if wo.outsourcing_partner and wo.outsourcing_partner.user_id:
        recipient_ids.add(wo.outsourcing_partner.user_id)
    from app.models.notifications import NotificationType
    from app.services.notification_service import create_notification
    for recipient_id in recipient_ids:
        create_notification(
            recipient_id, NotificationType.work_order_created,
            f"{message} for work order #{wo.id[:8]}. New date: {wo.start_date}.", db=db,
        )


def _notify_schedule_approvers(wo: WorkOrder, requester_name: str, db: Session) -> None:
    from app.models.farms import Farm
    from app.services.notification_service import notify_approval_required
    farm = db.query(Farm).filter(Farm.id == wo.farm_id).first() if wo.farm_id else None
    admins_query = db.query(User).filter(User.role == UserRole.zone_admin, User.is_deleted == False)
    if farm and farm.zone_id:
        admins_query = admins_query.filter(User.zone_id == farm.zone_id)
    else:
        admins_query = admins_query.filter(False)
    reviewer_ids = {u.id for u in admins_query.all()}
    reviewer_ids.update(u.id for u in db.query(User).filter(
        User.role == UserRole.founder, User.is_deleted == False,
    ).all())
    context = (
        f"Schedule change requested by {requester_name} for work order #{wo.id[:8]}: "
        f"{wo.start_date} → {wo.proposed_date}. Reason: {wo.schedule_change_reason or 'Not provided'}"
    )
    for reviewer_id in reviewer_ids:
        notify_approval_required(reviewer_id, context, db)


@router.post("/{wo_id}/submit-proof")
def submit_proof(
    wo_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.farm_employee, UserRole.employee, UserRole.agri_officer, UserRole.work_partner, UserRole.founder)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo: raise HTTPException(404, "Work order not found")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    if current_user.role == UserRole.farm_employee and wo.farm_employee_id != current_user.id:
        raise HTTPException(403, "This work order is assigned to another farm employee")
    if current_user.role == UserRole.farm_employee and wo.outsourcing_partner_id and wo.status == WorkOrderStatus.partner_accepted:
        raise HTTPException(403, "The accepted outsourcing provider is responsible for starting this work")
    if current_user.role == UserRole.agri_officer and wo.agri_officer_id != current_user.id:
        raise HTTPException(403, "This work order is assigned to another Agriculture Officer")
    if current_user.role == UserRole.work_partner:
        _authorize_work_order(wo, current_user, db)
    if wo.status != WorkOrderStatus.in_progress:
        raise HTTPException(400, "Start the assigned work before submitting proof")
    from datetime import datetime
    import json
    urls = payload.get("proof_urls", [])
    if isinstance(urls, str):
        urls = [urls]
    if not isinstance(urls, list):
        raise HTTPException(400, "Proof URLs must be a list")
    urls = [url.strip() for url in urls if isinstance(url, str) and url.strip()]
    if not urls:
        raise HTTPException(400, "Upload at least one work proof before submitting")
    notes = payload.get("notes")
    for url in urls:
        db.add(Proof(id=str(uuid.uuid4()), work_order_id=wo.id, image_url=url,
                     note=notes, submitted_by=current_user.id))
    prior_urls = []
    try:
        prior_urls = json.loads(wo.proof_urls or "[]")
    except (TypeError, ValueError):
        prior_urls = [wo.proof_urls] if wo.proof_urls else []
    wo.proof_urls = json.dumps(list(dict.fromkeys(prior_urls + urls)))
    wo.proof_submitted_at = datetime.now()
    wo.status = WorkOrderStatus.proof_submitted
    db.commit()
    reviewer_id = wo.assigned_employee_id or wo.created_by
    if reviewer_id and reviewer_id != current_user.id:
        from app.services.notification_service import notify_proof_submitted
        notify_proof_submitted(reviewer_id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Proof of work submitted successfully")


@router.post("/{wo_id}/verify")
def verify_work_order(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    if wo.status != WorkOrderStatus.proof_submitted:
        raise HTTPException(400, "Proof must be submitted before employee verification")
    wo.is_verified_by_employee = True
    wo.status = WorkOrderStatus.verified
    from datetime import datetime, timezone
    for proof in wo.proofs:
        if proof.review_status == "submitted":
            proof.review_status = "verified"
            proof.reviewed_by = current_user.id
            proof.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    # Notify customer that work is verified
    from app.models.farms import Farm
    from app.models.customers import Customer
    farm = db.query(Farm).filter(Farm.id == wo.farm_id).first()
    if farm:
        customer = db.query(Customer).filter(Customer.id == farm.customer_id).first()
        if customer:
            notify_work_order_completed(customer.user_id, wo.id, db)
    elif wo.lead_id:
        lead = db.query(Lead).filter(Lead.id == wo.lead_id).first()
        if lead and lead.customer_id:
            notify_work_order_completed(lead.customer_id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Work order verified by employee")


@router.post("/{wo_id}/accept-work")
def accept_work_by_customer(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo: raise HTTPException(404, "Work order not found")
    if current_user.role != UserRole.customer:
        raise HTTPException(403, "Only the customer can accept completed work")
    from app.models.farms import Farm
    from app.models.customers import Customer
    from sqlalchemy import or_
    farm_owned = db.query(Farm).join(Customer, Customer.id == Farm.customer_id).filter(Farm.id == wo.farm_id, Customer.user_id == current_user.id).first()
    lead_owned = db.query(Lead).filter(Lead.id == wo.lead_id, Lead.customer_id == current_user.id).first()
    project_owned = None
    if wo.project_id:
        from app.models.projects import Project
        project_owned = db.query(Project).filter(Project.id == wo.project_id, Project.customer_id == current_user.id).first()
    if not (farm_owned or lead_owned or project_owned):
        raise HTTPException(404, "Work order not found")
    if wo.status != WorkOrderStatus.verified:
        raise HTTPException(400, "Work proof must be verified before customer acceptance")
    wo.is_accepted_by_customer = True
    wo.status = WorkOrderStatus.customer_accepted
    db.commit()
    return success(data=wo_to_dict(wo), message="Customer accepted work completion! Ticket is ready for closure.")


@router.post("/{wo_id}/close")
def close_work_order(wo_id: str, body: Optional[WorkOrderClose] = None, db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.employee, UserRole.zone_admin, UserRole.founder))):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.is_deleted == False).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    if wo.type == WorkOrderType.land_sale_followup:
        if wo.status not in {WorkOrderStatus.assigned, WorkOrderStatus.in_progress}:
            raise HTTPException(400, "Land sale follow-up must be assigned or in progress before closure")
        completion_notes = (body.completion_notes if body else None) or ""
        if not completion_notes.strip():
            raise HTTPException(400, "Record the follow-up outcome before closing this task")
        wo.status = WorkOrderStatus.completed
        wo.notes = f"{wo.notes or ''}\nCompletion: {completion_notes.strip()}".strip()
        db.commit()
        db.refresh(wo)
        return success(data=wo_to_dict(wo), message="Land sale follow-up closed")
    if wo.status != WorkOrderStatus.customer_accepted:
        raise HTTPException(400, "Customer acceptance is required before closing this work order")
    wo.status = WorkOrderStatus.completed
    if wo.lead_id:
        lead = db.query(Lead).filter(Lead.id == wo.lead_id).with_for_update().first()
        if lead and lead.type.value == "service_enquiry" and lead.status == LeadStatus.payment:
            from app.models.projects import Project, ProjectType, ProjectApprovalStatus, ProjectStatus
            from app.services.lead_service import transition_lead
            from app.models.customers import Customer
            from app.models.farms import Farm
            customer_profile = db.query(Customer).filter(Customer.user_id == lead.customer_id).first()
            farm = db.query(Farm).filter(Farm.customer_id == customer_profile.id).first() if customer_profile else None
            if customer_profile and not farm and lead.farm_location:
                farm = Farm(id=str(uuid.uuid4()), customer_id=customer_profile.id,
                            location=lead.farm_location, zone_id=lead.zone_id or customer_profile.zone_id,
                            notes=f"Service enquiry location: {lead.farm_details or lead.farm_location}")
                db.add(farm)
                db.flush()
            transition_lead(lead, LeadStatus.closed_won)
            project = db.query(Project).filter(Project.lead_id == lead.id).first()
            if not project:
                project = Project(
                    id=str(uuid.uuid4()), name=f"Project for Service #{lead.id[:8]}",
                    type=ProjectType.one_time_service, lead_id=lead.id, customer_id=lead.customer_id,
                    farm_id=farm.id if farm else None,
                    total_amount=lead.final_amount or lead.price_to_complete or 0,
                    status=ProjectStatus.completed, approval_status=ProjectApprovalStatus.approved,
                    posted_by=current_user.id, description=lead.farm_details, start_date=date.today(),
                )
                db.add(project)
                db.flush()
            lead.project_id = project.id
            lead.won_date = date.today()
            wo.project_id = project.id
            wo.farm_id = project.farm_id
    db.commit()
    db.refresh(wo)
    return success(data=wo_to_dict(wo), message="Work order closed")


@router.patch("/{wo_id}/status")
def update_status(
    wo_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if current_user.role not in [UserRole.employee, UserRole.zone_admin, UserRole.founder, UserRole.farm_employee, UserRole.agri_officer, UserRole.work_partner]:
        raise HTTPException(403, "You cannot change work order status")
    if current_user.role == UserRole.farm_employee and wo.farm_employee_id != current_user.id:
        raise HTTPException(403, "This work order is assigned to another farm employee")
    if current_user.role == UserRole.agri_officer and wo.agri_officer_id != current_user.id:
        raise HTTPException(403, "This work order is assigned to another Agriculture Officer")
    if current_user.role in {UserRole.employee, UserRole.zone_admin}:
        _authorize_work_order(wo, current_user, db)
    if current_user.role in {UserRole.farm_employee, UserRole.agri_officer, UserRole.work_partner}:
        _authorize_work_order(wo, current_user, db)
    if body.payment_status is not None:
        raise HTTPException(400, "Payment state is updated only through verified payment and finance workflows")
    if body.status != WorkOrderStatus.in_progress:
        raise HTTPException(400, "Use the dedicated proof, verification, customer acceptance, or closure action for this status")
    if wo.status not in [WorkOrderStatus.assigned, WorkOrderStatus.partner_accepted]:
        raise HTTPException(400, "Only an assigned task can be started")
    if wo.start_date and wo.start_date > date.today():
        raise HTTPException(400, "This work is scheduled for a future date")
    if current_user.role == UserRole.employee and (wo.farm_employee_id or wo.outsourcing_partner_id or wo.agri_officer_id):
        raise HTTPException(403, "Start work through the assigned field worker or Agriculture Officer")
    if current_user.role == UserRole.farm_employee and wo.outsourcing_partner_id and wo.status == WorkOrderStatus.partner_accepted:
        raise HTTPException(403, "The accepted outsourcing provider is responsible for starting this work")
    if current_user.role == UserRole.work_partner and wo.outsourcing_partner_id is None:
        raise HTTPException(403, "This work order is not assigned to your work partner account")
    wo.status = WorkOrderStatus.in_progress
    from datetime import datetime, timezone
    wo.started_at = datetime.now(timezone.utc)
    db.commit()
    return success(data=wo_to_dict(wo), message="Status updated")


def _authorize_work_order(wo: WorkOrder, user: User, db: Session) -> None:
    if user.role == UserRole.customer:
        from app.models.farms import Farm
        from app.models.customers import Customer
        from app.models.leads import Lead
        from app.models.projects import Project
        from sqlalchemy import or_
        owns_farm = db.query(Farm).join(Customer, Customer.id == Farm.customer_id).filter(Farm.id == wo.farm_id, Customer.user_id == user.id).first()
        owns_lead = db.query(Lead).filter(Lead.id == wo.lead_id, Lead.customer_id == user.id).first()
        owns_project = db.query(Project).filter(Project.id == wo.project_id, Project.customer_id == user.id).first()
        if not (owns_farm or owns_lead or owns_project):
            raise HTTPException(404, "Work order not found")
    elif user.role == UserRole.employee and user.id not in (wo.assigned_employee_id, wo.created_by):
        raise HTTPException(404, "Work order not found")
    elif user.role == UserRole.zone_admin:
        from app.models.projects import Project
        from app.models.farms import Farm
        project = db.query(Project).filter(Project.id == wo.project_id).first() if wo.project_id else None
        lead = db.query(Lead).filter(Lead.id == wo.lead_id).first() if wo.lead_id else None
        farm = db.query(Farm).filter(Farm.id == wo.farm_id).first() if wo.farm_id else None
        project_lead = db.query(Lead).filter(Lead.id == project.lead_id).first() if project and project.lead_id else None
        poster = db.query(User).filter(User.id == project.posted_by).first() if project else None
        branch_id = (lead.branch_id if lead else None) or (project_lead.branch_id if project_lead else None) or (poster.branch_id if poster else None)
        zone_id = (lead.zone_id if lead else None) or (project_lead.zone_id if project_lead else None) or (farm.zone_id if farm else None) or (poster.zone_id if poster else None)
        scoped = (user.branch_id is not None and branch_id == user.branch_id) or (
            user.branch_id is not None and branch_id is None and user.zone_id is not None and zone_id == user.zone_id
        ) or (user.branch_id is None and user.zone_id is not None and zone_id == user.zone_id) or (
            user.branch_id is None and user.zone_id is None and branch_id is None and zone_id is None
        )
        if not scoped:
            raise HTTPException(404, "Work order not found")
    elif user.role == UserRole.farm_employee and wo.farm_employee_id != user.id:
        raise HTTPException(404, "Work order not found")
    elif user.role == UserRole.agri_officer and wo.agri_officer_id != user.id:
        raise HTTPException(404, "Work order not found")
    elif user.role == UserRole.work_partner:
        from app.models.work_partners import WorkPartner, WorkPartnerStatus
        if not db.query(WorkPartner.id).filter(WorkPartner.id == wo.outsourcing_partner_id, WorkPartner.user_id == user.id, WorkPartner.status == WorkPartnerStatus.active).first():
            raise HTTPException(404, "Work order not found")
    elif user.role not in {UserRole.founder, UserRole.zone_admin}:
        raise HTTPException(403, "You cannot access this work order")
