import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.branches import Branch
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/branches", tags=["branches"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class BranchCreate(BaseModel):
    name: str
    location: Optional[str] = None
    admin_user_id: Optional[str] = None


def branch_to_dict(b: Branch):
    return {"id": b.id, "name": b.name, "location": b.location,
            "admin_user_id": b.admin_user_id, "created_at": str(b.created_at)}


@router.get("")
def list_branches(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Branch)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Branch.id == current_user.branch_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [branch_to_dict(b) for b in items]})


@router.post("")
def create_branch(
    body: BranchCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder)),
):
    branch = Branch(id=str(uuid.uuid4()), name=body.name,
                    location=body.location, admin_user_id=body.admin_user_id)
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return success(data=branch_to_dict(branch), message="Branch created")


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    admin_user_id: Optional[str] = None


@router.get("/{branch_id}")
def get_branch(branch_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    b = db.query(Branch).filter(Branch.id == branch_id).first()
    if not b:
        raise HTTPException(404, "Branch not found")
    return success(data=branch_to_dict(b))


@router.patch("/{branch_id}")
def update_branch(
    branch_id: str,
    body: BranchUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder)),
):
    b = db.query(Branch).filter(Branch.id == branch_id).first()
    if not b:
        raise HTTPException(404, "Branch not found")
    for field, val in body.dict(exclude_none=True).items():
        setattr(b, field, val)
    db.commit()
    db.refresh(b)
    return success(data=branch_to_dict(b), message="Branch updated")


@router.delete("/{branch_id}")
def delete_branch(
    branch_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder)),
):
    b = db.query(Branch).filter(Branch.id == branch_id).first()
    if not b:
        raise HTTPException(404, "Branch not found")
    db.delete(b)
    db.commit()
    return success(message="Branch deleted")
