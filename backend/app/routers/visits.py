import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.visits import Visit, VisitType, VisitStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/visits", tags=["visits"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class VisitCreate(BaseModel):
    work_order_id: Optional[str] = None
    farm_id: Optional[str] = None
    type: VisitType
    notes: Optional[str] = None


class ProofSubmit(BaseModel):
    gps_lat: float
    gps_lng: float
    proof_photos: Optional[List[str]] = None   # Cloudinary URLs
    proof_video_url: Optional[str] = None
    notes: Optional[str] = None


def visit_to_dict(v: Visit):
    return {
        "id": v.id, "work_order_id": v.work_order_id, "farm_id": v.farm_id,
        "farm_employee_id": v.farm_employee_id, "type": v.type.value,
        "gps_lat": v.gps_lat, "gps_lng": v.gps_lng,
        "proof_photos": v.proof_photos, "proof_video_url": v.proof_video_url,
        "status": v.status.value, "notes": v.notes,
        "visited_at": str(v.visited_at) if v.visited_at else None,
    }


@router.get("")
def list_visits(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    status: Optional[VisitStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Visit)
    if current_user.role == UserRole.farm_employee:
        query = query.filter(Visit.farm_employee_id == current_user.id)
    if status:
        query = query.filter(Visit.status == status)
    total = query.count()
    items = query.order_by(Visit.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [visit_to_dict(v) for v in items]})


@router.post("")
def create_visit(
    body: VisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = Visit(
        id=str(uuid.uuid4()),
        work_order_id=body.work_order_id,
        farm_id=body.farm_id,
        farm_employee_id=current_user.id,
        type=body.type,
        status=VisitStatus.pending,
        notes=body.notes,
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return success(data=visit_to_dict(visit), message="Visit created")


@router.get("/pending")
def pending_visits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Visit).filter(Visit.status == VisitStatus.pending)
    if current_user.role == UserRole.farm_employee:
        q = q.filter(Visit.farm_employee_id == current_user.id)
    return success(data={"items": [visit_to_dict(v) for v in q.all()]})


@router.get("/failed")
def failed_visits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Visit).filter(Visit.status == VisitStatus.failed)
    if current_user.role == UserRole.farm_employee:
        q = q.filter(Visit.farm_employee_id == current_user.id)
    return success(data={"items": [visit_to_dict(v) for v in q.all()]})


@router.get("/{visit_id}")
def get_visit(visit_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(404, "Visit not found")
    return success(data=visit_to_dict(visit))


@router.post("/{visit_id}/submit-proof")
def submit_proof(
    visit_id: str,
    body: ProofSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.farm_employee, UserRole.employee, UserRole.agri_officer)),
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(404, "Visit not found")
    if not body.proof_photos and not body.proof_video_url:
        raise HTTPException(400, "At least one photo or video proof is required")
    visit.gps_lat = body.gps_lat
    visit.gps_lng = body.gps_lng
    visit.proof_photos = body.proof_photos
    visit.proof_video_url = body.proof_video_url
    visit.notes = body.notes or visit.notes
    visit.status = VisitStatus.completed
    visit.visited_at = datetime.utcnow()
    db.commit()
    db.refresh(visit)
    return success(data=visit_to_dict(visit), message="Proof submitted successfully")
