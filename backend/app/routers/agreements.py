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
from app.auth.scope import scope_projects

router = APIRouter(prefix="/agreements", tags=["agreements"])


def _scope_agreements(query, user: User, db: Session):
    if user.role == UserRole.founder:
        return query
    if user.role == UserRole.customer:
        from app.models.customers import Customer
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        return query.filter(Agreement.customer_id == (customer.id if customer else ""))
    if user.role == UserRole.zone_admin:
        from app.models.customers import Customer
        return query.join(Customer, Agreement.customer_id == Customer.id).filter(
            (Customer.branch_id == user.branch_id) if user.branch_id else (Customer.zone_id == user.zone_id)
        )
    if user.role in {UserRole.employee, UserRole.agri_officer, UserRole.farm_employee}:
        from app.models.projects import Project
        project_ids = scope_projects(db.query(Project.id), user, db)
        return query.filter(Agreement.project_id.in_(project_ids))
    return query.filter(False)


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
        "lead_id": a.lead_id, "project_id": a.project_id,
        "type": a.type.value, "start_date": str(a.start_date) if a.start_date else None,
        "end_date": str(a.end_date) if a.end_date else None,
        "amount": a.amount, "payment_terms": a.payment_terms, "status": a.status.value,
        "document_url": a.document_url,
    }


@router.get("")
def list_agreements(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.customer}:
        raise HTTPException(403, "You cannot access agreements")
    query = _scope_agreements(db.query(Agreement), current_user, db)
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
def get_agreement(ag_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = _scope_agreements(db.query(Agreement).filter(Agreement.id == ag_id), current_user, db).first()
    if not ag:
        raise HTTPException(404, "Agreement not found")
    if current_user.role not in {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.customer}:
        raise HTTPException(403, "You cannot access agreements")
    return success(data=ag_to_dict(ag))
