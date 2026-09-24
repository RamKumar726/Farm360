import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.land_sales import LandSale, LandType, LandSaleStatus
from app.models.users import User, UserRole
from app.models.leads import Lead, LeadType, LeadSource, LeadStatus
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
        "id": l.id, "land_type": l.land_type.value if hasattr(l.land_type, 'value') else l.land_type,
        "area": l.area, "location": l.location, "facing": l.facing, "listed_price": l.listed_price,
        "status": l.status.value if hasattr(l.status, 'value') else l.status,
        "broker_ids": l.broker_ids,
        "is_broadcasted": l.is_broadcasted,
        "broadcasted_at": str(l.broadcasted_at) if l.broadcasted_at else None,
        "broadcast_recipients_count": l.broadcast_recipients_count,
        "description": l.description, "photos": l.photos,
        "listed_at": str(l.listed_at) if l.listed_at else None,
    }


@router.get("")
def list_land_sales(
    page: int = Query(1, ge=1), page_size: int = Query(50),
    status: Optional[LandSaleStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(LandSale)
    if current_user.role == UserRole.customer:
        from app.models.customers import Customer
        c = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        from sqlalchemy import or_
        query = query.filter(or_(LandSale.status.in_([LandSaleStatus.listed, LandSaleStatus.broadcast]), LandSale.customer_id == (c.id if c else "")))
    if status:
        if current_user.role == UserRole.customer and status == LandSaleStatus.listed:
            query = query.filter(or_(LandSale.status.in_([LandSaleStatus.listed, LandSaleStatus.broadcast]), LandSale.customer_id == (c.id if c else "")))
        else:
            query = query.filter(LandSale.status == status)
    total = query.count()
    items = query.order_by(LandSale.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [ls_to_dict(l) for l in items]})


@router.post("")
def create_land_sale(body: LandSaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.customer, UserRole.real_estate]:
        raise HTTPException(403, "Land sale requests can be created by customers and landowners")
    from app.models.customers import Customer
    from app.models.real_estate_users import RealEstateUser
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first() if current_user.role == UserRole.customer else None
    owner = db.query(RealEstateUser).filter(RealEstateUser.user_id == current_user.id).first() if current_user.role == UserRole.real_estate else None
    if current_user.role == UserRole.customer and not customer:
        raise HTTPException(400, "Customer profile is required")
    if current_user.role == UserRole.real_estate and not owner:
        raise HTTPException(400, "Landowner profile is required")
    fields = body.dict(exclude={"customer_id", "real_estate_user_id"})
    ls = LandSale(id=str(uuid.uuid4()), **fields,
                  customer_id=customer.id if customer else None,
                  real_estate_user_id=owner.id if owner else None)
    db.add(ls)
    is_existing_customer = customer is not None
    lead = Lead(id=str(uuid.uuid4()), type=LeadType.sell_land, source=LeadSource.customer_app,
                status=LeadStatus.prospecting, customer_id=current_user.id if is_existing_customer else None,
                contact_name=current_user.name, contact_phone=current_user.phone, contact_email=current_user.email,
                is_opportunity=is_existing_customer, related_land_sale_id=ls.id,
                branch_id=current_user.branch_id, zone_id=current_user.zone_id,
                farm_location=ls.location,
                farm_details=f"Sell my land request: {ls.area or 'Area TBD'} acres at {ls.location or 'Location TBD'}; asking ₹{ls.listed_price or 'TBD'}.")
    from app.routers.leads import _assign_lead_owner
    _assign_lead_owner(lead, db, creator=current_user)
    db.add(lead)
    db.commit()
    db.refresh(ls)
    db.refresh(lead)
    if lead.assigned_employee_id:
        from app.services.notification_service import notify_new_lead
        notify_new_lead(lead.assigned_employee_id, f"New land sale request #{lead.id[:8]}", db)
    return success(data={**ls_to_dict(ls), "lead_id": lead.id}, message="Land sale request created and assigned for review")


@router.get("/{ls_id}")
def get_land_sale(ls_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    if current_user.role == UserRole.customer:
        from app.models.customers import Customer
        profile = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if ls.status not in [LandSaleStatus.listed, LandSaleStatus.broadcast] and (not profile or ls.customer_id != profile.id):
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
    """Broadcast land listing to all brokers and customers."""
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    if ls.is_broadcasted:
        return success(data=ls_to_dict(ls), message="This land listing has already been broadcast")
    if ls.status not in [LandSaleStatus.listed, LandSaleStatus.broadcast]:
        raise HTTPException(400, "Post the land listing publicly before broadcasting it")

    from app.models.brokers import Broker
    from app.models.customers import Customer
    brokers = db.query(Broker).all()
    broker_ids = [b.id for b in brokers]
    customers = db.query(Customer).filter(Customer.is_deleted == False).all()

    ls.broker_ids = broker_ids
    ls.status = LandSaleStatus.broadcast
    ls.is_broadcasted = True
    ls.broadcasted_at = datetime.utcnow()
    ls.broadcast_recipients_count = len(brokers) + len(customers)
    db.commit()

    for c in customers:
        notify_land_sale_listed(c.user_id, ls.location or "unspecified location", db)
    for broker in brokers:
        if broker.user_id:
            notify_land_sale_listed(broker.user_id, ls.location or "unspecified location", db)
    return success(data=ls_to_dict(ls), message=f"Broadcast sent to {len(brokers)} brokers and {len(customers)} customers")



@router.post("/{ls_id}/interest")
def express_interest(ls_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    if current_user.role != UserRole.customer or ls.status not in [LandSaleStatus.listed, LandSaleStatus.broadcast]:
        raise HTTPException(400, "Only customers can express interest in active land listings")
    existing = db.query(Lead).filter(Lead.customer_id == current_user.id, Lead.related_land_sale_id == ls.id, Lead.type == LeadType.land_purchase_interest).first()
    if existing:
        return success(data={"lead_id": existing.id}, message="Your interest is already registered")
    lead = Lead(id=str(uuid.uuid4()), type=LeadType.land_purchase_interest,
                source=LeadSource.customer_app, status=LeadStatus.prospecting,
                customer_id=current_user.id, is_opportunity=True,
                related_land_sale_id=ls.id,
                farm_details=f"Interest in land listing #{ls.id[:8]} at {ls.location or 'unspecified location'}")
    db.add(lead)
    from app.routers.leads import _assign_lead_owner
    _assign_lead_owner(lead, db, creator=current_user)
    db.commit()
    if lead.assigned_employee_id:
        from app.services.notification_service import notify_new_lead
        notify_new_lead(lead.assigned_employee_id, f"New land purchase interest #{lead.id[:8]}", db)
    return success(data={"lead_id": lead.id}, message="Interest registered — the sales team will contact you")


@router.patch("/{ls_id}/status")
def update_status(
    ls_id: str, body: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    ls = db.query(LandSale).filter(LandSale.id == ls_id).first()
    if not ls:
        raise HTTPException(404, "Land sale not found")
    ls.status = body.status
    if body.status == LandSaleStatus.sold:
        ls.sold_at = datetime.utcnow()
    db.commit()
    return success(data=ls_to_dict(ls), message="Status updated")
