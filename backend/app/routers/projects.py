import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.projects import Project, ProjectType, ProjectStatus
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
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cover_image_url: Optional[str] = None


class StatusUpdate(BaseModel):
    status: ProjectStatus
    total_revenue: Optional[float] = None


def proj_to_dict(p: Project):
    return {
        "id": p.id, "name": p.name, "type": p.type.value,
        "total_amount": p.total_amount, "funded_amount": p.funded_amount,
        "status": p.status.value, "posted_by": p.posted_by,
        "description": p.description,
        "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None,
        "total_revenue": p.total_revenue,
        "funding_percentage": round((p.funded_amount / p.total_amount) * 100, 1) if p.total_amount else 0,
        "cover_image_url": p.cover_image_url,
    }


@router.get("")
def list_projects(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    status: Optional[ProjectStatus] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    total = query.count()
    items = query.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [proj_to_dict(p) for p in items]})


@router.post("")
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder)),
):
    proj = Project(
        id=str(uuid.uuid4()),
        name=body.name, type=body.type,
        total_amount=body.total_amount,
        description=body.description,
        start_date=body.start_date, end_date=body.end_date,
        cover_image_url=body.cover_image_url,
        posted_by=current_user.id,
        status=ProjectStatus.open,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    # Notify all active customers
    from app.models.customers import Customer
    customers = db.query(Customer).filter(Customer.subscription_active == True).all()
    for c in customers:
        notify_investment_posted(c.user_id, proj.name, db)
    return success(data=proj_to_dict(proj), message=f"Project posted and {len(customers)} customers notified")


@router.get("/{proj_id}")
def get_project(proj_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.id == proj_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    return success(data=proj_to_dict(p))


@router.patch("/{proj_id}/status")
def update_project_status(
    proj_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder)),
):
    p = db.query(Project).filter(Project.id == proj_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    p.status = body.status
    if body.total_revenue:
        p.total_revenue = body.total_revenue
    db.commit()
    # If completed/settled, trigger revenue share credit notifications
    if body.status in [ProjectStatus.completed, ProjectStatus.settled]:
        from app.models.investments import Investment
        from app.services.notification_service import notify_revenue_credited
        investments = db.query(Investment).filter(Investment.project_id == proj_id).all()
        for inv in investments:
            if p.total_revenue and inv.revenue_share_percentage:
                inv.actual_return = round((inv.revenue_share_percentage / 100) * p.total_revenue, 2)
                from app.models.customers import Customer
                c = db.query(Customer).filter(Customer.id == inv.customer_id).first()
                if c:
                    notify_revenue_credited(c.user_id, inv.actual_return, db)
        db.commit()
    return success(data=proj_to_dict(p), message="Project status updated")
