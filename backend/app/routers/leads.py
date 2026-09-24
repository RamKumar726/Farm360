import uuid
import secrets
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, EmailStr, Field
from app.database import get_db
from app.models.leads import Lead, LeadType, LeadSource, LeadStatus
from app.models.users import User, UserRole
from app.models.customers import Customer
from app.models.branches import Branch
from app.models.zones import Zone
from app.auth.dependencies import get_current_user, require_roles
from app.services.lead_service import transition_lead
from app.services.notification_service import notify_new_lead

router = APIRouter(prefix="/leads", tags=["leads"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class LeadCreate(BaseModel):
    type: LeadType
    source: LeadSource
    customer_id: Optional[str] = None
    zone_id: Optional[str] = None
    branch_id: Optional[str] = None
    farm_details: Optional[str] = None
    is_opportunity: bool = False
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    crop_name: Optional[str] = None
    farm_location: Optional[str] = None
    farm_area: Optional[float] = Field(default=None, gt=0)
    existing_project_id: Optional[str] = None


class RegisterCustomerRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class FeasibilityReport(BaseModel):
    report: str


class PublicConsultationCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    location: Optional[str] = None
    space_type: Optional[str] = "Terrace"
    service: Optional[str] = None
    notes: Optional[str] = None


class LeadStageUpdate(BaseModel):
    status: LeadStatus
    lost_reason: Optional[str] = None
    qualification_data: Optional[str] = None
    need_analysis_data: Optional[str] = None
    value_prop_data: Optional[str] = None
    land_verification_data: Optional[str] = None
    ao_feasibility_data: Optional[str] = None
    commercial_model_data: Optional[str] = None
    proposal_data: Optional[str] = None
    negotiation_data: Optional[str] = None
    agreement_url: Optional[str] = None
    assigned_ao_id: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    services_needed: Optional[str] = None
    price_to_complete: Optional[float] = Field(default=None, ge=0)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    final_amount: Optional[float] = Field(default=None, ge=0)
    existing_project_id: Optional[str] = None
    project_level: Optional[str] = None
    crop_name: Optional[str] = None
    farm_location: Optional[str] = None
    farm_area: Optional[float] = Field(default=None, gt=0)
    lease_arrangement_type: Optional[str] = None
    commercial_model_type: Optional[str] = None
    settlement_base: Optional[str] = None
    fixed_lease_amount: Optional[float] = Field(default=None, ge=0)
    revenue_share_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    lease_duration_months: Optional[int] = Field(default=None, gt=0)
    payment_frequency: Optional[str] = Field(default=None, pattern="^(monthly|quarterly|annual)$")
    possession_date: Optional[date] = None
    landowner_responsibilities: Optional[str] = None
    company_responsibilities: Optional[str] = None
    termination_conditions: Optional[str] = None


def lead_to_dict(l: Lead):
    return {
        "id": l.id, "type": l.type.value, "source": l.source.value,
        "is_opportunity": l.is_opportunity,
        "contact_name": l.contact_name, "contact_phone": l.contact_phone,
        "contact_email": l.contact_email,
        "crop_name": l.crop_name,
        "farm_location": l.farm_location, "farm_area": l.farm_area,
        "project_level": l.project_level, "lease_arrangement_type": l.lease_arrangement_type,
        "commercial_model_type": l.commercial_model_type, "settlement_base": l.settlement_base,
        "fixed_lease_amount": l.fixed_lease_amount, "revenue_share_percentage": l.revenue_share_percentage,
        "lease_duration_months": l.lease_duration_months, "payment_frequency": l.payment_frequency,
        "possession_date": str(l.possession_date) if l.possession_date else None,
        "landowner_responsibilities": l.landowner_responsibilities,
        "company_responsibilities": l.company_responsibilities,
        "termination_conditions": l.termination_conditions,
        "project_id": l.project_id, "existing_project_id": l.existing_project_id,
        "renewal_for_date": str(l.renewal_for_date) if l.renewal_for_date else None,
        "related_land_sale_id": l.related_land_sale_id,
        "status": l.status.value, "customer_id": l.customer_id,
        "employee_id": l.employee_id, "assigned_ao_id": l.assigned_ao_id,
        "assigned_employee_id": l.assigned_employee_id,
        "zone_id": l.zone_id, "branch_id": l.branch_id, "farm_details": l.farm_details,
        "qualification_data": l.qualification_data,
        "need_analysis_data": l.need_analysis_data,
        "value_prop_data": l.value_prop_data,
        "land_verification_data": l.land_verification_data,
        "ao_feasibility_data": l.ao_feasibility_data,
        "commercial_model_data": l.commercial_model_data,
        "proposal_data": l.proposal_data,
        "negotiation_data": l.negotiation_data,
        "ao_quotation_doc": l.ao_quotation_doc,
        "agreement_url": l.agreement_url,
        "is_reviewed_by_employee": l.is_reviewed_by_employee,
        "sent_to_client": l.sent_to_client,
        "approval_status": l.approval_status,
        "services_needed": l.services_needed,
        "price_to_complete": l.price_to_complete,
        "discount_amount": l.discount_amount,
        "final_amount": l.final_amount,
        "site_visit_date": str(l.site_visit_date) if l.site_visit_date else None,
        "advance_paid_date": str(l.advance_paid_date) if l.advance_paid_date else None,
        "payment_confirmed_at": str(l.payment_confirmed_at) if l.payment_confirmed_at else None,
        "won_date": str(l.won_date) if l.won_date else None,
        "lost_reason": l.lost_reason, "created_at": str(l.created_at),
    }


@router.get("")
def list_leads(
    page: int = Query(1, ge=1), page_size: int = Query(50),
    status: Optional[LeadStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_roles = {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.customer}
    if current_user.role not in allowed_roles:
        raise HTTPException(403, "You cannot access leads")
    query = db.query(Lead).filter(Lead.is_deleted == False, Lead.type != LeadType.investment_interest)
    if current_user.role == UserRole.customer:
        query = query.filter(Lead.customer_id == current_user.id)
    elif current_user.role == UserRole.zone_admin:
        query = query.filter(or_(
            and_(Lead.branch_id.isnot(None), Lead.branch_id == current_user.branch_id) if current_user.branch_id else False,
            and_(Lead.branch_id.is_(None), Lead.zone_id == current_user.zone_id) if current_user.zone_id else and_(Lead.branch_id.is_(None), Lead.zone_id.is_(None)),
        ))
    elif current_user.role == UserRole.employee:
        unassigned_scope = or_(
            and_(Lead.branch_id == current_user.branch_id, Lead.branch_id.isnot(None)) if current_user.branch_id else False,
            and_(Lead.branch_id.is_(None), Lead.zone_id == current_user.zone_id) if current_user.zone_id else and_(Lead.branch_id.is_(None), Lead.zone_id.is_(None)),
        )
        query = query.filter(
            (Lead.employee_id == current_user.id) |
            (Lead.assigned_ao_id == current_user.id) |
            (Lead.employee_id.is_(None) & Lead.assigned_employee_id.is_(None) & unassigned_scope)
        )
    elif current_user.role == UserRole.agri_officer:
        query = query.filter(Lead.assigned_ao_id == current_user.id)
    elif current_user.role == UserRole.founder:
        pass
    if status:
        query = query.filter(Lead.status == status)
    total = query.count()
    items = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [lead_to_dict(l) for l in items]})


@router.post("/public")
def create_public_lead(
    body: PublicConsultationCreate,
    db: Session = Depends(get_db),
):
    lead_type = LeadType.one_time_service
    notes_lower = (body.notes or "").lower()
    service_lower = (body.service or "").lower()
    if "lease" in service_lower:
        lead_type = LeadType.farm_lease
    elif body.space_type == "Farm" or "farm" in service_lower or "paddy" in notes_lower or "cultivate" in notes_lower:
        lead_type = LeadType.farm_management
    elif body.space_type == "Small plot":
        lead_type = LeadType.site_management

    farm_details = f"Client: {body.name} | Contact: {body.phone}"
    if body.location:
        farm_details += f" | Location: {body.location}"
    if body.space_type:
        farm_details += f" | Space: {body.space_type}"
    if body.service:
        farm_details += f" | Service: {body.service}"
    if body.notes:
        farm_details += f" | Requirements: {body.notes}"

    branch_id, zone_id = _match_public_lead_region(body.location, db)
    lead = Lead(
        id=str(uuid.uuid4()),
        type=lead_type,
        source=LeadSource.website,
        status=LeadStatus.prospecting,
        customer_id=None,
        contact_name=body.name,
        contact_phone=body.phone,
        contact_email=body.email,
        farm_location=body.location,
        branch_id=branch_id,
        zone_id=zone_id,
        lease_arrangement_type=("lease_arrangement" if "partner" in service_lower or "arrangement" in service_lower else "in_house_lease") if lead_type == LeadType.farm_lease else None,
        employee_id=None,
        farm_details=farm_details,
    )
    db.add(lead)
    _assign_lead_owner(lead, db)
    db.commit()
    db.refresh(lead)
    if lead.assigned_employee_id:
        notify_new_lead(lead.assigned_employee_id, f"New website enquiry #{lead.id[:8]} ({lead.type.value})", db)
    return success(data=lead_to_dict(lead), message="Consultation request created")


@router.post("")
def create_lead(
    body: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.customer}:
        raise HTTPException(403, "You cannot create leads")
    customer_id = current_user.id if current_user.role == UserRole.customer else body.customer_id
    if current_user.role == UserRole.customer and not db.query(Customer.id).filter(Customer.user_id == current_user.id).first():
        db.add(Customer(id=str(uuid.uuid4()), user_id=current_user.id,
                        branch_id=current_user.branch_id, zone_id=current_user.zone_id))
    is_opportunity = body.is_opportunity or (current_user.role == UserRole.customer and customer_id is not None)
    lead = Lead(
        id=str(uuid.uuid4()),
        type=body.type, source=body.source,
        status=LeadStatus.prospecting,
        customer_id=customer_id,
        is_opportunity=is_opportunity,
        contact_name=body.contact_name or (current_user.name if current_user.role == UserRole.customer else None),
        contact_phone=body.contact_phone or (current_user.phone if current_user.role == UserRole.customer else None),
        contact_email=body.contact_email or (current_user.email if current_user.role == UserRole.customer else None),
        crop_name=body.crop_name,
        farm_location=body.farm_location,
        farm_area=body.farm_area,
        existing_project_id=body.existing_project_id,
        employee_id=current_user.id if current_user.role == UserRole.employee else None,
        zone_id=(current_user.zone_id if current_user.role == UserRole.customer else (body.zone_id or current_user.zone_id)),
        branch_id=(current_user.branch_id if current_user.role == UserRole.customer else (body.branch_id or current_user.branch_id)),
        farm_details=body.farm_details,
    )
    db.add(lead)
    _assign_lead_owner(lead, db, creator=current_user)
    db.commit()
    db.refresh(lead)
    if lead.assigned_employee_id and lead.assigned_employee_id != current_user.id:
        notify_new_lead(lead.assigned_employee_id, f"New lead #{lead.id[:8]} created ({lead.type.value})", db)
    return success(data=lead_to_dict(lead), message="Lead created")


@router.get("/lost")
def list_lost_leads(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.customer}:
        raise HTTPException(403, "You cannot access closed leads")
    query = db.query(Lead).filter(Lead.status == LeadStatus.closed_lost)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Lead.branch_id == current_user.branch_id)
    elif current_user.role == UserRole.employee:
        query = query.filter(Lead.employee_id == current_user.id)
    elif current_user.role == UserRole.customer:
        query = query.filter(Lead.customer_id == current_user.id)
    total = query.count()
    items = query.order_by(Lead.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [lead_to_dict(l) for l in items]})


