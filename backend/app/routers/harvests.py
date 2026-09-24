import uuid
from typing import Optional
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.harvests import Harvest, HarvestStatus
from app.models.projects import Project
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/harvests", tags=["harvests"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class HarvestCreate(BaseModel):
    project_id: str
    farm_id: Optional[str] = None
    crop_cycle_id: Optional[str] = None
    work_order_id: Optional[str] = None
    crop_name: Optional[str] = None
    harvest_date: Optional[date] = None
    yield_quantity: Optional[float] = None
    yield_unit: str = "kg"
    market_price_per_unit: Optional[float] = None
    gross_revenue: Optional[float] = None
    buyer_name: Optional[str] = None
    sale_reference: Optional[str] = None
    harvesting_cost: Optional[float] = None
    transport_cost: Optional[float] = None
    other_expenses: Optional[float] = None
    landowner_share_pct: Optional[float] = None
    notes: Optional[str] = None
    proof_photos: Optional[str] = None


class HarvestUpdate(BaseModel):
    status: Optional[HarvestStatus] = None
    yield_quantity: Optional[float] = None
    market_price_per_unit: Optional[float] = None
    gross_revenue: Optional[float] = None
    harvesting_cost: Optional[float] = None
    transport_cost: Optional[float] = None
    other_expenses: Optional[float] = None
    landowner_share_pct: Optional[float] = None
    notes: Optional[str] = None
    proof_photos: Optional[str] = None


class RevenueReceipt(BaseModel):
    payment_reference: str


def harvest_to_dict(h: Harvest):
    # Compute net profit and landowner settlement
    gross = h.gross_revenue or 0.0
    costs = (h.harvesting_cost or 0.0) + (h.transport_cost or 0.0) + (h.other_expenses or 0.0)
    landowner_amt = round((gross * (h.landowner_share_pct or 0) / 100), 2)
    net = round(gross - costs - landowner_amt, 2)
    return {
        "id": h.id,
        "project_id": h.project_id,
        "farm_id": h.farm_id,
        "crop_cycle_id": h.crop_cycle_id,
        "work_order_id": h.work_order_id,
        "crop_name": h.crop_name,
        "harvest_date": str(h.harvest_date) if h.harvest_date else None,
        "yield_quantity": h.yield_quantity,
        "yield_unit": h.yield_unit,
        "market_price_per_unit": h.market_price_per_unit,
        "gross_revenue": gross,
        "buyer_name": h.buyer_name,
        "sale_reference": h.sale_reference,
        "is_revenue_received": bool(h.is_revenue_received),
        "revenue_payment_reference": h.revenue_payment_reference,
        "revenue_received_at": str(h.revenue_received_at) if h.revenue_received_at else None,
        "harvesting_cost": h.harvesting_cost,
        "transport_cost": h.transport_cost,
        "other_expenses": h.other_expenses,
        "landowner_share_pct": h.landowner_share_pct,
        "landowner_settlement_amount": landowner_amt,
        "net_profit": net,
        "status": h.status.value if hasattr(h.status, "value") else h.status,
        "notes": h.notes,
        "proof_photos": h.proof_photos,
        "created_at": str(h.created_at),
    }


@router.get("")
def list_harvests(
    page: int = Query(1, ge=1),
    page_size: int = Query(50),
    project_id: Optional[str] = None,
    farm_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.founder, UserRole.zone_admin, UserRole.employee,
        UserRole.agri_officer, UserRole.farm_employee, UserRole.customer,
    }:
        raise HTTPException(403, "You cannot access harvest records")
    query = db.query(Harvest)
    if current_user.role == UserRole.customer:
        query = query.join(Project, Project.id == Harvest.project_id).filter(Project.customer_id == current_user.id)
    elif current_user.role != UserRole.founder:
        from app.routers.finance import _can_view_project
        allowed_project_ids = [project.id for project in db.query(Project).all() if _can_view_project(project, current_user)]
        query = query.filter(Harvest.project_id.in_(allowed_project_ids or [""]))
    if project_id:
        query = query.filter(Harvest.project_id == project_id)
    if farm_id:
        query = query.filter(Harvest.farm_id == farm_id)
    total = query.count()
    items = query.order_by(Harvest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [harvest_to_dict(h) for h in items]})


