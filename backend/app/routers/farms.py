import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.farms import Farm
from app.models.customers import Customer
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/farms", tags=["farms"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class FarmCreate(BaseModel):
    customer_id: str
    location: Optional[str] = None
    area: Optional[float] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    soil_type: Optional[str] = None
    water_source: Optional[str] = None
    zone_id: Optional[str] = None
    notes: Optional[str] = None


def farm_to_dict(f: Farm):
    return {
        "id": f.id, "customer_id": f.customer_id, "location": f.location,
        "area": f.area, "gps_lat": f.gps_lat, "gps_lng": f.gps_lng,
        "soil_type": f.soil_type, "water_source": f.water_source,
        "zone_id": f.zone_id, "notes": f.notes,
    }


@router.get("")
def list_farms(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Farm)
    if current_user.role == UserRole.customer:
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if customer:
            query = query.filter(Farm.customer_id == customer.id)
    elif current_user.role == UserRole.zone_admin:
        query = query.join(Customer).filter(Customer.branch_id == current_user.branch_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [farm_to_dict(f) for f in items]})


@router.post("")
def create_farm(
    body: FarmCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer)),
):
    farm = Farm(id=str(uuid.uuid4()), **body.dict())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return success(data=farm_to_dict(farm), message="Farm created")


@router.get("/{farm_id}")
def get_farm(farm_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(404, "Farm not found")
    return success(data=farm_to_dict(farm))


@router.get("/{farm_id}/crop-health")
def crop_health(farm_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.crop_cycles import CropCycle
    from app.models.visits import Visit, VisitStatus
    cycles = db.query(CropCycle).filter(CropCycle.farm_id == farm_id).all()
    recent_visits = db.query(Visit).filter(
        Visit.farm_id == farm_id, Visit.status == VisitStatus.completed
    ).order_by(Visit.visited_at.desc()).limit(5).all()
    return success(data={
        "cycles": [{"id": c.id, "name": c.cycle_name, "start": str(c.start_date), "end": str(c.end_date)} for c in cycles],
        "recent_visits": [{"id": v.id, "notes": v.notes, "visited_at": str(v.visited_at)} for v in recent_visits],
    })


@router.get("/{farm_id}/agreements")
def farm_agreements(farm_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.agreements import Agreement
    items = db.query(Agreement).filter(Agreement.farm_id == farm_id).all()
    return success(data={"items": [{"id": a.id, "type": a.type.value, "status": a.status.value, "amount": a.amount} for a in items]})


@router.get("/{farm_id}/work-orders")
def farm_work_orders(farm_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.work_orders import WorkOrder
    items = db.query(WorkOrder).filter(WorkOrder.farm_id == farm_id, WorkOrder.is_deleted == False).all()
    return success(data={"items": [{"id": w.id, "type": w.type.value, "status": w.status.value} for w in items]})
