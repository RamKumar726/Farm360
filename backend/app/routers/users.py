import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from app.database import get_db
from app.models.users import User, UserRole
from app.models.branches import Branch
from app.models.zones import Zone
from app.auth.dependencies import get_current_user, require_roles
from app.auth.jwt import hash_password
from app.services.audit_service import record_audit

router = APIRouter(prefix="/users", tags=["users"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    phone: Optional[str] = None
    role: UserRole = UserRole.customer
    branch_id: Optional[str] = None
    zone_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_available: Optional[bool] = None
    branch_id: Optional[str] = None
    zone_id: Optional[str] = None


ZONE_ADMIN_MANAGED_ROLES = {
    UserRole.employee, UserRole.agri_officer, UserRole.farm_employee, UserRole.work_partner,
}


def _validate_organization(db: Session, branch_id: Optional[str], zone_id: Optional[str]):
    branch = None
    zone = None
    if branch_id:
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            raise HTTPException(status_code=400, detail="Selected branch does not exist")
    if zone_id:
        zone = db.query(Zone).filter(Zone.id == zone_id).first()
        if not zone:
            raise HTTPException(status_code=400, detail="Selected zone does not exist")
        if branch_id and zone.branch_id != branch_id:
            raise HTTPException(status_code=400, detail="Selected zone does not belong to the selected branch")
        branch = branch or zone.branch
    return branch, zone


def _authorize_staff_change(current_user: User, target: Optional[User], role: UserRole, branch_id: Optional[str]):
    if current_user.role == UserRole.founder:
        return
    if current_user.role != UserRole.zone_admin:
        raise HTTPException(status_code=403, detail="Staff administration is restricted")
    if role not in ZONE_ADMIN_MANAGED_ROLES:
        raise HTTPException(status_code=403, detail="Zone Admins cannot grant or manage this role")
    if not current_user.branch_id or branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Zone Admins can manage only their own branch")
    if target and target.branch_id != current_user.branch_id:
        raise HTTPException(status_code=404, detail="User not found")


def user_to_dict(u: User):
    return {
        "id": u.id, "name": u.name, "email": u.email,
        "phone": u.phone, "role": u.role.value,
        "branch_id": u.branch_id, "zone_id": u.zone_id,
        "is_available": u.is_available, "created_at": str(u.created_at),
    }


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(User).filter(User.is_deleted == False)
    # Scope by role
    if current_user.role == UserRole.zone_admin:
        query = query.filter(
            User.branch_id == current_user.branch_id,
            User.role.in_(ZONE_ADMIN_MANAGED_ROLES),
        )
    elif current_user.role == UserRole.employee:
        # Employees need to choose a same-branch Agriculture Officer when
        # qualifying a lease. Seeded/officer accounts may have a branch but no
        # zone, so a zone-only list hides valid assignees from the UI.
        same_zone = User.zone_id == current_user.zone_id if current_user.zone_id else False
        same_branch_officers = and_(
            User.role == UserRole.agri_officer,
            User.branch_id == current_user.branch_id,
        ) if current_user.branch_id else False
        query = query.filter(or_(same_zone, same_branch_officers))
    if role:
        query = query.filter(User.role == role)
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "page": page, "items": [user_to_dict(u) for u in users]})


@router.post("")
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    branch_id = body.branch_id
    zone_id = body.zone_id
    _, zone = _validate_organization(db, branch_id, zone_id)
    if zone and not branch_id:
        branch_id = zone.branch_id
    if current_user.role == UserRole.zone_admin:
        branch_id = current_user.branch_id
        if zone and zone.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="Selected zone is outside your branch")
    _authorize_staff_change(current_user, None, body.role, branch_id)
    if body.role in {UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee} and not branch_id:
        raise HTTPException(status_code=400, detail="A branch is required for this staff role")
    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
        role=body.role,
        branch_id=branch_id,
        zone_id=zone_id,
    )
    db.add(user)
    db.flush()
    if body.role == UserRole.customer:
        from app.models.customers import Customer
        db.add(Customer(id=str(uuid.uuid4()), user_id=user.id, branch_id=branch_id, zone_id=zone_id))
    record_audit(db, action="user.created", entity_type="user", entity_id=user.id,
                 actor_user_id=current_user.id, changes={"role": body.role.value, "branch_id": branch_id, "zone_id": zone_id})
    db.commit()
    db.refresh(user)
    return success(data=user_to_dict(user), message="User created")


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role == UserRole.zone_admin and user.branch_id != current_user.branch_id:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role not in {UserRole.founder, UserRole.zone_admin} and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return success(data=user_to_dict(user))


@router.patch("/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    changes = body.model_dump(exclude_unset=True)
    if current_user.role not in [UserRole.founder, UserRole.zone_admin] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user.role not in [UserRole.founder, UserRole.zone_admin]:
        protected = {"role", "branch_id", "zone_id"}
        if protected.intersection(changes):
            raise HTTPException(status_code=403, detail="You cannot change your own role or organization assignment")
    requested_role = body.role or user.role
    requested_branch = body.branch_id if "branch_id" in changes else user.branch_id
    requested_zone = body.zone_id if "zone_id" in changes else user.zone_id
    _, zone = _validate_organization(db, requested_branch, requested_zone)
    if zone and not requested_branch:
        requested_branch = zone.branch_id
        changes["branch_id"] = requested_branch
    if current_user.role in {UserRole.founder, UserRole.zone_admin}:
        _authorize_staff_change(current_user, user, requested_role, requested_branch)
    if requested_role in {UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee} and not requested_branch:
        raise HTTPException(status_code=400, detail="A branch is required for this staff role")
    for field, val in changes.items():
        setattr(user, field, val)
    record_audit(db, action="user.updated", entity_type="user", entity_id=user.id,
                 actor_user_id=current_user.id, changes={k: (v.value if isinstance(v, UserRole) else v) for k, v in changes.items()})
    db.commit()
    db.refresh(user)
    return success(data=user_to_dict(user), message="User updated")


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    _authorize_staff_change(current_user, user, user.role, user.branch_id)
    user.is_deleted = True
    user.is_available = False
    record_audit(db, action="user.deleted", entity_type="user", entity_id=user.id,
                 actor_user_id=current_user.id, changes={"soft_delete": True})
    db.commit()
    return success(message="User deleted (soft)")
