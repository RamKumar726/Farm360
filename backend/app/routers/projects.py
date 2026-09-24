import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.projects import Project, ProjectType, ProjectStatus, ProjectApprovalStatus
from app.models.prototypes import Prototype
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.notification_service import notify_investment_posted

router = APIRouter(prefix="/projects", tags=["projects"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class ProjectCreate(BaseModel):
    name: str
    type: ProjectType
    total_amount: float
    minimum_investment: float = 150000.0
    crop_name: Optional[str] = None
    farm_id: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    commercial_model_type: Optional[str] = None
    fixed_lease_amount: Optional[float] = 0.0
    revenue_share_percentage: Optional[float] = 0.0
    settlement_base: Optional[str] = None


class PrototypeCreate(BaseModel):
    crop_name: str
    total_duration_days: int = 120
    project_type: str = "managed"
    water_schedule_days: int = 15
    fertilizer_schedule_days: int = 25
    ao_visit_schedule_days: int = 15
    harvest_day: int = 120
    description: Optional[str] = None


class StatusUpdate(BaseModel):
    status: ProjectStatus
    total_revenue: Optional[float] = None
    total_expenses: Optional[float] = None


def proj_to_dict(p: Project):
    return {
        "id": p.id, "name": p.name, "type": p.type.value if hasattr(p.type, 'value') else p.type,
        "lead_id": p.lead_id, "farm_id": p.farm_id, "customer_id": p.customer_id,
        "total_amount": p.total_amount, "funded_amount": p.funded_amount,
        "minimum_investment": p.minimum_investment,
        "status": p.status.value if hasattr(p.status, 'value') else p.status,
        "approval_status": p.approval_status.value if hasattr(p.approval_status, 'value') else p.approval_status,
        "posted_by": p.posted_by,
        "description": p.description,
        "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None,
        "subscription_end": str(p.subscription_end) if p.subscription_end else None,
        "crop_name": p.crop_name, "assigned_ao_id": p.assigned_ao_id,
        "prototype_id": p.prototype_id,
        "commercial_model_type": p.commercial_model_type,
        "fixed_lease_amount": p.fixed_lease_amount,
        "revenue_share_percentage": p.revenue_share_percentage,
        "settlement_base": p.settlement_base,
        "total_revenue": p.total_revenue,
        "total_expenses": p.total_expenses,
        "landowner_settlement": p.landowner_settlement,
        "net_profit": (p.total_revenue or 0.0) - (p.total_expenses or 0.0) - (p.landowner_settlement or 0.0),
        "funding_percentage": round((p.funded_amount / p.total_amount) * 100, 1) if p.total_amount else 0,
        "cover_image_url": p.cover_image_url,
    }


@router.get("")
def list_projects(
    page: int = Query(1, ge=1), page_size: int = Query(50),
    status: Optional[ProjectStatus] = None,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Project)
    if current_user.role == UserRole.customer:
        from sqlalchemy import or_
        from app.models.customers import Customer
        from app.models.investments import Investment
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if status == ProjectStatus.open:
            query = query.filter(Project.approval_status == ProjectApprovalStatus.approved)
            query = query.filter(Project.status == ProjectStatus.open)
        else:
            investment_owned = Project.investments.any(Investment.customer_id == customer.id) if customer else Project.id == ""
            query = query.filter(or_(Project.customer_id == current_user.id, investment_owned))

    if status:
        query = query.filter(Project.status == status)
    if approval_status:
        query = query.filter(Project.approval_status == approval_status)

    total = query.count()
    items = query.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [proj_to_dict(p) for p in items]})


@router.post("")
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    # Founder direct post is approved, branch/zone admin post requires founder approval
    app_status = ProjectApprovalStatus.approved if current_user.role == UserRole.founder else ProjectApprovalStatus.pending_approval

    proj = Project(
        id=str(uuid.uuid4()),
        name=body.name, type=body.type,
        farm_id=body.farm_id,
        total_amount=body.total_amount,
        minimum_investment=body.minimum_investment,
        crop_name=body.crop_name,
        description=body.description,
        start_date=body.start_date or date.today(),
        end_date=body.end_date,
        cover_image_url=body.cover_image_url,
        commercial_model_type=body.commercial_model_type,
        fixed_lease_amount=body.fixed_lease_amount or 0.0,
        revenue_share_percentage=body.revenue_share_percentage or 0.0,
        settlement_base=body.settlement_base,
        posted_by=current_user.id,
        status=ProjectStatus.open,
        approval_status=app_status,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)

    if app_status == ProjectApprovalStatus.approved:
        from app.models.customers import Customer
        customers = db.query(Customer).filter(Customer.subscription_active == True).all()
        for c in customers:
            notify_investment_posted(c.user_id, proj.name, db)

    return success(data=proj_to_dict(proj), message="Project created" if app_status == ProjectApprovalStatus.approved else "Project posted and pending Founder approval")


@router.patch("/{proj_id}/approve")
def approve_project_listing(
    proj_id: str,
    approved: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder)),
):
    p = db.query(Project).filter(Project.id == proj_id).first()
    if not p: raise HTTPException(404, "Project not found")
    p.approval_status = ProjectApprovalStatus.approved if approved else ProjectApprovalStatus.rejected
    db.commit()

    if approved:
        from app.models.customers import Customer
        customers = db.query(Customer).filter(Customer.subscription_active == True).all()
        for c in customers:
            notify_investment_posted(c.user_id, p.name, db)

    return success(data=proj_to_dict(p), message=f"Project approval updated to {p.approval_status.value}")


