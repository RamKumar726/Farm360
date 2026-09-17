import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.agreements import Agreement, AgreementType, AgreementStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/agreements", tags=["agreements"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class AgreementCreate(BaseModel):
    customer_id: str
    farm_id: Optional[str] = None
    type: AgreementType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    payment_terms: Optional[str] = None
    amount: Optional[float] = None
    document_url: Optional[str] = None


def ag_to_dict(a: Agreement):
    return {
        "id": a.id, "customer_id": a.customer_id, "farm_id": a.farm_id,
        "type": a.type.value, "start_date": str(a.start_date) if a.start_date else None,
        "end_date": str(a.end_date) if a.end_date else None,
        "amount": a.amount, "status": a.status.value,
        "document_url": a.document_url,
    }


@router.get("")
def list_agreements(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Agreement)
    if current_user.role == UserRole.customer:
        from app.models.customers import Customer
        c = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if c:
            query = query.filter(Agreement.customer_id == c.id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [ag_to_dict(a) for a in items]})


@router.post("")
def create_agreement(
    body: AgreementCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    ag = Agreement(id=str(uuid.uuid4()), **body.dict())
    db.add(ag)
    db.commit()
    db.refresh(ag)
    return success(data=ag_to_dict(ag), message="Agreement created")


@router.get("/{ag_id}")
def get_agreement(ag_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ag = db.query(Agreement).filter(Agreement.id == ag_id).first()
    if not ag:
        raise HTTPException(404, "Agreement not found")
    return success(data=ag_to_dict(ag))
