import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.auth.jwt import hash_password

router = APIRouter(prefix="/users", tags=["users"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: UserRole = UserRole.customer
    branch_id: Optional[str] = None
    zone_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_available: Optional[bool] = None
    branch_id: Optional[str] = None
    zone_id: Optional[str] = None


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
        query = query.filter(User.branch_id == current_user.branch_id)
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
    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
        role=body.role,
        branch_id=body.branch_id,
        zone_id=body.zone_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return success(data=user_to_dict(user), message="User created")


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
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
    # Only founder/zone_admin or the user themselves can update
    if current_user.role not in [UserRole.founder, UserRole.zone_admin] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    for field, val in body.dict(exclude_none=True).items():
        setattr(user, field, val)
    db.commit()
    db.refresh(user)
    return success(data=user_to_dict(user), message="User updated")


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_deleted = True
    db.commit()
    return success(message="User deleted (soft)")
