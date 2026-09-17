import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.brokers import Broker
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/brokers", tags=["brokers"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class BrokerCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    zone_id: Optional[str] = None
    specializations: Optional[list] = None


class AssignZone(BaseModel):
    zone_id: str


def broker_to_dict(b: Broker):
    return {"id": b.id, "name": b.name, "contact": b.contact,
            "zone_id": b.zone_id, "specializations": b.specializations}


@router.get("")
def list_brokers(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    zone_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Broker)
    if zone_id:
        query = query.filter(Broker.zone_id == zone_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [broker_to_dict(b) for b in items]})


@router.post("")
def create_broker(
    body: BrokerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    broker = Broker(
        id=str(uuid.uuid4()), name=body.name, contact=body.contact,
        zone_id=body.zone_id, specializations=body.specializations,
        assigned_by=current_user.id,
    )
    db.add(broker)
    db.commit()
    db.refresh(broker)
    return success(data=broker_to_dict(broker), message="Broker added")


@router.post("/{broker_id}/assign-zone")
def assign_zone(
    broker_id: str, body: AssignZone,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    broker = db.query(Broker).filter(Broker.id == broker_id).first()
    if not broker:
        raise HTTPException(404, "Broker not found")
    broker.zone_id = body.zone_id
    db.commit()
    return success(data=broker_to_dict(broker), message="Zone assigned to broker")