@router.get("/won")
def list_won_leads(
    page: int = Query(1, ge=1), page_size: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.customer}:
        raise HTTPException(403, "You cannot access closed leads")
    query = db.query(Lead).filter(Lead.status == LeadStatus.closed_won)
    if current_user.role == UserRole.zone_admin:
        query = query.filter(Lead.branch_id == current_user.branch_id)
    elif current_user.role == UserRole.employee:
        query = query.filter(Lead.employee_id == current_user.id)
    elif current_user.role == UserRole.customer:
        query = query.filter(Lead.customer_id == current_user.id)
    total = query.count()
    items = query.order_by(Lead.won_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [lead_to_dict(l) for l in items]})


@router.get("/{lead_id}")
def get_lead(lead_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")

    _authorize_lead(lead, current_user)
    return success(data=lead_to_dict(lead))


@router.patch("/{lead_id}/status")
def update_lead_status(
    lead_id: str,
    body: LeadStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.zone_admin, UserRole.founder)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user, allow_unassigned=True)

    if body.status == LeadStatus.qualification and not (body.qualification_data or lead.qualification_data):
        raise HTTPException(400, "Qualification details are required")
    if body.status == LeadStatus.need_analysis and not (body.need_analysis_data or lead.need_analysis_data):
        raise HTTPException(400, "Need analysis challenges and goals are required")
    if lead.type == LeadType.farm_lease and body.status == LeadStatus.need_analysis and not (body.lease_arrangement_type or lead.lease_arrangement_type):
        raise HTTPException(400, "Choose whether FarmCare takes the land directly or arranges another lease taker")
    if lead.type == LeadType.farm_lease and body.status == LeadStatus.land_verification:
        ao_id = body.assigned_ao_id or lead.assigned_ao_id
        if not ao_id:
            raise HTTPException(400, "Assign an Agriculture Officer for the lease site assessment")
        ao = db.query(User).filter(User.id == ao_id, User.role == UserRole.agri_officer, User.is_deleted == False).first()
        if not ao:
            raise HTTPException(400, "Assigned Agriculture Officer must be an active account")
    if body.status == LeadStatus.value_proposition and not (body.value_prop_data or lead.value_prop_data):
        raise HTTPException(400, "A value proposition statement is required")
    if body.status == LeadStatus.decision_makers:
        ao_id = body.assigned_ao_id or lead.assigned_ao_id
        ao = db.query(User).filter(User.id == ao_id, User.role == UserRole.agri_officer, User.is_deleted == False).first() if ao_id else None
        if not ao:
            raise HTTPException(400, "Assign an active Agriculture Officer before entering Decision Makers")
    if body.assigned_ao_id is not None:
        assigned_ao = db.query(User).filter(User.id == body.assigned_ao_id, User.role == UserRole.agri_officer, User.is_deleted == False).first()
        if not assigned_ao:
            raise HTTPException(400, "Assigned Agriculture Officer must be an active account")
        if lead.branch_id and assigned_ao.branch_id != lead.branch_id:
            raise HTTPException(400, "Assigned Agriculture Officer must belong to the lead's branch")
        if not lead.branch_id and lead.zone_id and assigned_ao.zone_id != lead.zone_id:
            raise HTTPException(400, "Assigned Agriculture Officer must belong to the lead's zone")
    if body.assigned_employee_id is not None:
        assigned_employee = db.query(User).filter(User.id == body.assigned_employee_id, User.role == UserRole.employee, User.is_deleted == False).first()
        if not assigned_employee:
            raise HTTPException(400, "Assigned employee must be an active employee account")
        if lead.branch_id and assigned_employee.branch_id != lead.branch_id:
            raise HTTPException(400, "Assigned employee must belong to the lead's branch")
        if not lead.branch_id and lead.zone_id and assigned_employee.zone_id != lead.zone_id:
            raise HTTPException(400, "Assigned employee must belong to the lead's zone")

    if body.status == LeadStatus.login_guide and not lead.customer_id:
        raise HTTPException(400, "Create or attach the customer account before login guidance")
    if body.status == LeadStatus.payment:
        if not lead.customer_id or not lead.sent_to_client:
            raise HTTPException(400, "A registered customer and sent quotation are required before payment")
        if lead.final_amount is None and lead.price_to_complete is None:
            raise HTTPException(400, "Set the final agreed amount before payment")
    if body.status == LeadStatus.negotiation and lead.type not in {LeadType.farm_lease, LeadType.sell_land} and not lead.sent_to_client:
        raise HTTPException(400, "Send the reviewed Agriculture Officer quotation to the customer before negotiating the final price")
    proposed_base = body.price_to_complete if body.price_to_complete is not None else lead.price_to_complete
    proposed_discount = body.discount_amount if body.discount_amount is not None else (lead.discount_amount or 0)
    proposed_final = body.final_amount if body.final_amount is not None else lead.final_amount
    if proposed_base is not None and proposed_discount > proposed_base:
        raise HTTPException(400, "Negotiated discount cannot exceed the original quoted price")
    if proposed_base is not None and proposed_final is not None and proposed_final > proposed_base:
        raise HTTPException(400, "Final agreed price cannot exceed the original quoted price")
    if body.discount_amount is not None and body.final_amount is not None and abs(body.final_amount - (proposed_base - body.discount_amount)) > 0.01:
        raise HTTPException(400, "Final agreed price must equal the original quote minus the negotiated discount")
    if lead.type == LeadType.farm_lease and body.status == LeadStatus.proposal:
        if not (lead.ao_feasibility_data or body.ao_feasibility_data):
            raise HTTPException(400, "Complete the Agriculture Officer feasibility report before preparing the proposal")
        proposal = body.proposal_data or lead.proposal_data
        final_amount = body.final_amount if body.final_amount is not None else lead.final_amount
        price = body.price_to_complete if body.price_to_complete is not None else lead.price_to_complete
        if not proposal or (final_amount is None and price is None):
            raise HTTPException(400, "Lease proposal terms and a proposed amount are required")
    if lead.type == LeadType.farm_lease and body.status == LeadStatus.feasibility and not (lead.land_verification_data or body.land_verification_data):
        raise HTTPException(400, "Record land and document verification before feasibility assessment")
    if lead.type == LeadType.farm_lease and body.status == LeadStatus.commercial_model:
        if not (lead.ao_feasibility_data or body.ao_feasibility_data):
            raise HTTPException(400, "The assigned Agriculture Officer must submit feasibility before lease terms are selected")
        model = body.commercial_model_type or lead.commercial_model_type
        duration = body.lease_duration_months if body.lease_duration_months is not None else lead.lease_duration_months
        frequency = body.payment_frequency or lead.payment_frequency
        landowner = body.landowner_responsibilities or lead.landowner_responsibilities
        company = body.company_responsibilities or lead.company_responsibilities
        termination = body.termination_conditions or lead.termination_conditions
        if not all((model, duration, frequency, landowner, company, termination)):
            raise HTTPException(400, "Complete the lease model, duration, frequency, both parties’ responsibilities, and termination conditions")
        percentage = body.revenue_share_percentage if body.revenue_share_percentage is not None else lead.revenue_share_percentage
        fixed = body.fixed_lease_amount if body.fixed_lease_amount is not None else lead.fixed_lease_amount
        settlement_base = body.settlement_base or lead.settlement_base
        if model in ("fixed_plus_percentage", "percentage_share") and settlement_base not in ("revenue", "net_realization", "defined_profit"):
            raise HTTPException(400, "Choose a settlement base for percentage payments")
        if model == "fixed_lease" and not fixed:
            raise HTTPException(400, "Enter the fixed lease amount")
        if model == "fixed_plus_percentage" and (not fixed or not percentage):
            raise HTTPException(400, "Enter both the fixed amount and percentage")
        if model == "percentage_share" and not percentage:
            raise HTTPException(400, "Enter the revenue share percentage")
    if lead.type == LeadType.farm_lease and body.status == LeadStatus.agreement and not (body.agreement_url or lead.agreement_url):
        raise HTTPException(400, "Attach the executed lease agreement before moving to approval")
    if lead.status == LeadStatus.payment and any(value is not None for value in (body.final_amount, body.price_to_complete, body.discount_amount)):
        from app.models.finance import Payment, PaymentStatus
        pending_order = db.query(Payment.id).filter(
            Payment.lead_id == lead.id, Payment.status == PaymentStatus.created
        ).first()
        if pending_order:
            proposed_final = body.final_amount if body.final_amount is not None else lead.final_amount
            proposed_price = body.price_to_complete if body.price_to_complete is not None else lead.price_to_complete
            proposed_discount = body.discount_amount if body.discount_amount is not None else lead.discount_amount
            if (proposed_final, proposed_price, proposed_discount) != (lead.final_amount, lead.price_to_complete, lead.discount_amount):
                raise HTTPException(409, "The quotation is locked while a payment order is active")

    transition_lead(lead, body.status, body.lost_reason)

    # Update stage payloads if provided
    if body.qualification_data is not None: lead.qualification_data = body.qualification_data
    if body.need_analysis_data is not None: lead.need_analysis_data = body.need_analysis_data
    if body.value_prop_data is not None: lead.value_prop_data = body.value_prop_data
    if body.land_verification_data is not None: lead.land_verification_data = body.land_verification_data
    if body.ao_feasibility_data is not None: lead.ao_feasibility_data = body.ao_feasibility_data
    if body.commercial_model_data is not None: lead.commercial_model_data = body.commercial_model_data
    if body.proposal_data is not None: lead.proposal_data = body.proposal_data
    if body.negotiation_data is not None: lead.negotiation_data = body.negotiation_data
    if body.agreement_url is not None: lead.agreement_url = body.agreement_url
    if body.assigned_ao_id is not None:
        is_new_ao_assignment = body.assigned_ao_id != lead.assigned_ao_id
        lead.assigned_ao_id = body.assigned_ao_id
        if is_new_ao_assignment:
            notify_new_lead(body.assigned_ao_id, f"Lease feasibility assessment assigned for lead #{lead.id[:8]}", db)
    if body.assigned_employee_id is not None: lead.assigned_employee_id = body.assigned_employee_id
    if current_user.role == UserRole.employee and lead.employee_id is None:
        lead.employee_id = current_user.id
    if current_user.role == UserRole.employee and lead.assigned_employee_id is None:
        lead.assigned_employee_id = current_user.id
    if body.services_needed is not None: lead.services_needed = body.services_needed
    if body.price_to_complete is not None: lead.price_to_complete = body.price_to_complete
    if body.discount_amount is not None: lead.discount_amount = body.discount_amount
    if body.final_amount is not None: lead.final_amount = body.final_amount
    elif body.status == LeadStatus.negotiation and lead.final_amount is None and lead.price_to_complete is not None:
        lead.final_amount = lead.price_to_complete
    if body.crop_name is not None: lead.crop_name = body.crop_name
    if body.farm_location is not None: lead.farm_location = body.farm_location
    if body.farm_area is not None: lead.farm_area = body.farm_area
    if body.existing_project_id is not None: lead.existing_project_id = body.existing_project_id
    for field in ("project_level", "lease_arrangement_type", "commercial_model_type", "settlement_base", "fixed_lease_amount", "revenue_share_percentage", "lease_duration_months", "payment_frequency", "possession_date", "landowner_responsibilities", "company_responsibilities", "termination_conditions"):
        value = getattr(body, field)
        if value is not None:
            setattr(lead, field, value)

    # Auto-create exactly one project when the deal closes.
    if body.status == LeadStatus.closed_won:
        _close_won_lead(lead, current_user, db)

    db.commit()
    db.refresh(lead)
    return success(data=lead_to_dict(lead), message=f"Lead status updated to {body.status.value}")


