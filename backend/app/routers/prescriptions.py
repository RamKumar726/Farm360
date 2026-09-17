import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from app.database import get_db
from app.models.prescriptions import Prescription, PrescriptionStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.notification_service import notify_prescription_sent

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class PrescriptionCreate(BaseModel):
    farm_id: str
    work_order_id: Optional[str] = None
    prescription_text: str
    quote_amount: Optional[float] = None
    sent_to: Optional[list] = None   # ["customer", "admin", "employee"]
    attachment_url: Optional[str] = None


class StatusUpdate(BaseModel):
    status: PrescriptionStatus


def p_to_dict(p: Prescription):
    return {
        "id": p.id, "farm_id": p.farm_id, "agri_officer_id": p.agri_officer_id,
        "work_order_id": p.work_order_id, "prescription_text": p.prescription_text,
        "quote_amount": p.quote_amount, "sent_to": p.sent_to,
        "status": p.status.value, "created_at": str(p.created_at),
    }


@router.get("")
def list_prescriptions(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Prescription)
    if current_user.role == UserRole.agri_officer:
        query = query.filter(Prescription.agri_officer_id == current_user.id)
    total = query.count()
    items = query.order_by(Prescription.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [p_to_dict(p) for p in items]})


@router.post("")
def create_prescription(
    body: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer, UserRole.founder)),
):
    p = Prescription(
        id=str(uuid.uuid4()),
        farm_id=body.farm_id,
        agri_officer_id=current_user.id,
        work_order_id=body.work_order_id,
        prescription_text=body.prescription_text,
        quote_amount=body.quote_amount,
        sent_to=body.sent_to or [],
        attachment_url=body.attachment_url,
        status=PrescriptionStatus.sent,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    # Notify recipients
    if body.sent_to:
        for recipient_role in body.sent_to:
            # In real implementation, resolve user by role+farm; here notify agri_officer as placeholder
            notify_prescription_sent(current_user.id, p.id, db)
    return success(data=p_to_dict(p), message="Prescription sent")


@router.get("/{p_id}")
def get_prescription(p_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    p = db.query(Prescription).filter(Prescription.id == p_id).first()
    if not p:
        raise HTTPException(404, "Prescription not found")
    return success(data=p_to_dict(p))


@router.patch("/{p_id}/status")
def update_status(
    p_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    p = db.query(Prescription).filter(Prescription.id == p_id).first()
    if not p:
        raise HTTPException(404, "Prescription not found")
    p.status = body.status
    db.commit()
    return success(data=p_to_dict(p), message="Prescription status updated")
