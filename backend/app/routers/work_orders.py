import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.work_orders import WorkOrder, WorkOrderType, WorkOrderStatus, PaymentStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.work_assignment_service import auto_assign_farm_employee
from app.services.notification_service import notify_work_order_created, notify_work_order_completed

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class WorkOrderCreate(BaseModel):
    farm_id: str
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


def wo_to_dict(w: WorkOrder):
    return {
        "id": w.id, "farm_id": w.farm_id, "type": w.type.value,
        "status": w.status.value, "agri_officer_id": w.agri_officer_id,
        "start_date": str(w.start_date) if w.start_date else None,
        "end_date": str(w.end_date) if w.end_date else None,
        "outsourcing_partner_id": w.outsourcing_partner_id,
        "farm_employee_id": w.farm_employee_id,
        "payment_status": w.payment_status.value,
        "notes": w.notes, "created_at": str(w.created_at),
    }


@router.get("")
def list_work_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    status: Optional[WorkOrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(WorkOrder).filter(WorkOrder.is_deleted == False)
    if current_user.role == UserRole.agri_officer:
        query = query.filter(WorkOrder.agri_officer_id == current_user.id)
    elif current_user.role == UserRole.farm_employee:
        query = query.filter(WorkOrder.farm_employee_id == current_user.id)
    if status:
        query = query.filter(WorkOrder.status == status)
    total = query.count()
    items = query.order_by(WorkOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [wo_to_dict(w) for w in items]})


@router.post("")
def create_work_order(
    body: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = WorkOrder(
        id=str(uuid.uuid4()),
        farm_id=body.farm_id, type=body.type,
        agri_officer_id=body.agri_officer_id,
        start_date=body.start_date, end_date=body.end_date,
        notes=body.notes,
        status=WorkOrderStatus.pending,
        payment_status=PaymentStatus.pending,
        created_by=current_user.id,
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    # Auto-assign farm employee based on zone queue
    assigned = auto_assign_farm_employee(wo, db)
    if assigned:
        notify_work_order_created(assigned.id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Work order created")


@router.get("/{wo_id}")
def get_work_order(wo_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.is_deleted == False).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    return success(data=wo_to_dict(wo))


@router.post("/{wo_id}/assign-partner")
def assign_partner(
    wo_id: str, body: AssignPartner,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    wo.outsourcing_partner_id = body.partner_id
    wo.status = WorkOrderStatus.assigned
    db.commit()
    return success(data=wo_to_dict(wo), message="Partner assigned")


@router.post("/{wo_id}/assign-farm-employee")
def assign_farm_employee(
    wo_id: str, body: AssignEmployee,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    wo.farm_employee_id = body.employee_id
    db.commit()
    return success(data=wo_to_dict(wo), message="Farm employee manually assigned")


@router.post("/{wo_id}/verify")
def verify_work_order(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.farm_employee)),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    wo.status = WorkOrderStatus.verified
    db.commit()
    # Notify customer that work is verified
    from app.models.farms import Farm
    from app.models.customers import Customer
    farm = db.query(Farm).filter(Farm.id == wo.farm_id).first()
    if farm:
        customer = db.query(Customer).filter(Customer.id == farm.customer_id).first()
        if customer:
            notify_work_order_completed(customer.user_id, wo.id, db)
    return success(data=wo_to_dict(wo), message="Work order verified")


@router.patch("/{wo_id}/status")
def update_status(
    wo_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(404, "Work order not found")
    wo.status = body.status
    if body.payment_status:
        wo.payment_status = body.payment_status
    db.commit()
    return success(data=wo_to_dict(wo), message="Status updated")