@router.post("/{lead_id}/register-customer")
def register_lead_customer(
    lead_id: str,
    body: RegisterCustomerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.zone_admin, UserRole.founder)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.is_deleted == False).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user, allow_unassigned=True)
    if lead.contact_email and body.email.casefold() != lead.contact_email.casefold():
        raise HTTPException(400, "Use the email address recorded on the lead")
    if lead.contact_phone and body.phone and body.phone.strip() != lead.contact_phone.strip():
        raise HTTPException(400, "Use the phone number recorded on the lead")
    lease_registration = (
        lead.type == LeadType.farm_lease
        and not lead.is_opportunity
        and lead.status in {LeadStatus.agreement, LeadStatus.approval}
    )
    if lead.is_opportunity or (lead.status != LeadStatus.register_user and not lease_registration):
        raise HTTPException(400, "This lead is not at a customer-registration stage")
    user = db.query(User).filter(User.email == body.email).first()
    temporary_password = None
    if user and user.role != UserRole.customer:
        raise HTTPException(409, "This email is already associated with a staff account")
    if user and body.phone and user.phone and body.phone.strip() != user.phone.strip():
        raise HTTPException(409, "The phone number does not match this customer account")
    if user is None:
        from app.auth.jwt import hash_password
        temporary_password = secrets.token_urlsafe(12)
        user = User(id=str(uuid.uuid4()), name=body.name, email=body.email, phone=body.phone,
                    password_hash=hash_password(temporary_password), role=UserRole.customer,
                    branch_id=lead.branch_id, zone_id=lead.zone_id)
        db.add(user)
        db.flush()
    customer = db.query(Customer).filter(Customer.user_id == user.id).first()
    if not customer:
        customer = Customer(id=str(uuid.uuid4()), user_id=user.id,
                            branch_id=lead.branch_id, zone_id=lead.zone_id)
        db.add(customer)
    lead.customer_id = user.id
    lead.contact_name = body.name
    lead.contact_email = body.email
    lead.contact_phone = body.phone
    db.commit()
    db.refresh(lead)
    return success({"lead": lead_to_dict(lead), "temporary_password": temporary_password},
                   "Customer account created. Share the temporary password securely." if temporary_password else "Existing customer account linked to lead")


