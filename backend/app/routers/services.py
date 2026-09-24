import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.services import Service
from app.models.users import User, UserRole

router = APIRouter(prefix="/services", tags=["services"])


class ServiceInput(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=2)
    image_url: Optional[str] = None
    subtitle: Optional[str] = None
    features: list = Field(default_factory=list)
    steps: list = Field(default_factory=list)
    is_featured: bool = False
    is_active: bool = True
    sort_order: int = 0


def service_dict(row: Service):
    return {
        "id": row.id, "title": row.title, "category": row.category,
        "desc": row.description, "description": row.description,
        "image": row.image_url, "image_url": row.image_url,
        "subtitle": row.subtitle, "features": row.features or [], "steps": row.steps or [],
        "is_featured": row.is_featured, "is_active": row.is_active, "sort_order": row.sort_order,
    }


@router.get("")
def list_services(category: Optional[str] = None, featured: Optional[bool] = None,
                  db: Session = Depends(get_db)):
    query = db.query(Service).filter(Service.is_active.is_(True))
    if category:
        query = query.filter(Service.category == category)
    if featured is not None:
        query = query.filter(Service.is_featured.is_(featured))
    rows = query.order_by(Service.sort_order, Service.title).all()
    return {"success": True, "data": [service_dict(row) for row in rows]}


@router.post("")
def create_service(payload: ServiceInput, db: Session = Depends(get_db),
                   _: User = Depends(require_roles(UserRole.founder))):
    if db.query(Service).filter(Service.title == payload.title).first():
        raise HTTPException(status_code=409, detail="A service with this title already exists")
    row = Service(id=str(uuid.uuid4()), **payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"success": True, "data": service_dict(row)}


@router.patch("/{service_id}")
def update_service(service_id: str, payload: ServiceInput, db: Session = Depends(get_db),
                   _: User = Depends(require_roles(UserRole.founder))):
    row = db.query(Service).filter(Service.id == service_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Service not found")
    duplicate = db.query(Service).filter(Service.title == payload.title, Service.id != service_id).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="A service with this title already exists")
    for key, value in payload.dict().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return {"success": True, "data": service_dict(row)}
