import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.investments import Investment, InvestmentType, InvestmentStatus
from app.models.projects import Project
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.investment_service import calculate_revenue_share, calculate_expected_return, settle_investment
from app.services.notification_service import notify_investment_posted, notify_revenue_credited

router = APIRouter(prefix="/investments", tags=["investments"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class InvestmentCreate(BaseModel):
    project_id: str
    customer_id: str
    type: InvestmentType
    amount: float
    bond_period: Optional[int] = None  # months


def inv_to_dict(i: Investment):
    return {
        "id": i.id, "project_id": i.project_id, "customer_id": i.customer_id,
        "type": i.type.value, "amount": i.amount, "bond_period": i.bond_period,
        "status": i.status.value,
        "revenue_share_percentage": i.revenue_share_percentage,
        "expected_return": i.expected_return, "actual_return": i.actual_return,
        "settlement_date": str(i.settlement_date) if i.settlement_date else None,
    }


@router.get("")
def list_investments(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Investment)
    if current_user.role == UserRole.customer:
        from app.models.customers import Customer
        c = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if c:
            query = query.filter(Investment.customer_id == c.id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [inv_to_dict(i) for i in items]})


@router.post("")
def create_investment(
    body: InvestmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == body.project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if project.funded_amount + body.amount > project.total_amount:
        raise HTTPException(400, f"Investment exceeds project capacity. Available: ₹{project.total_amount - project.funded_amount:,.2f}")

    inv = Investment(
        id=str(uuid.uuid4()),
        project_id=body.project_id,
        customer_id=body.customer_id,
        type=body.type,
        amount=body.amount,
        bond_period=body.bond_period,
        status=InvestmentStatus.active,
    )
    db.add(inv)
    project.funded_amount += body.amount
    db.commit()
    db.refresh(inv)
    # Calculate revenue share
    calculate_revenue_share(inv, db)
    inv.expected_return = calculate_expected_return(inv, project)
    db.commit()
    return success(data=inv_to_dict(inv), message="Investment created successfully")


@router.get("/{inv_id}")
def get_investment(inv_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    inv = db.query(Investment).filter(Investment.id == inv_id).first()
    if not inv:
        raise HTTPException(404, "Investment not found")
    return success(data=inv_to_dict(inv))


@router.get("/{inv_id}/revenue-share")
def get_revenue_share(inv_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    inv = db.query(Investment).filter(Investment.id == inv_id).first()
    if not inv:
        raise HTTPException(404, "Investment not found")
    project = db.query(Project).filter(Project.id == inv.project_id).first()
    share = calculate_revenue_share(inv, db)
    expected = calculate_expected_return(inv, project) if project else 0
    return success(data={
        "investment_id": inv.id,
        "amount_invested": inv.amount,
        "total_project_amount": project.total_amount if project else None,
        "revenue_share_percentage": share,
        "expected_return": expected,
        "actual_return": inv.actual_return,
        "bond_period_months": inv.bond_period,
        "status": inv.status.value,
    })