@router.post("/{lead_id}/reset-customer-password")
def reset_lead_customer_password(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.zone_admin, UserRole.founder)),
):
    """Issue a fresh one-time password when staff missed the original display."""
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.is_deleted == False).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user)
    if not lead.customer_id:
        raise HTTPException(400, "Create or link the customer account first")
    customer_user = db.query(User).filter(
        User.id == lead.customer_id, User.role == UserRole.customer, User.is_deleted == False
    ).first()
    if not customer_user:
        raise HTTPException(404, "Linked customer account not found")
    temporary_password = secrets.token_urlsafe(12)
    from app.auth.jwt import hash_password
    customer_user.password_hash = hash_password(temporary_password)
    db.commit()
    return success({"temporary_password": temporary_password, "email": customer_user.email},
                   "Temporary password reset. Share it securely with the customer.")


@router.post("/{lead_id}/ao-quotation")
def submit_ao_quotation(
    lead_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead: raise HTTPException(404, "Lead not found")
    if lead.assigned_ao_id != current_user.id:
        raise HTTPException(403, "This lead is assigned to another Agriculture Officer")
    if lead.status != LeadStatus.decision_makers:
        raise HTTPException(status_code=400, detail="Quotation can be submitted only during Decision Makers stage")
    import json
    lead.ao_quotation_doc = json.dumps(payload)
    if payload.get("services_needed") is not None: lead.services_needed = json.dumps(payload.get("services_needed"))
    if payload.get("price_to_complete") is not None: lead.price_to_complete = float(payload.get("price_to_complete"))
    lead.assigned_ao_id = current_user.id if current_user.role == UserRole.agri_officer else lead.assigned_ao_id
    lead.status = LeadStatus.proposal_price
    db.commit()
    db.refresh(lead)
    return success(data=lead_to_dict(lead), message="Quotation and solution document submitted by AO")


@router.post("/{lead_id}/ao-feasibility")
def submit_lease_feasibility(
    lead_id: str,
    body: FeasibilityReport,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.agri_officer)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead or lead.type != LeadType.farm_lease or lead.assigned_ao_id != current_user.id:
        raise HTTPException(404, "Assigned lease assessment not found")
    if lead.status != LeadStatus.feasibility:
        raise HTTPException(400, "Lease feasibility can be submitted only during the feasibility stage")
    if not body.report.strip():
        raise HTTPException(400, "A feasibility report is required")
    lead.ao_feasibility_data = body.report.strip()
    db.commit()
    db.refresh(lead)
    return success(data=lead_to_dict(lead), message="Lease feasibility report submitted")


@router.post("/{lead_id}/review-quote")
def review_and_send_quote(
    lead_id: str,
    action: str = Query("send"), # review or send
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.zone_admin, UserRole.founder)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead: raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user, allow_unassigned=True)
    if lead.status != LeadStatus.proposal_price:
        raise HTTPException(status_code=400, detail="Quote review is available only during Proposal/Price stage")
    if action == "review":
        lead.is_reviewed_by_employee = True
    elif action == "send":
        if not lead.is_reviewed_by_employee:
            raise HTTPException(status_code=400, detail="Review the Agriculture Officer quote before sending it to the customer")
        if not lead.ao_quotation_doc:
            raise HTTPException(status_code=400, detail="The Agriculture Officer must submit a quotation first")
        lead.is_reviewed_by_employee = True
        lead.sent_to_client = True
        if lead.final_amount is None and lead.price_to_complete is not None:
            lead.final_amount = lead.price_to_complete
    else:
        raise HTTPException(status_code=400, detail="Action must be 'review' or 'send'")
    db.commit()
    db.refresh(lead)
    return success(data=lead_to_dict(lead), message=f"Quotation updated ({action})")


