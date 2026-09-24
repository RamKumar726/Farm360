import json
import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models.finance import ExpenseStatus, LandownerSettlement, ProjectExpense, SettlementStatus
from app.models.agreements import Agreement
from app.models.outsourcing_contracts import OutsourcingContract, OutsourcingContractStatus
from app.models.work_partners import WorkPartner, WorkPartnerStatus
from app.models.harvests import Harvest
from app.models.projects import Project
from app.models.users import User, UserRole

router = APIRouter(prefix="/finance", tags=["project-finance"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class ExpenseCreate(BaseModel):
    project_id: str
    work_order_id: Optional[str] = None
    category: str = Field(min_length=1, max_length=100)
    vendor: Optional[str] = None
    amount: float = Field(gt=0)
    proof_url: str = Field(min_length=1, max_length=1000)


class ExpenseReview(BaseModel):
    approved: bool
    note: Optional[str] = None


class ExpensePaid(BaseModel):
    transaction_reference: str = Field(min_length=1, max_length=200)
    proof_url: str = Field(min_length=1)


class SettlementCreate(BaseModel):
    period_key: str = Field(min_length=1, max_length=100)
    harvest_id: Optional[str] = None


class SettlementPaid(BaseModel):
    transaction_reference: str = Field(min_length=1, max_length=200)
    proof_url: str = Field(min_length=1)


class OutsourcingContractCreate(BaseModel):
    work_order_id: Optional[str] = None
    partner_id: str
    scope: str = Field(min_length=1, max_length=5000)
    terms: Optional[str] = None
    amount: float = Field(ge=0)
    document_url: str = Field(min_length=1, max_length=1000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


def _can_view_project(project: Project, user: User):
    if user.role == UserRole.founder:
        return True
    if user.role == UserRole.customer:
        if project.customer_id == user.id:
            return True
        return any(inv.customer and inv.customer.user_id == user.id for inv in project.investments)
    if user.role in {UserRole.zone_admin, UserRole.employee}:
        return _can_manage_project(project, user)
    if user.role == UserRole.agri_officer:
        return project.assigned_ao_id == user.id
    return False


def _can_manage_project(project: Project, user: User):
    if user.role == UserRole.founder:
        return True
    if user.role == UserRole.agri_officer:
        return project.assigned_ao_id == user.id
    if user.role == UserRole.employee:
        return project.posted_by == user.id or bool(project.lead and user.id in (project.lead.employee_id, project.lead.assigned_employee_id))
    if user.role == UserRole.zone_admin:
        branch_id = (project.lead.branch_id if project.lead and project.lead.branch_id else
                     project.posted_by_user.branch_id if project.posted_by_user else None)
        zone_id = (project.lead.zone_id if project.lead and project.lead.zone_id else
                   project.posted_by_user.zone_id if project.posted_by_user else None)
        if user.branch_id:
            return branch_id == user.branch_id
        if user.zone_id:
            return zone_id == user.zone_id
        return False
    return False


def _sync_project_expenses(project_id: str, db: Session):
    total = db.query(func.coalesce(func.sum(ProjectExpense.amount), 0)).filter(
        ProjectExpense.project_id == project_id,
        ProjectExpense.status.in_([ExpenseStatus.approved, ExpenseStatus.paid]),
    ).scalar()
    project = db.query(Project).filter(Project.id == project_id).with_for_update().first()
    if project:
        project.total_expenses = float(total or 0)
        project.net_profit = (project.total_revenue or 0.0) - project.total_expenses - (project.landowner_settlement or 0.0)
        from app.services.investment_service import refresh_project_expected_returns
        refresh_project_expected_returns(project, db)


def _sync_project_settlement(project_id: str, db: Session):
    total = db.query(func.coalesce(func.sum(LandownerSettlement.amount), 0)).filter(
        LandownerSettlement.project_id == project_id,
        LandownerSettlement.status.in_([SettlementStatus.approved, SettlementStatus.paid]),
    ).scalar()
    project = db.query(Project).filter(Project.id == project_id).with_for_update().first()
    if project:
        project.landowner_settlement = float(total or 0)
        project.net_profit = (project.total_revenue or 0.0) - (project.total_expenses or 0.0) - project.landowner_settlement
        from app.services.investment_service import refresh_project_expected_returns
        refresh_project_expected_returns(project, db)


def _expense_dict(row: ProjectExpense):
    return {"id": row.id, "project_id": row.project_id, "work_order_id": row.work_order_id,
            "category": row.category, "vendor": row.vendor, "amount": row.amount,
            "proof_url": row.proof_url, "status": row.status.value,
            "transaction_reference": row.transaction_reference,
            "created_by": row.created_by, "created_at": str(row.created_at),
            "paid_at": str(row.paid_at) if row.paid_at else None}


def _settlement_dict(row: LandownerSettlement):
    return {"id": row.id, "project_id": row.project_id, "harvest_id": row.harvest_id,
            "period_key": row.period_key, "base_amount": row.base_amount, "amount": row.amount,
            "calculation": json.loads(row.calculation), "status": row.status.value,
            "approved_by": row.approved_by, "proof_url": row.proof_url,
            "transaction_reference": row.transaction_reference,
            "created_at": str(row.created_at), "paid_at": str(row.paid_at) if row.paid_at else None}


def _outsourcing_contract_dict(row: OutsourcingContract):
    return {"id": row.id, "project_id": row.project_id, "work_order_id": row.work_order_id,
            "partner_id": row.partner_id, "scope": row.scope, "terms": row.terms,
            "amount": row.amount, "document_url": row.document_url,
            "start_date": str(row.start_date) if row.start_date else None,
            "end_date": str(row.end_date) if row.end_date else None,
            "status": row.status.value, "created_at": str(row.created_at)}


@router.get("/projects/{project_id}/outsourcing-contracts")
def list_outsourcing_contracts(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or not _can_view_project(project, user):
        raise HTTPException(404, "Project not found")
    rows = db.query(OutsourcingContract).filter(OutsourcingContract.project_id == project_id).order_by(OutsourcingContract.created_at.desc()).all()
    return success([_outsourcing_contract_dict(row) for row in rows])


@router.post("/projects/{project_id}/outsourcing-contracts")
def create_outsourcing_contract(
    project_id: str,
    body: OutsourcingContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or not _can_manage_project(project, user):
        raise HTTPException(404, "Project not found")
    partner = db.query(WorkPartner).filter(WorkPartner.id == body.partner_id, WorkPartner.status == WorkPartnerStatus.active).first()
    if not partner:
        raise HTTPException(404, "Active outsourcing partner not found")
    if body.work_order_id:
        from app.models.work_orders import WorkOrder
        work = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id, WorkOrder.project_id == project.id).first()
        if not work or work.outsourcing_partner_id != partner.id:
            raise HTTPException(400, "Select a project work order already assigned to this outsourcing partner")
    if body.start_date and body.end_date and body.end_date < body.start_date:
        raise HTTPException(400, "Contract end date cannot be before its start date")
    row = OutsourcingContract(
        id=str(uuid.uuid4()), project_id=project.id, work_order_id=body.work_order_id,
        partner_id=partner.id, scope=body.scope.strip(), terms=body.terms,
        amount=body.amount, document_url=body.document_url.strip(),
        start_date=body.start_date, end_date=body.end_date,
        status=OutsourcingContractStatus.active, created_by=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success(_outsourcing_contract_dict(row), "Signed outsourcing contract recorded")


@router.get("/projects/{project_id}/expenses")
def list_project_expenses(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if not _can_view_project(project, user):
        raise HTTPException(404, "Project not found")
    rows = db.query(ProjectExpense).filter(ProjectExpense.project_id == project_id).order_by(ProjectExpense.created_at.desc()).all()
    return success(rows and [_expense_dict(row) for row in rows] or [])


@router.post("/expenses")
def create_expense(body: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(
    UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee
))):
    project = db.query(Project).filter(Project.id == body.project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if project.type.value == "lease" and not body.work_order_id:
        raise HTTPException(400, "Lease expenses must be linked to a project work order")
    if user.role != UserRole.farm_employee and not _can_manage_project(project, user):
        raise HTTPException(404, "Project not found")
    if body.work_order_id:
        from app.models.work_orders import WorkOrder
        work = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id, WorkOrder.project_id == project.id).first()
        if not work:
            raise HTTPException(400, "Expense work order must belong to the selected project")
        if user.role == UserRole.farm_employee and work.farm_employee_id != user.id:
            raise HTTPException(403, "Expense work order is not assigned to you")
    elif user.role == UserRole.farm_employee:
        raise HTTPException(403, "Farm employees must link expenses to their assigned work order")
    if user.role == UserRole.agri_officer and project.assigned_ao_id != user.id:
        raise HTTPException(403, "Project is not assigned to you")
    row = ProjectExpense(id=str(uuid.uuid4()), project_id=project.id, work_order_id=body.work_order_id,
                         category=body.category.strip(), vendor=body.vendor, amount=body.amount,
                         proof_url=body.proof_url, status=ExpenseStatus.submitted, created_by=user.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return success(_expense_dict(row), "Expense submitted for approval")


@router.post("/expenses/{expense_id}/review")
def review_expense(expense_id: str, body: ExpenseReview, db: Session = Depends(get_db), user: User = Depends(require_roles(
    UserRole.founder, UserRole.zone_admin
))):
    row = db.query(ProjectExpense).filter(ProjectExpense.id == expense_id).with_for_update().first()
    if not row:
        raise HTTPException(404, "Expense not found")
    project = db.query(Project).filter(Project.id == row.project_id).first()
    if not project or not _can_manage_project(project, user):
        raise HTTPException(404, "Expense not found")
    if row.status != ExpenseStatus.submitted:
        raise HTTPException(400, "Only submitted expenses can be reviewed")
    row.status = ExpenseStatus.approved if body.approved else ExpenseStatus.rejected
    _sync_project_expenses(row.project_id, db)
    db.commit()
    db.refresh(row)
    return success(_expense_dict(row), "Expense approved" if body.approved else "Expense rejected")


@router.post("/expenses/{expense_id}/mark-paid")
def mark_expense_paid(expense_id: str, body: ExpensePaid, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin))):
    row = db.query(ProjectExpense).filter(ProjectExpense.id == expense_id).with_for_update().first()
    if not row:
        raise HTTPException(404, "Expense not found")
    project = db.query(Project).filter(Project.id == row.project_id).first()
    if not project or not _can_manage_project(project, user):
        raise HTTPException(404, "Expense not found")
    if row.status != ExpenseStatus.approved:
        raise HTTPException(400, "Only approved expenses can be recorded as paid")
    row.status = ExpenseStatus.paid
    row.transaction_reference = body.transaction_reference
    row.proof_url = body.proof_url
    row.paid_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return success(_expense_dict(row), "Expense payment recorded")


@router.get("/projects/{project_id}/settlements")
def list_project_settlements(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if not _can_view_project(project, user):
        raise HTTPException(404, "Project not found")
    rows = db.query(LandownerSettlement).filter(LandownerSettlement.project_id == project_id).order_by(LandownerSettlement.created_at.desc()).all()
    return success([_settlement_dict(row) for row in rows])


@router.post("/projects/{project_id}/settlements")
def create_settlement(project_id: str, body: SettlementCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(
    UserRole.founder, UserRole.zone_admin, UserRole.employee
))):
    project = db.query(Project).filter(Project.id == project_id).with_for_update().first()
    if not project:
        raise HTTPException(404, "Project not found")
    if not _can_manage_project(project, user):
        raise HTTPException(404, "Project not found")
    if project.type.value != "lease":
        raise HTTPException(400, "Landowner settlements are available only for lease projects")
    if db.query(LandownerSettlement).filter(LandownerSettlement.project_id == project.id, LandownerSettlement.period_key == body.period_key).first():
        raise HTTPException(409, "A settlement already exists for this period")
    harvest = None
    if body.harvest_id:
        harvest = db.query(Harvest).filter(Harvest.id == body.harvest_id, Harvest.project_id == project.id).first()
        if not harvest:
            raise HTTPException(404, "Harvest not found for this project")
        if project.commercial_model_type in ("fixed_plus_percentage", "percentage_share") and not harvest.is_revenue_received:
            raise HTTPException(400, "Record the harvest sale payment before calculating its revenue-share settlement")
        if harvest.harvest_date and body.period_key != harvest.harvest_date.strftime("%Y-%m"):
            raise HTTPException(400, "Settlement period must match the selected harvest month")
        revenue = harvest.gross_revenue or 0.0
        expense_base = (harvest.harvesting_cost or 0) + (harvest.transport_cost or 0) + (harvest.other_expenses or 0)
        if harvest.work_order_id:
            linked_expenses = db.query(func.coalesce(func.sum(ProjectExpense.amount), 0)).filter(
                ProjectExpense.project_id == project.id,
                ProjectExpense.work_order_id == harvest.work_order_id,
                ProjectExpense.status.in_([ExpenseStatus.approved, ExpenseStatus.paid]),
            ).scalar()
            expense_base += float(linked_expenses or 0)
    else:
        if project.commercial_model_type in ("fixed_plus_percentage", "percentage_share"):
            raise HTTPException(400, "Select the harvest record for a percentage-based settlement")
        revenue = project.total_revenue or 0.0
        expense_base = project.total_expenses or 0.0
    base_key = project.settlement_base
    if base_key not in ("revenue", "net_realization", "defined_profit") and project.commercial_model_type != "fixed_lease":
        raise HTTPException(400, "The agreement must define a settlement base for percentage payments")
    base = revenue if base_key == "revenue" else max(0.0, revenue - expense_base)
    fixed = float(project.fixed_lease_amount or 0)
    percentage = float(project.revenue_share_percentage or 0)
    model = project.commercial_model_type
    frequency = "annual"
    agreement = db.query(Agreement).filter(Agreement.project_id == project.id).first()
    if agreement and agreement.payment_terms:
        try:
            frequency = json.loads(agreement.payment_terms).get("payment_frequency", "annual")
        except (TypeError, ValueError):
            frequency = "annual"
    periods_per_year = {"monthly": 12, "quarterly": 4, "annual": 1}.get(frequency)
    if periods_per_year is None:
        raise HTTPException(400, "Lease agreement has an unsupported payment frequency")
    try:
        settlement_month = datetime.strptime(body.period_key, "%Y-%m").date()
    except ValueError as exc:
        raise HTTPException(400, "Settlement period must use YYYY-MM format") from exc
    if model in ("fixed_lease", "fixed_plus_percentage"):
        cadence_start = agreement.start_date if agreement and agreement.start_date else (project.start_date or date.today())
        elapsed_months = (settlement_month.year - cadence_start.year) * 12 + settlement_month.month - cadence_start.month
        fixed_due = elapsed_months >= 0 and (frequency == "monthly" or (frequency == "quarterly" and elapsed_months % 3 == 0) or (frequency == "annual" and elapsed_months % 12 == 0))
        if model == "fixed_lease" and not fixed_due:
            raise HTTPException(400, f"Settlement period does not match the agreement’s {frequency} payment schedule")
    else:
        fixed_due = False
    period_fixed = fixed / periods_per_year if fixed_due else 0.0
    if model == "fixed_lease":
        amount = period_fixed
    elif model == "fixed_plus_percentage":
        amount = period_fixed + base * percentage / 100
    elif model == "percentage_share":
        amount = base * percentage / 100
    else:
        raise HTTPException(400, "Lease commercial model is missing or invalid")
    if amount <= 0:
        raise HTTPException(400, "Calculated settlement must be greater than zero")
    calculation = {"model": model, "settlement_base": base_key, "revenue": revenue,
                   "eligible_expenses": expense_base, "base_amount": base,
                   "fixed_lease_amount": fixed, "payment_frequency": frequency,
                   "fixed_period_amount": period_fixed, "percentage": percentage, "amount": round(amount, 2)}
    row = LandownerSettlement(id=str(uuid.uuid4()), project_id=project.id,
                              harvest_id=harvest.id if harvest else None, period_key=body.period_key,
                              base_amount=base, amount=round(amount, 2), calculation=json.dumps(calculation),
                              status=SettlementStatus.pending_approval, created_by=user.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return success(_settlement_dict(row), "Landowner settlement calculated and submitted for approval")


@router.post("/settlements/{settlement_id}/approve")
def approve_settlement(settlement_id: str, approved: bool = Query(True), db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.zone_admin, UserRole.founder))):
    row = db.query(LandownerSettlement).filter(LandownerSettlement.id == settlement_id).with_for_update().first()
    if not row:
        raise HTTPException(404, "Settlement not found")
    project = db.query(Project).filter(Project.id == row.project_id).first()
    if not project or not _can_manage_project(project, user):
        raise HTTPException(404, "Settlement not found")
    if row.status != SettlementStatus.pending_approval:
        raise HTTPException(400, "Settlement is not pending approval")
    row.status = SettlementStatus.approved if approved else SettlementStatus.rejected
    row.approved_by = user.id
    _sync_project_settlement(row.project_id, db)
    db.commit()
    db.refresh(row)
    return success(_settlement_dict(row), "Settlement approved" if approved else "Settlement rejected")


@router.post("/settlements/{settlement_id}/mark-paid")
def mark_settlement_paid(settlement_id: str, body: SettlementPaid, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin))):
    row = db.query(LandownerSettlement).filter(LandownerSettlement.id == settlement_id).with_for_update().first()
    if not row:
        raise HTTPException(404, "Settlement not found")
    project = db.query(Project).filter(Project.id == row.project_id).first()
    if not project or not _can_manage_project(project, user):
        raise HTTPException(404, "Settlement not found")
    if row.status != SettlementStatus.approved:
        raise HTTPException(400, "Only an approved settlement can be recorded as paid")
    row.status = SettlementStatus.paid
    row.transaction_reference = body.transaction_reference
    row.proof_url = body.proof_url
    row.paid_at = datetime.now(timezone.utc)
    _sync_project_settlement(row.project_id, db)
    db.commit()
    db.refresh(row)
    return success(_settlement_dict(row), "Landowner payment recorded")
