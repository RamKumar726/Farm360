import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.leads import Lead, LeadType, LeadSource, LeadStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.lead_service import transition_lead
from app.services.notification_service import notify_new_lead

router = APIRouter(prefix="/leads", tags=["leads"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class LeadCreate(BaseModel):
    type: LeadType
    source: LeadSource
    customer_id: Optional[str] = None
    zone_id: Optional[str] = None
    branch_id: Optional[str] = None
    farm_details: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    status: LeadStatus
    lost_reason: Optional[str] = None
    site_visit_date: Optional[date] = None
    advance_paid_date: Optional[date] = None


def lead_to_dict(l: Lead):
    return {
        "id": l.id, "type": l.type.value, "source": l.source.value,
        "status": l.status.value, "customer_id": l.customer_id,
        "employee_id": l.employee_id, "zone_id": l.zone_id,
        "branch_id": l.branch_id, "farm_details": l.farm_details,
        "site_visit_date": str(l.site_visit_date) if l.site_visit_date else None,
        "advance_paid_date": str(l.advance_paid_date) if l.advance_paid_date else None,
        "won_date": str(l.won_date) if l.won_date else None,
        "lost_reason": l.lost_reason, "created_at": str(l.created_at),
    }


@router.get("")
def list_leads(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    status: Optional[LeadStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Lead).filter(Lead.is_deleted == False)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Lead.branch_id == current_user.branch_id)
    elif current_user.role == UserRole.employee:
        query = query.filter(Lead.employee_id == current_user.id)
    if status:
        query = query.filter(Lead.status == status)
    total = query.count()
    items = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [lead_to_dict(l) for l in items]})


@router.post("")
def create_lead(
    body: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    lead = Lead(
        id=str(uuid.uuid4()),
        type=body.type, source=body.source,
        status=LeadStatus.new,
        customer_id=body.customer_id,
        employee_id=current_user.id,
        zone_id=body.zone_id or current_user.zone_id,
        branch_id=body.branch_id or current_user.branch_id,
        farm_details=body.farm_details,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    notify_new_lead(current_user.id, f"New lead #{lead.id[:8]} created ({lead.type.value})", db)
    return success(data=lead_to_dict(lead), message="Lead created")


@router.get("/lost")
def list_lost_leads(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Lost leads are NEVER deleted — stored for future reference
    query = db.query(Lead).filter(Lead.status == LeadStatus.lost)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Lead.branch_id == current_user.branch_id)
    elif current_user.role == UserRole.employee:
        query = query.filter(Lead.employee_id == current_user.id)
    total = query.count()
    items = query.order_by(Lead.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [lead_to_dict(l) for l in items]})


@router.get("/won")
def list_won_leads(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Lead).filter(Lead.status == LeadStatus.won)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Lead.branch_id == current_user.branch_id)
    elif current_user.role == UserRole.employee:
        query = query.filter(Lead.employee_id == current_user.id)
    total = query.count()
    items = query.order_by(Lead.won_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [lead_to_dict(l) for l in items]})


@router.get("/{lead_id}")
def get_lead(lead_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    return success(data=lead_to_dict(lead))


@router.patch("/{lead_id}/status")
def update_lead_status(
    lead_id: str,
    body: LeadStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    # Apply strict state machine
    transition_lead(lead, body.status, body.lost_reason)
    if body.site_visit_date:
        lead.site_visit_date = body.site_visit_date
    if body.advance_paid_date:
        lead.advance_paid_date = body.advance_paid_date
    if body.status == LeadStatus.won:
        from datetime import date
        lead.won_date = date.today()
    db.commit()
    db.refresh(lead)
    return success(data=lead_to_dict(lead), message=f"Lead status updated to {body.status.value}")