@router.get("/prototypes")
def list_prototypes(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    items = db.query(Prototype).order_by(Prototype.created_at.desc()).all()
    res = [{
        "id": proto.id, "crop_name": proto.crop_name,
        "total_duration_days": proto.total_duration_days,
        "project_type": proto.project_type,
        "water_schedule_days": proto.water_schedule_days,
        "fertilizer_schedule_days": proto.fertilizer_schedule_days,
        "ao_visit_schedule_days": proto.ao_visit_schedule_days,
        "harvest_day": proto.harvest_day,
        "description": proto.description,
    } for proto in items]
    return success(data=res)


@router.post("/prototypes")
def create_prototype(
    body: PrototypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer, UserRole.founder)),
):
    proto = Prototype(
        id=str(uuid.uuid4()),
        crop_name=body.crop_name,
        total_duration_days=body.total_duration_days,
        project_type=body.project_type,
        water_schedule_days=body.water_schedule_days,
        fertilizer_schedule_days=body.fertilizer_schedule_days,
        ao_visit_schedule_days=body.ao_visit_schedule_days,
        harvest_day=body.harvest_day,
        description=body.description,
        created_by_ao_id=current_user.id,
    )
    db.add(proto)
    db.commit()
    db.refresh(proto)
    return success(data={"id": proto.id, "crop_name": proto.crop_name}, message="Crop prototype created successfully")


@router.post("/{proj_id}/apply-prototype")
def apply_prototype(
    proj_id: str,
    prototype_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer, UserRole.employee, UserRole.founder)),
):
    p = db.query(Project).filter(Project.id == proj_id).first()
    if not p: raise HTTPException(404, "Project not found")
    if current_user.role == UserRole.agri_officer and p.assigned_ao_id != current_user.id:
        raise HTTPException(404, "Project not found")
    if current_user.role == UserRole.employee and not (
        p.posted_by == current_user.id or
        (p.lead and current_user.id in (p.lead.employee_id, p.lead.assigned_employee_id))
    ):
        raise HTTPException(404, "Project not found")

    proto = db.query(Prototype).filter(Prototype.id == prototype_id).first()
    if not proto: raise HTTPException(404, "Prototype not found")

    required_project_type = {"managed": ProjectType.managing_farm, "lease": ProjectType.lease, "one_time": ProjectType.one_time_service}.get(proto.project_type)
    if not required_project_type or p.type != required_project_type or (p.crop_name or "").strip().casefold() != proto.crop_name.strip().casefold():
        raise HTTPException(400, "Prototype crop and project type must match")
    if p.prototype_id:
        raise HTTPException(409, "A prototype has already been applied to this project")

    # Resolve farm_id — must exist on the project
    if not p.farm_id:
        raise HTTPException(400, "Cannot apply prototype: Project has no associated farm. Set farm_id on the project first.")
    start = p.start_date or date.today()
    if not p.assigned_ao_id and current_user.role == UserRole.agri_officer:
        p.assigned_ao_id = current_user.id
    if proto.ao_visit_schedule_days and not p.assigned_ao_id:
        raise HTTPException(400, "Assign an Agriculture Officer before applying a prototype with AO visit tasks")
    from datetime import timedelta
    if p.type == ProjectType.managing_farm:
        schedule_end = p.subscription_end or (start + timedelta(days=30))
    else:
        schedule_end = p.end_date or (start + timedelta(days=proto.total_duration_days))
    p.prototype_id = proto.id
    from app.services.prototype_scheduler import schedule_prototype_tasks
    new_work_orders = schedule_prototype_tasks(p, proto, db, start, schedule_end, current_user.id)
    db.commit()
    return success(data={"tasks": [{"date": str(w.start_date), "type": w.type.value, "notes": w.notes} for w in new_work_orders]}, message=f"Applied prototype '{proto.crop_name}' to project. Created {len(new_work_orders)} scheduled tasks.")


@router.get("/{proj_id}")
def get_project(proj_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.id == proj_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    if current_user.role == UserRole.customer and p.customer_id != current_user.id and not (p.approval_status == ProjectApprovalStatus.approved and p.status == ProjectStatus.open):
        from app.models.customers import Customer
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        owns_investment = bool(customer and any(inv.customer_id == customer.id for inv in p.investments))
        if not owns_investment:
            raise HTTPException(404, "Project not found")
    return success(data=proj_to_dict(p))


@router.patch("/{proj_id}/status")
def update_project_status(
    proj_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    p = db.query(Project).filter(Project.id == proj_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    p.status = body.status
    if body.total_revenue is not None:
        p.total_revenue = body.total_revenue
    if body.total_expenses is not None:
        p.total_expenses = body.total_expenses
    p.net_profit = (p.total_revenue or 0.0) - (p.total_expenses or 0.0) - (p.landowner_settlement or 0.0)
    db.commit()

    if body.status in [ProjectStatus.completed, ProjectStatus.settled]:
        from app.models.investments import Investment
        from app.services.notification_service import notify_revenue_credited
        investments = db.query(Investment).filter(Investment.project_id == proj_id).all()
        for inv in investments:
            if inv.revenue_share_percentage is not None:
                inv.actual_return = round((inv.revenue_share_percentage / 100) * max(0.0, p.net_profit), 2)
                from app.models.customers import Customer
                c = db.query(Customer).filter(Customer.id == inv.customer_id).first()
                if c:
                    notify_revenue_credited(c.user_id, inv.actual_return, db)
        db.commit()
    return success(data=proj_to_dict(p), message="Project status updated")
