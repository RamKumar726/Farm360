import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.work_partners import WorkPartner, WorkPartnerStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.notification_service import notify_partner_response

router = APIRouter(prefix="/work-partners", tags=["work-partners"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class WorkPartnerCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    zone_id: Optional[str] = None
    work_types: Optional[list] = None
    payment_terms: Optional[str] = None


class PaymentAction(BaseModel):
    work_order_id: str
    amount: float
    is_full_payment: bool = True
    reason: Optional[str] = None


def wp_to_dict(w: WorkPartner):
    return {"id": w.id, "name": w.name, "contact": w.contact,
            "zone_id": w.zone_id, "work_types": w.work_types,
            "status": w.status.value, "payment_terms": w.payment_terms}


@router.get("")
def list_work_partners(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    zone_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(WorkPartner)
    if zone_id:
        query = query.filter(WorkPartner.zone_id == zone_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [wp_to_dict(w) for w in items]})


@router.post("")
def create_work_partner(
    body: WorkPartnerCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wp = WorkPartner(id=str(uuid.uuid4()), **body.dict())
    db.add(wp)
    db.commit()
    db.refresh(wp)
    return success(data=wp_to_dict(wp), message="Work partner added")


@router.post("/{wp_id}/accept")
def accept_work(
    wp_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    wp = db.query(WorkPartner).filter(WorkPartner.id == wp_id).first()
    if not wp:
        raise HTTPException(404, "Work partner not found")
    # Update status and notify employee
    notify_partner_response("system", wp.name, accepted=True, db=db)
    return success(message=f"Work partner '{wp.name}' accepted the assignment")


@router.post("/{wp_id}/reject")
def reject_work(
    wp_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    wp = db.query(WorkPartner).filter(WorkPartner.id == wp_id).first()
    if not wp:
        raise HTTPException(404, "Work partner not found")
    notify_partner_response("system", wp.name, accepted=False, db=db)
    return success(message=f"Work partner '{wp.name}' rejected. Please reassign.")


@router.post("/{wp_id}/verify")
def verify_work(
    wp_id: str,
    work_order_id: str,
    quality_good: bool = True,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.farm_employee)),
):
    """Verify work quality — good → full payment, bad → rework + reduced payment."""
    from app.models.work_orders import WorkOrder, WorkOrderStatus, PaymentStatus
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    if quality_good:
        wo.status = WorkOrderStatus.verified
        wo.payment_status = PaymentStatus.paid
        message = "Work verified as good — full payment released"
    else:
        wo.status = WorkOrderStatus.assigned  # Back to rework
        wo.payment_status = PaymentStatus.reduced
        message = "Work quality not satisfactory — rework required and payment reduced"
    db.commit()
    return success(data={"work_order_id": wo.id, "quality_good": quality_good}, message=message)


@router.post("/{wp_id}/payment")
def process_payment(
    wp_id: str, body: PaymentAction,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    from app.models.work_orders import WorkOrder, PaymentStatus
    wo = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    wo.payment_status = PaymentStatus.paid if body.is_full_payment else PaymentStatus.reduced
    db.commit()
    return success(message=f"Payment of ₹{body.amount:,.2f} processed ({'full' if body.is_full_payment else 'reduced'})")
