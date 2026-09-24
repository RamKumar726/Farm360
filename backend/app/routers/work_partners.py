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
    user_id: Optional[str] = None
    user_email: Optional[str] = None


class WorkPartnerDecision(BaseModel):
    work_order_id: str
    confirmed_start_date: Optional[date] = None


class WorkPartnerAccountLink(BaseModel):
    user_email: str


class PaymentAction(BaseModel):
    work_order_id: str
    amount: float
    is_full_payment: bool = True
    reason: Optional[str] = None


def wp_to_dict(w: WorkPartner):
    return {"id": w.id, "name": w.name, "contact": w.contact,
            "user_id": w.user_id,
            "zone_id": w.zone_id, "work_types": w.work_types,
            "status": w.status.value, "payment_terms": w.payment_terms}


@router.get("")
def list_work_partners(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    zone_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.work_partner}:
        raise HTTPException(403, "You cannot access work partner records")
    query = db.query(WorkPartner)
    if current_user.role == UserRole.work_partner:
        query = query.filter(WorkPartner.user_id == current_user.id)
    elif current_user.role in {UserRole.zone_admin, UserRole.employee}:
        query = query.filter(WorkPartner.zone_id == current_user.zone_id) if current_user.zone_id else query.filter(False)
    if zone_id:
        query = query.filter(WorkPartner.zone_id == zone_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [wp_to_dict(w) for w in items]})


@router.post("")
def create_work_partner(
    body: WorkPartnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    data = body.dict(exclude={"user_email"})
    if not body.user_email and not data.get("user_id"):
        raise HTTPException(400, "Link an authenticated Work Partner account to enable assignments")
    if body.user_email or data.get("user_id"):
        account_query = db.query(User).filter(User.role == UserRole.work_partner, User.is_deleted == False)
        account = account_query.filter(User.email == body.user_email).first() if body.user_email else account_query.filter(User.id == data["user_id"]).first()
        if not account:
            raise HTTPException(400, "Create an active Work Partner user account with this email first")
        if data.get("zone_id") and account.zone_id != data["zone_id"]:
            raise HTTPException(400, "Provider login and partner record must belong to the same zone")
        if data.get("user_id") and data["user_id"] != account.id:
            raise HTTPException(400, "Use either the provider email or user ID, not different accounts")
        data["user_id"] = account.id
        data["zone_id"] = data.get("zone_id") or account.zone_id
    if not data.get("zone_id"):
        raise HTTPException(400, "Assign the provider login to a zone before linking it")
    if current_user.role in {UserRole.zone_admin, UserRole.employee} and data["zone_id"] != current_user.zone_id:
        raise HTTPException(404, "You cannot create a provider outside your zone")
    wp = WorkPartner(id=str(uuid.uuid4()), **data)
    db.add(wp)
    db.commit()
    db.refresh(wp)
    return success(data=wp_to_dict(wp), message="Work partner added")


@router.patch("/{wp_id}/account")
def link_partner_account(
    wp_id: str,
    body: WorkPartnerAccountLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    partner = db.query(WorkPartner).filter(WorkPartner.id == wp_id).first()
    if not partner:
        raise HTTPException(404, "Work partner not found")
    if current_user.role in {UserRole.zone_admin, UserRole.employee} and partner.zone_id != current_user.zone_id:
        raise HTTPException(404, "Work partner not found")
    account = db.query(User).filter(User.email == body.user_email, User.role == UserRole.work_partner, User.is_deleted == False).first()
    if not account:
        raise HTTPException(404, "Active Work Partner account not found")
    if not partner.zone_id or account.zone_id != partner.zone_id:
        raise HTTPException(400, "Provider login and partner record must belong to the same zone")
    if db.query(WorkPartner.id).filter(WorkPartner.user_id == account.id, WorkPartner.id != partner.id).first():
        raise HTTPException(409, "This account is already linked to another work partner")
    partner.user_id = account.id
    db.commit()
    db.refresh(partner)
    return success(data=wp_to_dict(partner), message="Work Partner portal account linked")


@router.post("/{wp_id}/accept")
def accept_work(
    wp_id: str,
    body: WorkPartnerDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.work_partner)),
):
    from app.models.work_orders import WorkOrder, WorkOrderStatus
    wp = db.query(WorkPartner).filter(WorkPartner.id == wp_id, WorkPartner.user_id == current_user.id, WorkPartner.status == WorkPartnerStatus.active).first()
    wo = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id, WorkOrder.outsourcing_partner_id == wp_id).with_for_update().first() if wp else None
    if not wp or not wo:
        raise HTTPException(404, "Work partner not found")
    if wo.status != WorkOrderStatus.assigned:
        raise HTTPException(400, "Only an assigned work order can be confirmed")
    if body.confirmed_start_date is None:
        raise HTTPException(400, "Confirm the work date before accepting the assignment")
    if body.confirmed_start_date < date.today():
        raise HTTPException(400, "Confirmed work date cannot be in the past")
    wo.start_date = body.confirmed_start_date
    wo.end_date = body.confirmed_start_date
    wo.status = WorkOrderStatus.partner_accepted
    db.commit()
    if wo.assigned_employee_id:
        notify_partner_response(wo.assigned_employee_id, wp.name, accepted=True, db=db)
    return success({"work_order_id": wo.id, "status": wo.status.value, "start_date": str(wo.start_date) if wo.start_date else None}, "Assignment and work date confirmed")


@router.post("/{wp_id}/reject")
def reject_work(
    wp_id: str,
    body: WorkPartnerDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.work_partner)),
):
    from app.models.work_orders import WorkOrder, WorkOrderStatus
    wp = db.query(WorkPartner).filter(WorkPartner.id == wp_id, WorkPartner.user_id == current_user.id, WorkPartner.status == WorkPartnerStatus.active).first()
    wo = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id, WorkOrder.outsourcing_partner_id == wp_id).with_for_update().first() if wp else None
    if not wp or not wo:
        raise HTTPException(404, "Work partner not found")
    if wo.status != WorkOrderStatus.assigned:
        raise HTTPException(400, "Only an assigned work order can be rejected")
    wo.outsourcing_partner_id = None
    wo.status = WorkOrderStatus.pending
    db.commit()
    if wo.assigned_employee_id:
        notify_partner_response(wo.assigned_employee_id, wp.name, accepted=False, db=db)
    return success({"work_order_id": wo.id, "status": wo.status.value}, "Assignment rejected; work order returned to the employee queue")


@router.post("/{wp_id}/verify")
def verify_work(
    wp_id: str,
    work_order_id: str,
    quality_good: bool = True,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.farm_employee)),
):
    raise HTTPException(410, "Submit task proof, verify it through the work-order review, and record provider payment as a project expense")


@router.post("/{wp_id}/payment")
def process_payment(
    wp_id: str, body: PaymentAction,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    raise HTTPException(410, "Record provider costs and payment references through project finance expenses")
