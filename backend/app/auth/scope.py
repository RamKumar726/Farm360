from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.customers import Customer
from app.models.farms import Farm
from app.models.leads import Lead
from app.models.projects import Project
from app.models.users import User, UserRole
from app.models.work_orders import WorkOrder


def scope_farms(query, user: User, db: Session):
    if user.role == UserRole.founder:
        return query
    if user.role == UserRole.customer:
        return query.join(Customer, Farm.customer_id == Customer.id).filter(Customer.user_id == user.id)
    if user.role == UserRole.zone_admin:
        return query.join(Customer, Farm.customer_id == Customer.id).filter(or_(
            and_(user.zone_id is not None, Farm.zone_id == user.zone_id),
            and_(user.branch_id is not None, Customer.branch_id == user.branch_id),
        ))
    if user.role == UserRole.employee:
        assigned_farms = db.query(WorkOrder.farm_id).filter(WorkOrder.assigned_employee_id == user.id)
        return query.filter(or_(Farm.id.in_(assigned_farms), and_(user.zone_id is not None, Farm.zone_id == user.zone_id)))
    if user.role == UserRole.agri_officer:
        assigned_farms = db.query(WorkOrder.farm_id).filter(WorkOrder.agri_officer_id == user.id)
        return query.filter(Farm.id.in_(assigned_farms))
    if user.role == UserRole.farm_employee:
        assigned_farms = db.query(WorkOrder.farm_id).filter(WorkOrder.farm_employee_id == user.id)
        return query.filter(Farm.id.in_(assigned_farms))
    if user.role == UserRole.work_partner:
        from app.models.work_partners import WorkPartner
        partner = db.query(WorkPartner).filter(WorkPartner.user_id == user.id).first()
        assigned_farms = db.query(WorkOrder.farm_id).filter(WorkOrder.outsourcing_partner_id == (partner.id if partner else ""))
        return query.filter(Farm.id.in_(assigned_farms))
    return query.filter(False)


def get_scoped_farm(db: Session, farm_id: str, user: User) -> Farm:
    farm = scope_farms(db.query(Farm).filter(Farm.id == farm_id), user, db).first()
    if not farm:
        raise HTTPException(404, "Farm not found")
    return farm


def scope_projects(query, user: User, db: Session):
    if user.role == UserRole.founder:
        return query
    if user.role == UserRole.customer:
        return query.filter(Project.customer_id == user.id)
    if user.role == UserRole.zone_admin:
        return query.filter(or_(
            Project.farm.has(and_(user.zone_id is not None, Farm.zone_id == user.zone_id)),
            Project.lead.has(or_(
                and_(user.branch_id is not None, Lead.branch_id == user.branch_id),
                and_(user.zone_id is not None, Lead.zone_id == user.zone_id),
            )),
        ))
    if user.role == UserRole.employee:
        return query.filter(or_(
            Project.posted_by == user.id,
            Project.lead.has(or_(Lead.employee_id == user.id, Lead.assigned_employee_id == user.id)),
            Project.id.in_(db.query(WorkOrder.project_id).filter(WorkOrder.assigned_employee_id == user.id)),
        ))
    if user.role == UserRole.agri_officer:
        return query.filter(or_(
            Project.assigned_ao_id == user.id,
            Project.id.in_(db.query(WorkOrder.project_id).filter(WorkOrder.agri_officer_id == user.id)),
        ))
    if user.role == UserRole.farm_employee:
        return query.filter(Project.id.in_(db.query(WorkOrder.project_id).filter(WorkOrder.farm_employee_id == user.id)))
    return query.filter(False)


def get_scoped_project(db: Session, project_id: str, user: User) -> Project:
    project = scope_projects(db.query(Project).filter(Project.id == project_id), user, db).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return project
