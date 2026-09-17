import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.land_sales import LandSale, LandType, LandSaleStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.notification_service import notify_land_sale_listed

router = APIRouter(prefix="/land-sales", tags=["land-sales"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class LandSaleCreate(BaseModel):
    land_type: LandType
    area: Optional[float] = None
    location: Optional[str] = None
    facing: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    listed_price: Optional[float] = None
    description: Optional[str] = None
    customer_id: Optional[str] = None
    real_estate_user_id: Optional[str] = None


class StatusUpdate(BaseModel):
    status: LandSaleStatus


def ls_to_dict(l: LandSale):
    return {
        "id": l.id, "land_type": l.land_type.value, "area": l.area,
        "location": l.location, "facing": l.facing, "listed_price": l.listed_price,
        "status": l.status.value, "broker_ids": l.broker_ids,
        "description": l.description, "photos": l.photos,
        "listed_at": str(l.listed_at) if l.listed_at else None,
    }


@router.get("")
def list_land_sales(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    status: Optional[LandSaleStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(LandSale)
    if current_user.role == UserRole.customer:
        from app.models.customers import Customer
        c = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if c:
            query = query.filter(LandSale.customer_id == c.id)
    if status:
        query = query.filter(LandSale.status == status)
    total = query.count()
    items = query.order_by(LandSale.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [ls_to_dict(l) for l in items]})


@router.post("")
def create_land_sale(body: LandSaleCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ls = LandSale(id=str(uuid.uuid4()), **body.dict())
    db.add(ls)
    db.commit()
    db.refresh(ls)
    return success(data=ls_to_dict(ls), message="Land sale listing created")


@router.get("/{ls_id}")
def get_land_sale(ls_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    return success(data=ls_to_dict(ls))


@router.post("/{ls_id}/post-public")
def post_public(
    ls_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    ls.status = LandSaleStatus.listed
    ls.listed_at = datetime.utcnow()
    db.commit()
    return success(data=ls_to_dict(ls), message="Land sale posted publicly")


@router.post("/{ls_id}/broadcast")
def broadcast_to_brokers(
    ls_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    """Broadcast land listing to all brokers and customers in the zone."""
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    # Get zone from customer's farm
    from app.models.brokers import Broker
    from app.models.customers import Customer
    # Notify all brokers
    brokers = db.query(Broker).all()
    broker_ids = []
    for broker in brokers:
        broker_ids.append(broker.id)
        # Notify broker's user if linked
    ls.broker_ids = broker_ids
    ls.status = LandSaleStatus.broadcast
    db.commit()
    # Notify all customers
    customers = db.query(Customer).filter(Customer.subscription_active == True).all()
    for c in customers:
        notify_land_sale_listed(c.user_id, ls.location or "unspecified location", db)
    return success(data=ls_to_dict(ls), message=f"Broadcast sent to {len(brokers)} brokers and {len(customers)} customers")


@router.post("/{ls_id}/interest")
def express_interest(ls_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    ls.status = LandSaleStatus.interested
    db.commit()
    return success(data=ls_to_dict(ls), message="Interest registered — follow-up lead created")


@router.patch("/{ls_id}/status")
def update_status(
    ls_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    ls.status = body.status
    if body.status == LandSaleStatus.sold:
        ls.sold_at = datetime.utcnow()
    db.commit()
    return success(data=ls_to_dict(ls), message="Status updated")
