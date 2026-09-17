from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.users import User, UserRole
from app.models.leads import Lead, LeadStatus
from app.models.visits import Visit
from app.models.investments import Investment
from app.models.work_orders import WorkOrder
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/analytics", tags=["analytics"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


def _scope_leads(query, current_user: User, db):
    if current_user.role == UserRole.zone_admin:
        return query.filter(Lead.branch_id == current_user.branch_id)
    return query


@router.get("/leads")
def leads_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    base = db.query(Lead)
    base = _scope_leads(base, current_user, db)
    total = base.count()
    won = base.filter(Lead.status == LeadStatus.won).count()
    lost = base.filter(Lead.status == LeadStatus.lost).count()
    pending = base.filter(Lead.status == LeadStatus.new).count()
    conversion_rate = round((won / total * 100) if total > 0 else 0, 1)
    return success(data={
        "total_leads": total, "won": won, "lost": lost,
        "pending": pending, "conversion_rate_pct": conversion_rate,
    })


@router.get("/revenue")
def revenue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    from app.models.agreements import Agreement
    from app.models.projects import Project
    total_agreements = db.query(func.sum(Agreement.amount)).scalar() or 0
    total_investment = db.query(func.sum(Investment.amount)).scalar() or 0
    total_project_revenue = db.query(func.sum(Project.total_revenue)).scalar() or 0
    return success(data={
        "total_agreement_revenue": total_agreements,
        "total_investment_amount": total_investment,
        "total_project_revenue": total_project_revenue,
        "grand_total": total_agreements + total_investment + total_project_revenue,
    })


@router.get("/visits")
def visits_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    from app.models.visits import VisitStatus
    total = db.query(Visit).count()
    completed = db.query(Visit).filter(Visit.status == VisitStatus.completed).count()
    failed = db.query(Visit).filter(Visit.status == VisitStatus.failed).count()
    pending = db.query(Visit).filter(Visit.status == VisitStatus.pending).count()
    return success(data={"total": total, "completed": completed, "failed": failed, "pending": pending})


@router.get("/employees")
def employee_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    farm_employees = db.query(User).filter(User.role == UserRole.farm_employee, User.is_deleted == False).count()
    available = db.query(User).filter(User.role == UserRole.farm_employee, User.is_available == True).count()
    agri_officers = db.query(User).filter(User.role == UserRole.agri_officer, User.is_deleted == False).count()
    return success(data={
        "total_farm_employees": farm_employees, "available": available,
        "total_agri_officers": agri_officers,
    })


@router.get("/investments")
def investment_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    total_invested = db.query(func.sum(Investment.amount)).scalar() or 0
    total_settled = db.query(func.sum(Investment.actual_return)).scalar() or 0
    from app.models.investments import InvestmentStatus
    active_count = db.query(Investment).filter(Investment.status == InvestmentStatus.active).count()
    settled_count = db.query(Investment).filter(Investment.status == InvestmentStatus.settled).count()
    return success(data={
        "total_invested": total_invested, "total_settled": total_settled,
        "active_investments": active_count, "settled_investments": settled_count,
    })
