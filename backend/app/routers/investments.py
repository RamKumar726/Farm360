import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from sqlalchemy import and_, or_
from app.database import get_db
from app.models.investments import Investment, InvestmentType, InvestmentStatus, InvestmentVerificationStage
from app.models.projects import Project, ProjectStatus
from app.models.customers import Customer
from app.models.leads import Lead, LeadType, LeadSource, LeadStatus
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services.investment_service import calculate_revenue_share, calculate_expected_return, settle_investment
from app.services.notification_service import notify_investment_posted, notify_revenue_credited, notify_new_lead

router = APIRouter(prefix="/investments", tags=["investments"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class InvestmentCreate(BaseModel):
    project_id: str
    customer_id: str
    type: InvestmentType
    amount: float
    bond_period: Optional[int] = None  # months


class ExpressInterestCreate(BaseModel):
    project_id: str
    proposed_amount: float
    questions: Optional[str] = None
    acknowledgement_accepted: bool = True


class PipelineStageUpdate(BaseModel):
    verification_stage: InvestmentVerificationStage
    agreement_url: Optional[str] = None


class InvestmentPayout(BaseModel):
    transaction_reference: str = Field(min_length=1, max_length=200)
    proof_url: str = Field(min_length=1, max_length=1000)


@router.post("/{inv_id}/approve-interest")
def approve_investment_interest(inv_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    inv = db.query(Investment).filter(Investment.id == inv_id).first()
    if current_user.role != UserRole.customer or not customer or not inv or inv.customer_id != customer.id:
        raise HTTPException(404, "Investment interest not found")
    if inv.verification_stage != InvestmentVerificationStage.employee_contacted:
        raise HTTPException(400, "The employee must contact you before you can approve")
    inv.verification_stage = InvestmentVerificationStage.customer_approved
    db.commit()
    db.refresh(inv)
    return success(data=inv_to_dict(inv), message="Investment interest approved")


def inv_to_dict(i: Investment):
    return {
        "id": i.id, "project_id": i.project_id, "customer_id": i.customer_id,
        "type": i.type.value if hasattr(i.type, 'value') else i.type,
        "amount": i.amount, "proposed_amount": i.proposed_amount,
        "minimum_amount": i.minimum_amount_snapshot,
        "questions": i.questions,
        "acknowledgement_accepted": i.acknowledgement_accepted,
        "bond_period": i.bond_period,
        "agreement_url": i.agreement_url,
        "status": i.status.value if hasattr(i.status, 'value') else i.status,
        "verification_stage": i.verification_stage.value if hasattr(i.verification_stage, 'value') else i.verification_stage,
        "revenue_share_percentage": i.revenue_share_percentage,
        "expected_return": i.expected_return, "actual_return": i.actual_return,
        "settlement_date": str(i.settlement_date) if i.settlement_date else None,
        "payout_reference": i.payout_reference,
        "payout_proof_url": i.payout_proof_url,
        "created_at": str(i.created_at),
    }


def _authorize_investment(inv: Investment, user: User, db: Session) -> None:
    if user.role == UserRole.founder:
        return
    if user.role == UserRole.customer:
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        if customer and inv.customer_id == customer.id:
            return
    elif user.role in {UserRole.employee, UserRole.zone_admin}:
        lead = db.query(Lead).filter(Lead.id == inv.lead_id).first() if inv.lead_id else None
        if lead and user.role == UserRole.employee and user.id in (lead.employee_id, lead.assigned_employee_id):
            return
        if lead and user.role == UserRole.zone_admin and (
            (lead.branch_id and lead.branch_id == user.branch_id)
            or (not lead.branch_id and lead.zone_id and lead.zone_id == user.zone_id)
        ):
            return
    raise HTTPException(404, "Investment not found")


@router.get("")
def list_investments(
    page: int = Query(1, ge=1), page_size: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.customer, UserRole.employee, UserRole.zone_admin, UserRole.founder}:
        raise HTTPException(403, "You cannot access investment records")
    query = db.query(Investment)
    if current_user.role == UserRole.customer:
        c = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not c:
            return success(data={"total": 0, "items": []})
        query = query.filter(Investment.customer_id == c.id)
    elif current_user.role == UserRole.employee:
        query = query.join(Lead, Lead.id == Investment.lead_id).filter(
            (Lead.employee_id == current_user.id) | (Lead.assigned_employee_id == current_user.id)
        )
    elif current_user.role == UserRole.zone_admin:
        query = query.join(Lead, Lead.id == Investment.lead_id).filter(or_(
            and_(Lead.branch_id.isnot(None), Lead.branch_id == current_user.branch_id) if current_user.branch_id else False,
            and_(Lead.branch_id.is_(None), Lead.zone_id == current_user.zone_id) if current_user.zone_id else and_(Lead.branch_id.is_(None), Lead.zone_id.is_(None)),
        ))
    total = query.count()
    items = query.order_by(Investment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [inv_to_dict(i) for i in items]})


@router.post("/express-interest")
def express_interest(
    body: ExpressInterestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == body.project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if current_user.role != UserRole.customer or project.approval_status.value != "approved" or project.status.value not in ("open", "funded"):
        raise HTTPException(400, "Investment interest is available only for approved investment listings")

    available = project.total_amount - (project.funded_amount or 0.0)
    if available <= 0:
        raise HTTPException(400, "Project is fully funded")

    if body.proposed_amount < (project.minimum_investment or 150000):
        raise HTTPException(400, f"Minimum participation is ₹{project.minimum_investment or 150000:,.0f}")

    if body.proposed_amount > available:
        raise HTTPException(400, f"Proposed participation exceeds available allocation (Max allowed: ₹{available:,.2f})")
    if not body.acknowledgement_accepted:
        raise HTTPException(400, "Investment acknowledgement must be accepted")

    # Resolve or create Customer record for user
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        customer = Customer(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    inv = Investment(
        id=str(uuid.uuid4()),
        project_id=body.project_id,
        customer_id=customer.id,
        type=InvestmentType.project,
        amount=body.proposed_amount,
        proposed_amount=body.proposed_amount,
        questions=body.questions,
        acknowledgement_accepted=body.acknowledgement_accepted,
        minimum_amount_snapshot=project.minimum_investment,
        status=InvestmentStatus.pending,
        verification_stage=InvestmentVerificationStage.showed_interest,
    )

    # Create Investment Interest Lead for tracking pipeline
    lead = Lead(
        id=str(uuid.uuid4()),
        type=LeadType.investment_interest,
        source=LeadSource.customer_app,
        status=LeadStatus.prospecting,
        customer_id=current_user.id,
        zone_id=(project.lead.zone_id if project.lead and project.lead.zone_id else project.posted_by_user.zone_id if project.posted_by_user else current_user.zone_id),
        branch_id=(project.lead.branch_id if project.lead and project.lead.branch_id else project.posted_by_user.branch_id if project.posted_by_user else current_user.branch_id),
        farm_details=f"Investment Express Interest in '{project.name}' for ₹{body.proposed_amount:,.2f}. Questions: {body.questions or 'None'}",
    )
    from app.routers.leads import _assign_lead_owner
    _assign_lead_owner(lead, db)
    inv.lead_id = lead.id
    db.add(inv)
    db.add(lead)

    db.commit()
    db.refresh(inv)
    if lead.assigned_employee_id:
        notify_new_lead(lead.assigned_employee_id, f"New investment interest #{inv.id[:8]}", db)
    return success(data=inv_to_dict(inv), message="Interest expressed successfully! Your request is pending verification.")


@router.patch("/{inv_id}/pipeline")
def update_investment_pipeline(
    inv_id: str,
    body: PipelineStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.zone_admin, UserRole.founder)),
):
    inv = db.query(Investment).filter(Investment.id == inv_id).first()
    if not inv: raise HTTPException(404, "Investment record not found")
    _authorize_investment(inv, current_user, db)

    stages = list(InvestmentVerificationStage)
    if body.verification_stage == InvestmentVerificationStage.completed:
        raise HTTPException(400, "Investment completes only after verified payment")
    if body.verification_stage == InvestmentVerificationStage.customer_approved:
        raise HTTPException(400, "The customer must approve their own investment interest")
    if inv.verification_stage == InvestmentVerificationStage.completed:
        raise HTTPException(400, "Completed investment records are immutable")
    if stages.index(body.verification_stage) != stages.index(inv.verification_stage) + 1:
        raise HTTPException(400, "Investment verification stages must be completed in order")
    if body.verification_stage in [InvestmentVerificationStage.zone_approved] and current_user.role not in [UserRole.zone_admin, UserRole.founder]:
        raise HTTPException(403, "Zone Admin approval is required")
    if body.verification_stage == InvestmentVerificationStage.founder_approved:
        if current_user.role != UserRole.founder or inv.verification_stage != InvestmentVerificationStage.zone_approved:
            raise HTTPException(403, "Zone approval must precede Founder approval")
    if body.verification_stage == InvestmentVerificationStage.payment_gateway and inv.verification_stage != InvestmentVerificationStage.founder_approved:
        raise HTTPException(400, "Founder approval is required before payment")
    if body.verification_stage == InvestmentVerificationStage.payment_gateway and current_user.role != UserRole.founder:
        raise HTTPException(403, "Only a Founder can enable investment payment")
    if body.verification_stage == InvestmentVerificationStage.agreemented and not (body.agreement_url or inv.agreement_url):
        raise HTTPException(400, "Upload or link the signed investment agreement before recording agreement completion")

    inv.verification_stage = body.verification_stage
    if body.agreement_url is not None:
        inv.agreement_url = body.agreement_url
    db.commit()
    db.refresh(inv)
    return success(data=inv_to_dict(inv), message=f"Investment verification pipeline stage updated to '{body.verification_stage.value}'")


@router.post("/{inv_id}/payout")
def record_investment_payout(
    inv_id: str,
    body: InvestmentPayout,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    inv = db.query(Investment).filter(Investment.id == inv_id).with_for_update().first()
    if not inv:
        raise HTTPException(404, "Investment not found")
    project = db.query(Project).filter(Project.id == inv.project_id).with_for_update().first()
    if not project:
        raise HTTPException(404, "Project not found")
    if current_user.role == UserRole.zone_admin:
        branch_id = project.lead.branch_id if project.lead else (project.posted_by_user.branch_id if project.posted_by_user else None)
        if branch_id != current_user.branch_id:
            raise HTTPException(404, "Investment not found")
    if project.status not in [ProjectStatus.completed, ProjectStatus.settled]:
        raise HTTPException(400, "Investor payouts can be recorded only after project completion")
    if inv.status == InvestmentStatus.settled:
        raise HTTPException(409, "This investment payout has already been recorded")
    if inv.status != InvestmentStatus.active or inv.revenue_share_percentage is None:
        raise HTTPException(400, "Only funded investments with a calculated revenue share can be paid")
    inv.actual_return = calculate_expected_return(inv, project)
    inv.payout_reference = body.transaction_reference.strip()
    inv.payout_proof_url = body.proof_url.strip()
    inv.status = InvestmentStatus.settled
    from datetime import date
    inv.settlement_date = date.today()
    db.commit()
    db.refresh(inv)
    return success(data=inv_to_dict(inv), message="Investor payout and proof recorded")


@router.post("")
def create_investment(
    body: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(410, "Direct investment creation is disabled. Create an interest record, complete approvals, then confirm a verified payment.")


@router.get("/{inv_id}")
def get_investment(inv_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    inv = db.query(Investment).filter(Investment.id == inv_id).first()
    if not inv:
        raise HTTPException(404, "Investment not found")
    _authorize_investment(inv, _, db)
    return success(data=inv_to_dict(inv))


@router.get("/{inv_id}/revenue-share")
def get_revenue_share(inv_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    inv = db.query(Investment).filter(Investment.id == inv_id).first()
    if not inv:
        raise HTTPException(404, "Investment not found")
    _authorize_investment(inv, _, db)
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
        "verification_stage": inv.verification_stage.value,
    })