@router.post("/{lead_id}/approval")
def approve_lease_lead(
    lead_id: str,
    approved: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.zone_admin, UserRole.founder)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead: raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user)
    if current_user.role == UserRole.zone_admin:
        if lead.status != LeadStatus.approval:
            raise HTTPException(status_code=400, detail="Lease is not awaiting approval")
        lead.approval_status = "approved_zone" if approved else "rejected"
    elif current_user.role == UserRole.founder:
        if lead.status != LeadStatus.approval:
            raise HTTPException(status_code=400, detail="Lease is not awaiting approval")
        if approved and lead.approval_status != "approved_zone":
            raise HTTPException(status_code=400, detail="Zone Admin approval is required before Founder approval")
        if approved and lead.type == LeadType.farm_lease:
            from app.models.customers import Customer
            if not lead.customer_id or not db.query(Customer.id).filter(Customer.user_id == lead.customer_id).first():
                raise HTTPException(status_code=400, detail="Register or link the landowner customer account before Founder approval")
        lead.approval_status = "approved_founder" if approved else "rejected"
        if approved:
            transition_lead(lead, LeadStatus.closed_won)
            _close_won_lead(lead, current_user, db)
        else:
            lead.status = LeadStatus.closed_lost
            lead.lost_reason = "Founder rejected lease approval"
    elif not approved:
        lead.status = LeadStatus.closed_lost
        lead.lost_reason = "Zone Admin rejected lease approval"
    db.commit()
    db.refresh(lead)
    return success(data=lead_to_dict(lead), message=f"Approval status updated to {lead.approval_status}")


