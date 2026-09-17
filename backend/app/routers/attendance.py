import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.attendance import Attendance, AttendanceStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/attendance", tags=["attendance"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class AttendanceCreate(BaseModel):
    user_id: str
    date: date
    status: AttendanceStatus
    replacement_user_id: Optional[str] = None
    zone_id: Optional[str] = None
    notes: Optional[str] = None


def att_to_dict(a: Attendance):
    return {
        "id": a.id, "user_id": a.user_id, "date": str(a.date),
        "status": a.status.value, "replacement_user_id": a.replacement_user_id,
        "zone_id": a.zone_id, "notes": a.notes,
    }


@router.get("")
def list_attendance(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Attendance)
    if current_user.role == UserRole.farm_employee:
        query = query.filter(Attendance.user_id == current_user.id)
    elif user_id:
        query = query.filter(Attendance.user_id == user_id)
    total = query.count()
    items = query.order_by(Attendance.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [att_to_dict(a) for a in items]})


@router.post("")
def create_attendance(
    body: AttendanceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    att = Attendance(
        id=str(uuid.uuid4()),
        user_id=body.user_id, date=body.date,
        status=body.status,
        replacement_user_id=body.replacement_user_id,
        zone_id=body.zone_id, notes=body.notes,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return success(data=att_to_dict(att), message="Attendance recorded")


@router.get("/today")
def today_attendance(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    today = date.today()
    items = db.query(Attendance).filter(Attendance.date == today).all()
    return success(data={"date": str(today), "items": [att_to_dict(a) for a in items]})


@router.post("/mark-absent")
def mark_absent(
    user_id: str,
    replacement_user_id: Optional[str] = None,
    zone_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    """Mark an employee absent and optionally assign a replacement — work orders remain unchanged."""
    today = date.today()
    existing = db.query(Attendance).filter(Attendance.user_id == user_id, Attendance.date == today).first()
    if existing:
        existing.status = AttendanceStatus.absent
        existing.replacement_user_id = replacement_user_id
        db.commit()
        return success(data=att_to_dict(existing), message="Attendance updated to absent")
    att = Attendance(
        id=str(uuid.uuid4()),
        user_id=user_id, date=today,
        status=AttendanceStatus.absent,
        replacement_user_id=replacement_user_id,
        zone_id=zone_id,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return success(data=att_to_dict(att), message="Employee marked absent — work continues with replacement")
