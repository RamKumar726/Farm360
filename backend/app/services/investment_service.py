"""
Investment Revenue Share Service
Rule: revenue_share_percentage = (invested_amount / total_project_amount) * 100
"""
from sqlalchemy.orm import Session
from app.models.investments import Investment
from app.models.projects import Project


def calculate_revenue_share(investment: Investment, db: Session) -> float:
    """Calculate and update the investor's revenue share percentage."""
    project = db.query(Project).filter(Project.id == investment.project_id).first()
    if not project or project.total_amount == 0:
        return 0.0
    share = (investment.amount / project.total_amount) * 100
    investment.revenue_share_percentage = round(share, 4)
    return investment.revenue_share_percentage


def calculate_expected_return(investment: Investment, project: Project) -> float:
    """Estimate return based on projected total revenue and investor share."""
    if not project.total_revenue or investment.revenue_share_percentage is None:
        return 0.0
    return round((investment.revenue_share_percentage / 100) * project.total_revenue, 2)


def settle_investment(investment: Investment, actual_return: float, db: Session) -> Investment:
    """Mark investment as settled with actual return credited."""
    from app.models.investments import InvestmentStatus
    from datetime import date
    investment.actual_return = actual_return
    investment.status = InvestmentStatus.settled
    investment.settlement_date = date.today()
    db.commit()
    db.refresh(investment)
    return investment
