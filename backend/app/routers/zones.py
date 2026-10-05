import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.zones import Zone
from app.models.branches import Branch
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/zones", tags=["zones"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class ZoneCreate(BaseModel):
    name: str
    branch_id: str
    responsible_employee_id: Optional[str] = None


class AssignEmployee(BaseModel):
    employee_id: str


def _validate_zone_assignment(db: Session, branch_id: str, responsible_employee_id: Optional[str] = None):
    if not db.query(Branch.id).filter(Branch.id == branch_id).first():
        raise HTTPException(400, "Branch not found")
    if responsible_employee_id:
        employee = db.query(User).filter(
            User.id == responsible_employee_id, User.is_deleted == False
        ).first()
        if not employee or employee.branch_id != branch_id:
            raise HTTPException(400, "Responsible staff member must be active and belong to the zone's branch")


def zone_to_dict(z: Zone):
    return {"id": z.id, "name": z.name, "branch_id": z.branch_id,
            "responsible_employee_id": z.responsible_employee_id}


@router.get("")
def list_zones(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    branch_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Zone)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Zone.branch_id == current_user.branch_id)
    elif branch_id:
        query = query.filter(Zone.branch_id == branch_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [zone_to_dict(z) for z in items]})


@router.post("")
def create_zone(
    body: ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    branch_id = current_user.branch_id if current_user.role == UserRole.zone_admin else body.branch_id
    if not branch_id:
        raise HTTPException(400, "Branch is required")
    if current_user.role == UserRole.zone_admin and body.branch_id != branch_id:
        raise HTTPException(403, "Zone Admins can create zones only in their own branch")
    _validate_zone_assignment(db, branch_id, body.responsible_employee_id)
    zone = Zone(id=str(uuid.uuid4()), name=body.name,
                branch_id=branch_id, responsible_employee_id=body.responsible_employee_id)
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return success(data=zone_to_dict(zone), message="Zone created")


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    branch_id: Optional[str] = None
    responsible_employee_id: Optional[str] = None


@router.patch("/{zone_id}")
def update_zone(
    zone_id: str,
    body: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    if current_user.role == UserRole.zone_admin and zone.branch_id != current_user.branch_id:
        raise HTTPException(404, "Zone not found")
    changes = body.model_dump(exclude_unset=True)
    target_branch = changes.get("branch_id", zone.branch_id)
    if current_user.role == UserRole.zone_admin and target_branch != current_user.branch_id:
        raise HTTPException(403, "Zone Admins cannot move zones outside their branch")
    target_responsible = changes.get("responsible_employee_id", zone.responsible_employee_id)
    _validate_zone_assignment(db, target_branch, target_responsible)
    for field, val in changes.items():
        setattr(zone, field, val)
    db.commit()
    db.refresh(zone)
    return success(data=zone_to_dict(zone), message="Zone updated")


@router.post("/{zone_id}/assign-employee")
def assign_zone_employee(
    zone_id: str,
    body: AssignEmployee,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone or (current_user.role == UserRole.zone_admin and zone.branch_id != current_user.branch_id):
        raise HTTPException(404, "Zone not found")
    _validate_zone_assignment(db, zone.branch_id, body.employee_id)
    zone.responsible_employee_id = body.employee_id
    db.commit()
    db.refresh(zone)
    return success(data=zone_to_dict(zone), message="Responsible staff assigned")


@router.delete("/{zone_id}")
def delete_zone(
    zone_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder)),
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    db.delete(zone)
    db.commit()
    return success(message="Zone deleted")