def _close_won_lead(lead: Lead, current_user: User, db: Session) -> None:
    from datetime import date, timedelta
    from app.models.projects import Project, ProjectType, ProjectApprovalStatus, ProjectStatus

    lease_or_sale = lead.type in [LeadType.farm_lease, LeadType.sell_land]
    if lease_or_sale and lead.approval_status != "approved_founder":
        raise HTTPException(status_code=400, detail="Founder approval is required before closing this deal")
    if not lease_or_sale:
        if not lead.is_opportunity and not lead.customer_id:
            raise HTTPException(status_code=400, detail="Register the customer before closing this lead")
        if lead.payment_confirmed_at is None:
            raise HTTPException(status_code=400, detail="Confirmed customer payment is required before closing this lead")
    amount = lead.final_amount if lead.final_amount is not None else lead.price_to_complete
    if amount is None or amount < 0:
        raise HTTPException(status_code=400, detail="A final agreed amount is required before closing")
    if db.query(Project).filter(Project.lead_id == lead.id).first():
        raise HTTPException(status_code=409, detail="A project already exists for this lead")

    project_type = (ProjectType.land_sale if lead.type == LeadType.sell_land else ProjectType.lease) if lease_or_sale else (ProjectType.managing_farm if lead.type in [LeadType.farm_manage, LeadType.farm_management] else ProjectType.one_time_service)
    today = date.today()
    if lead.type in [LeadType.farm_manage, LeadType.farm_management] and lead.existing_project_id:
        project = db.query(Project).filter(Project.id == lead.existing_project_id, Project.customer_id == lead.customer_id).with_for_update().first()
        if not project:
            raise HTTPException(status_code=404, detail="Selected existing customer project was not found")
        if project.status not in [ProjectStatus.completed, ProjectStatus.settled, ProjectStatus.active]:
            raise HTTPException(status_code=400, detail="Only a completed, settled or active customer project can be used for farm management")
        if not project.farm_id:
            from app.models.customers import Customer
            from app.models.farms import Farm
            customer_profile = db.query(Customer).filter(Customer.user_id == lead.customer_id).first()
            if not customer_profile:
                raise HTTPException(status_code=400, detail="A customer profile is required to start farm management")
            farm = db.query(Farm).filter(Farm.customer_id == customer_profile.id).first()
            if not farm:
                farm = Farm(id=str(uuid.uuid4()), customer_id=customer_profile.id,
                            location=lead.farm_location, area=lead.farm_area,
                            zone_id=lead.zone_id or customer_profile.zone_id,
                            notes=f"Farm management request: {lead.farm_details or 'Farm management'}")
                db.add(farm)
                db.flush()
            elif lead.farm_location or lead.farm_area:
                if lead.farm_location: farm.location = lead.farm_location
                if lead.farm_area is not None: farm.area = lead.farm_area
                if not farm.zone_id: farm.zone_id = lead.zone_id or customer_profile.zone_id
            project.farm_id = farm.id
        project.type = ProjectType.managing_farm
        project.status = ProjectStatus.active
        project.total_amount = amount
        project.start_date = today
        project.end_date = today + timedelta(days=30)
        project.subscription_end = today + timedelta(days=30)
        project.assigned_ao_id = lead.assigned_ao_id
    else:
        project_start = (lead.possession_date or today) if project_type == ProjectType.lease else today
        project_end = (project_start + timedelta(days=(lead.lease_duration_months or 12) * 30)) if project_type == ProjectType.lease else (
            today + timedelta(days=30) if project_type == ProjectType.managing_farm else None
        )
        farm_id = None
        needs_farm_record = project_type in [ProjectType.managing_farm, ProjectType.lease] or (
            project_type == ProjectType.one_time_service and bool(lead.farm_location or lead.farm_area is not None)
        )
        if needs_farm_record and lead.customer_id:
            from app.models.customers import Customer
            from app.models.farms import Farm
            customer_profile = db.query(Customer).filter(Customer.user_id == lead.customer_id).with_for_update().first()
            if not customer_profile and project_type == ProjectType.managing_farm:
                raise HTTPException(status_code=400, detail="A customer profile is required to start farm management")
            farm = db.query(Farm).filter(Farm.customer_id == customer_profile.id).first() if customer_profile else None
            if not farm and customer_profile:
                farm = Farm(id=str(uuid.uuid4()), customer_id=customer_profile.id,
                            location=lead.farm_location, area=lead.farm_area,
                            zone_id=lead.zone_id or customer_profile.zone_id,
                            notes=f"Farm details from lead: {lead.farm_details or 'Farm'}")
                db.add(farm)
                db.flush()
            elif farm and (lead.farm_location or lead.farm_area is not None):
                if lead.farm_location: farm.location = lead.farm_location
                if lead.farm_area is not None: farm.area = lead.farm_area
                if not farm.zone_id: farm.zone_id = lead.zone_id or customer_profile.zone_id
            farm_id = farm.id
        project = Project(
            id=str(uuid.uuid4()), name=f"Project for Lead #{lead.id[:8]}", type=project_type,
            lead_id=lead.id, customer_id=lead.customer_id, farm_id=farm_id, total_amount=amount,
            status=ProjectStatus.not_started if project_type == ProjectType.one_time_service else ProjectStatus.active,
            approval_status=ProjectApprovalStatus.approved, posted_by=current_user.id,
            description=lead.farm_details or "Project created from closed won lead",
            start_date=project_start, end_date=project_end,
            subscription_end=project_end if project_type == ProjectType.managing_farm else None,
            assigned_ao_id=lead.assigned_ao_id,
            crop_name=lead.crop_name,
        )
        db.add(project)
    lead.project_id = project.id
    lead.won_date = today
    if project_type == ProjectType.one_time_service and lead.type != LeadType.service_enquiry:
        from app.models.work_orders import WorkOrder, WorkOrderType, WorkOrderStatus, PaymentStatus
        existing_ticket = db.query(WorkOrder).filter(WorkOrder.lead_id == lead.id).first()
        if not existing_ticket:
            details = f"{lead.services_needed or ''} {lead.farm_details or ''}".casefold()
            if "bore" in details or "well" in details:
                work_type = WorkOrderType.construction
            elif "fenc" in details:
                work_type = WorkOrderType.securing
            elif "clean" in details:
                work_type = WorkOrderType.cleaning
            else:
                work_type = WorkOrderType.monitoring
            assigned_employee = lead.assigned_employee_id or lead.employee_id
            db.add(WorkOrder(
                id=str(uuid.uuid4()), farm_id=project.farm_id, project_id=project.id,
                lead_id=lead.id, type=work_type,
                status=WorkOrderStatus.assigned if assigned_employee else WorkOrderStatus.pending,
                payment_status=PaymentStatus.paid, assigned_employee_id=assigned_employee,
                notes=f"Customer service work: {lead.services_needed or lead.farm_details or lead.type.value}",
                created_by=current_user.id,
            ))
    if project.type == ProjectType.managing_farm and lead.customer_id:
        from app.models.customers import Customer, ServiceType
        customer = db.query(Customer).filter(Customer.user_id == lead.customer_id).with_for_update().first()
        if customer:
            customer.service_type = ServiceType.managed
            customer.subscription_active = True
            customer.subscription_start = project.start_date or today
            customer.subscription_end = project.subscription_end
        if project.prototype_id:
            from app.models.prototypes import Prototype
            from app.services.prototype_scheduler import schedule_prototype_tasks
            prototype = db.query(Prototype).filter(Prototype.id == project.prototype_id).first()
            if prototype and project.subscription_end:
                schedule_prototype_tasks(project, prototype, db, today, project.subscription_end, current_user.id)
    if project_type == ProjectType.lease:
        from app.models.agreements import Agreement, AgreementType, AgreementStatus
        from app.models.customers import Customer
        import json
        customer = db.query(Customer).filter(Customer.user_id == lead.customer_id).first()
        if not customer:
            raise HTTPException(status_code=400, detail="A registered landowner customer profile is required to create the lease agreement")
        start = lead.possession_date or today
        duration_months = lead.lease_duration_months or 12
        terms = {
            "lease_arrangement_type": lead.lease_arrangement_type,
            "commercial_model_type": lead.commercial_model_type,
            "settlement_base": lead.settlement_base,
            "fixed_lease_amount": lead.fixed_lease_amount,
            "revenue_share_percentage": lead.revenue_share_percentage,
            "payment_frequency": lead.payment_frequency,
            "landowner_responsibilities": lead.landowner_responsibilities,
            "company_responsibilities": lead.company_responsibilities,
            "termination_conditions": lead.termination_conditions,
        }
        db.add(Agreement(
            id=str(uuid.uuid4()), customer_id=customer.id, lead_id=lead.id, project_id=project.id, farm_id=project.farm_id,
            type=AgreementType.lease, start_date=start,
            end_date=start + timedelta(days=duration_months * 30),
            payment_terms=json.dumps(terms),
            amount=lead.fixed_lease_amount or amount,
            status=AgreementStatus.active,
            document_url=lead.agreement_url,
        ))
    if lead.type == LeadType.sell_land and lead.related_land_sale_id:
        from app.models.land_sales import LandSale, LandSaleStatus
        from app.models.work_orders import WorkOrder, WorkOrderType, WorkOrderStatus
        from app.models.brokers import Broker
        from app.models.customers import Customer
        from app.services.notification_service import notify_land_sale_listed
        land_sale = db.query(LandSale).filter(LandSale.id == lead.related_land_sale_id).with_for_update().first()
        if land_sale:
            existing_task = db.query(WorkOrder).filter(WorkOrder.lead_id == lead.id).first()
            if not existing_task:
                db.add(WorkOrder(
                    id=str(uuid.uuid4()), lead_id=lead.id, project_id=project.id,
                    type=WorkOrderType.land_sale_followup,
                    status=WorkOrderStatus.assigned if (lead.assigned_employee_id or lead.employee_id) else WorkOrderStatus.pending,
                    assigned_employee_id=lead.assigned_employee_id or lead.employee_id,
                    notes=f"Land sale follow-up and site coordination: {land_sale.area or 'Area TBD'} acres at {land_sale.location or 'Location TBD'}; asking ₹{land_sale.listed_price or 'TBD'}.",
                    created_by=current_user.id,
                ))
            if not land_sale.is_broadcasted:
                brokers = db.query(Broker).all()
                customers = db.query(Customer).filter(Customer.is_deleted == False).all()
                land_sale.broker_ids = [broker.id for broker in brokers]
                land_sale.status = LandSaleStatus.broadcast
                land_sale.is_broadcasted = True
                land_sale.broadcasted_at = datetime.utcnow()
                land_sale.broadcast_recipients_count = len(brokers) + len(customers)
                for recipient in customers:
                    notify_land_sale_listed(recipient.user_id, land_sale.location or "unspecified location", db)
                for broker in brokers:
                    if broker.user_id:
                        notify_land_sale_listed(broker.user_id, land_sale.location or "unspecified location", db)


