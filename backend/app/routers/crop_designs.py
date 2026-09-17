import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.crop_designs import CropDesign, ApprovalStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.crop_cycle_service import generate_cycles_from_design

router = APIRouter(prefix="/crop-designs", tags=["crop-designs"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class CropDesignCreate(BaseModel):
    farm_id: str
    best_practices: Optional[str] = None
    land_suitability: Optional[str] = None
    timing: Optional[str] = None
    crop_time: Optional[str] = None
    estimated_yearly_cost: Optional[float] = None
    intercrop_design: Optional[str] = None
    recommended_machines: Optional[str] = None
    research_notes: Optional[str] = None


def cd_to_dict(c: CropDesign):
    return {
        "id": c.id, "farm_id": c.farm_id, "agri_officer_id": c.agri_officer_id,
        "best_practices": c.best_practices, "land_suitability": c.land_suitability,
        "timing": c.timing, "crop_time": c.crop_time,
        "estimated_yearly_cost": c.estimated_yearly_cost,
        "intercrop_design": c.intercrop_design,
        "recommended_machines": c.recommended_machines,
        "research_notes": c.research_notes,
        "approval_status": c.approval_status.value,
        "created_at": str(c.created_at),
    }


@router.get("")
def list_crop_designs(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(CropDesign)
    if current_user.role == UserRole.agri_officer:
        query = query.filter(CropDesign.agri_officer_id == current_user.id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [cd_to_dict(c) for c in items]})


@router.post("")
def create_crop_design(
    body: CropDesignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer, UserRole.founder)),
):
    cd = CropDesign(
        id=str(uuid.uuid4()),
        farm_id=body.farm_id,
        agri_officer_id=current_user.id,
        best_practices=body.best_practices,
        land_suitability=body.land_suitability,
        timing=body.timing, crop_time=body.crop_time,
        estimated_yearly_cost=body.estimated_yearly_cost,
        intercrop_design=body.intercrop_design,
        recommended_machines=body.recommended_machines,
        research_notes=body.research_notes,
    )
    db.add(cd)
    db.commit()
    db.refresh(cd)
    return success(data=cd_to_dict(cd), message="Crop design created")


@router.get("/{cd_id}")
def get_crop_design(cd_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cd = db.query(CropDesign).filter(CropDesign.id == cd_id).first()
    if not cd:
        raise HTTPException(404, "Crop design not found")
    return success(data=cd_to_dict(cd))


@router.post("/{cd_id}/approve")
def approve_crop_design(
    cd_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    """Approve and auto-generate crop/work/visit cycles."""
    cd = db.query(CropDesign).filter(CropDesign.id == cd_id).first()
    if not cd:
        raise HTTPException(404, "Crop design not found")
    cd.approval_status = ApprovalStatus.approved
    cd.approved_by = current_user.id
    db.commit()
    # Auto-generate all cycles
    cycles = generate_cycles_from_design(cd, db)
    return success(
        data={"crop_design": cd_to_dict(cd), "generated_cycles": len(cycles)},
        message=f"Crop design approved and {len(cycles)} cycles auto-generated"
    )


@router.get("/{cd_id}/generate-cycles")
def get_generated_cycles(cd_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.crop_cycles import CropCycle
    cycles = db.query(CropCycle).filter(CropCycle.crop_design_id == cd_id).all()
    return success(data={"items": [{"id": c.id, "name": c.cycle_name, "start": str(c.start_date), "end": str(c.end_date)} for c in cycles]})