@router.post("")
def create_harvest(
    body: HarvestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee
    )),
):
    # Auto-compute gross revenue if yield and price provided
    gross = body.gross_revenue
    if gross is None and body.yield_quantity and body.market_price_per_unit:
        gross = round(body.yield_quantity * body.market_price_per_unit, 2)

    project = db.query(Project).filter(Project.id == body.project_id).with_for_update().first()
    if not project:
        raise HTTPException(404, "Project not found")
    from app.routers.finance import _can_manage_project
    if current_user.role == UserRole.farm_employee:
        raise HTTPException(403, "Submit harvest-task proof first; an authorized project manager records the harvest")
    if not _can_manage_project(project, current_user):
        raise HTTPException(404, "Project not found")
    if body.farm_id and body.farm_id != project.farm_id:
        raise HTTPException(400, "Harvest farm must match the selected project")
    if project.type.value == "lease" and not body.work_order_id:
        raise HTTPException(400, "Lease harvests must be linked to the project harvest work order")
    if current_user.role == UserRole.agri_officer and project.assigned_ao_id != current_user.id:
        raise HTTPException(403, "Project is not assigned to you")
    if body.work_order_id:
        from app.models.work_orders import WorkOrder
        work_order = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id, WorkOrder.project_id == project.id).first()
        if not work_order:
            raise HTTPException(400, "Harvest work order must belong to this project")
        from app.models.work_orders import WorkOrderStatus, WorkOrderType
        if work_order.type != WorkOrderType.harvest:
            raise HTTPException(400, "Select a harvest work order")
        if work_order.status not in {WorkOrderStatus.verified, WorkOrderStatus.customer_accepted, WorkOrderStatus.completed}:
            raise HTTPException(400, "Verify the harvest work order before recording harvest results")
    harvest = Harvest(
        id=str(uuid.uuid4()),
        project_id=body.project_id,
        farm_id=body.farm_id,
        crop_cycle_id=body.crop_cycle_id,
        work_order_id=body.work_order_id,
        crop_name=body.crop_name,
        harvest_date=body.harvest_date or date.today(),
        yield_quantity=body.yield_quantity,
        yield_unit=body.yield_unit,
        market_price_per_unit=body.market_price_per_unit,
        gross_revenue=gross,
        buyer_name=body.buyer_name,
        sale_reference=body.sale_reference,
        harvesting_cost=body.harvesting_cost,
        transport_cost=body.transport_cost,
        other_expenses=body.other_expenses,
        landowner_share_pct=body.landowner_share_pct,
        notes=body.notes,
        proof_photos=body.proof_photos,
        status=HarvestStatus.completed,
        created_by=current_user.id,
    )
    db.add(harvest)
    db.commit()
    db.refresh(harvest)
    _sync_project_revenue(project.id, db)
    return success(data=harvest_to_dict(harvest), message="Harvest record created successfully")


@router.get("/{harvest_id}")
def get_harvest(harvest_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    h = db.query(Harvest).filter(Harvest.id == harvest_id).first()
    if not h:
        raise HTTPException(404, "Harvest record not found")
    from app.routers.finance import _can_view_project
    project = db.query(Project).filter(Project.id == h.project_id).first()
    if not project or not _can_view_project(project, current_user):
        raise HTTPException(404, "Harvest record not found")
    return success(data=harvest_to_dict(h))


@router.patch("/{harvest_id}")
def update_harvest(
    harvest_id: str,
    body: HarvestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer
    )),
):
    h = db.query(Harvest).filter(Harvest.id == harvest_id).first()
    if not h:
        raise HTTPException(404, "Harvest record not found")
    project = db.query(Project).filter(Project.id == h.project_id).first()
    from app.routers.finance import _can_manage_project
    if not project or not _can_manage_project(project, current_user):
        raise HTTPException(404, "Harvest record not found")
    project_id = h.project_id

    if body.status is not None: h.status = body.status
    if body.yield_quantity is not None: h.yield_quantity = body.yield_quantity
    if body.market_price_per_unit is not None: h.market_price_per_unit = body.market_price_per_unit
    if body.gross_revenue is not None:
        h.gross_revenue = body.gross_revenue
    elif h.yield_quantity and h.market_price_per_unit:
        h.gross_revenue = round(h.yield_quantity * h.market_price_per_unit, 2)
    if body.harvesting_cost is not None: h.harvesting_cost = body.harvesting_cost
    if body.transport_cost is not None: h.transport_cost = body.transport_cost
    if body.other_expenses is not None: h.other_expenses = body.other_expenses
    if body.landowner_share_pct is not None: h.landowner_share_pct = body.landowner_share_pct
    if body.notes is not None: h.notes = body.notes
    if body.proof_photos is not None: h.proof_photos = body.proof_photos

    db.commit()
    db.refresh(h)
    _sync_project_revenue(project_id, db)
    return success(data=harvest_to_dict(h), message="Harvest record updated")


def _sync_project_revenue(project_id: str, db: Session) -> None:
    from sqlalchemy import func
    total = db.query(func.coalesce(func.sum(Harvest.gross_revenue), 0)).filter(
        Harvest.project_id == project_id, Harvest.is_revenue_received == True
    ).scalar()
    project = db.query(Project).filter(Project.id == project_id).with_for_update().first()
    if project:
        project.total_revenue = float(total or 0)
        project.net_profit = project.total_revenue - (project.total_expenses or 0.0) - (project.landowner_settlement or 0.0)
        from app.services.investment_service import refresh_project_expected_returns
        refresh_project_expected_returns(project, db)
        db.commit()


@router.post("/{harvest_id}/record-payment")
def record_harvest_payment(
    harvest_id: str,
    body: RevenueReceipt,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    h = db.query(Harvest).filter(Harvest.id == harvest_id).with_for_update().first()
    if not h:
        raise HTTPException(404, "Harvest record not found")
    project = db.query(Project).filter(Project.id == h.project_id).first()
    from app.routers.finance import _can_manage_project
    if not project or not _can_manage_project(project, current_user):
        raise HTTPException(404, "Harvest record not found")
    if h.is_revenue_received:
        raise HTTPException(409, "Harvest revenue has already been recorded as received")
    if not h.gross_revenue or h.gross_revenue <= 0:
        raise HTTPException(400, "Record a positive sale amount before confirming receipt")
    if not body.payment_reference.strip():
        raise HTTPException(400, "Payment reference is required")
    h.is_revenue_received = True
    h.revenue_payment_reference = body.payment_reference.strip()
    h.revenue_received_at = datetime.now(timezone.utc)
    db.flush()
    _sync_project_revenue(project.id, db)
    db.refresh(h)
    return success(data=harvest_to_dict(h), message="Harvest revenue payment recorded")