def _authorize_lead(lead: Lead, user: User, allow_unassigned: bool = False) -> None:
    if user.role == UserRole.founder:
        return
    if user.role == UserRole.customer and lead.customer_id == user.id:
        return
    if user.role == UserRole.zone_admin:
        if (lead.branch_id is not None and lead.branch_id == user.branch_id) or (
            lead.branch_id is None and ((lead.zone_id is not None and lead.zone_id == user.zone_id) or (lead.zone_id is None and user.zone_id is None))
        ):
            return
    if user.role == UserRole.employee:
        if user.id in (lead.employee_id, lead.assigned_employee_id):
            return
        if allow_unassigned and lead.employee_id is None and lead.assigned_employee_id is None:
            same_branch = lead.branch_id is not None and lead.branch_id == user.branch_id
            same_zone = lead.branch_id is None and lead.zone_id is not None and lead.zone_id == user.zone_id
            unscoped = lead.branch_id is None and lead.zone_id is None and user.branch_id is None and user.zone_id is None
            if same_branch or same_zone or unscoped:
                return
    if user.role == UserRole.agri_officer and lead.assigned_ao_id == user.id:
        return
    raise HTTPException(404, "Lead not found")


def _match_public_lead_region(location: Optional[str], db: Session):
    """Match visitor-entered place names against configured zones/branches."""
    import re

    tokens = {word for word in re.findall(r"[a-z0-9]+", (location or "").casefold()) if len(word) >= 4}
    if not tokens:
        return None, None

    best_zone = None
    best_zone_score = 0
    for zone in db.query(Zone).all():
        branch = db.query(Branch).filter(Branch.id == zone.branch_id).first()
        labels = [zone.name, branch.name if branch else "", branch.location if branch else ""]
        score = max(
            (len(tokens & {word for word in re.findall(r"[a-z0-9]+", (label or "").casefold()) if len(word) >= 4}) for label in labels),
            default=0,
        )
        if score > best_zone_score:
            best_zone, best_zone_score = zone, score
    if best_zone:
        return best_zone.branch_id, best_zone.id

    best_branch = None
    best_branch_score = 0
    for branch in db.query(Branch).all():
        labels = [branch.name, branch.location]
        score = max(
            (len(tokens & {word for word in re.findall(r"[a-z0-9]+", (label or "").casefold()) if len(word) >= 4}) for label in labels),
            default=0,
        )
        if score > best_branch_score:
            best_branch, best_branch_score = branch, score
    return (best_branch.id, None) if best_branch else (None, None)


def _assign_lead_owner(lead: Lead, db: Session, creator: Optional[User] = None) -> None:
    if creator and creator.role == UserRole.employee:
        employee = creator
    else:
        query = db.query(User).filter(
            User.role == UserRole.employee,
            User.is_available == True,
            User.is_deleted == False,
        )
        if lead.zone_id:
            query = query.filter(User.zone_id == lead.zone_id)
            employee = query.order_by(User.created_at.asc()).first()
            if not employee and lead.branch_id:
                employee = db.query(User).filter(
                    User.role == UserRole.employee,
                    User.is_available == True,
                    User.is_deleted == False,
                    User.branch_id == lead.branch_id,
                ).order_by(User.created_at.asc()).first()
        elif lead.branch_id:
            employee = query.filter(User.branch_id == lead.branch_id).order_by(User.created_at.asc()).first()
        else:
            employee = query.order_by(User.created_at.asc()).first()
    if employee:
        lead.employee_id = employee.id
        lead.assigned_employee_id = employee.id
        if lead.branch_id is None:
            lead.branch_id = employee.branch_id
        if lead.zone_id is None:
            lead.zone_id = employee.zone_id
