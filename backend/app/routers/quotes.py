import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models.leads import Lead, LeadStatus
from app.models.quotes import QuoteAcceptance, QuoteItem, QuoteVersion
from app.models.users import User, UserRole
from app.models.billing import Invoice, InvoiceLine
from app.services.audit_service import record_audit

router = APIRouter(prefix="/quotes", tags=["quotes"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


def rupees_to_paise(value: Decimal) -> int:
    return int((value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class QuoteItemInput(BaseModel):
    description: str = Field(min_length=2, max_length=500)
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    unit: str = Field(min_length=1, max_length=50)
    unit_price: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    internal_cost: Optional[Decimal] = Field(default=None, ge=0, max_digits=14, decimal_places=2)


class QuoteCreate(BaseModel):
    items: list[QuoteItemInput] = Field(min_length=1)
    discount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    tax: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    inclusions: Optional[str] = None
    exclusions: Optional[str] = None
    timeline_assumptions: Optional[str] = None
    terms: Optional[str] = None
    valid_until: Optional[datetime] = None


def _authorize_lead(lead: Lead, user: User) -> None:
    if user.role == UserRole.founder:
        return
    if user.role == UserRole.customer and lead.customer_id == user.id:
        return
    if user.role == UserRole.zone_admin and (
        (lead.branch_id and lead.branch_id == user.branch_id)
        or (not lead.branch_id and lead.zone_id == user.zone_id)
    ):
        return
    if user.role == UserRole.employee and user.id in (lead.employee_id, lead.assigned_employee_id):
        return
    if user.role == UserRole.agri_officer and lead.assigned_ao_id == user.id:
        return
    raise HTTPException(404, "Lead not found")


def quote_to_dict(quote: QuoteVersion, include_internal: bool = False):
    result = {
        "id": quote.id,
        "lead_id": quote.lead_id,
        "version_number": quote.version_number,
        "status": quote.status,
        "currency": quote.currency,
        "subtotal": quote.subtotal_paise / 100,
        "discount": quote.discount_paise / 100,
        "tax": quote.tax_paise / 100,
        "total": quote.total_paise / 100,
        "inclusions": quote.inclusions,
        "exclusions": quote.exclusions,
        "timeline_assumptions": quote.timeline_assumptions,
        "terms": quote.terms,
        "valid_until": quote.valid_until.isoformat() if quote.valid_until else None,
        "accepted_at": quote.acceptance.accepted_at.isoformat() if quote.acceptance and not quote.acceptance.revoked else None,
        "items": [],
    }
    for item in quote.items:
        row = {
            "id": item.id,
            "description": item.description,
            "quantity": item.quantity_milli / 1000,
            "unit": item.unit,
            "unit_price": item.unit_price_paise / 100,
            "line_total": item.line_total_paise / 100,
        }
        if include_internal:
            row["internal_cost"] = item.internal_cost_paise / 100 if item.internal_cost_paise is not None else None
        result["items"].append(row)
    return result


@router.get("/leads/{lead_id}")
def list_lead_quotes(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.is_deleted == False).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user)
    query = db.query(QuoteVersion).filter(QuoteVersion.lead_id == lead.id)
    if current_user.role == UserRole.customer:
        query = query.filter(QuoteVersion.status.in_(["sent", "accepted", "superseded"]))
    rows = query.order_by(QuoteVersion.version_number.desc()).all()
    include_internal = current_user.role != UserRole.customer
    return success([quote_to_dict(row, include_internal) for row in rows])


@router.post("/leads/{lead_id}/versions")
def create_quote_version(
    lead_id: str,
    body: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer)),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.is_deleted == False).with_for_update().first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    _authorize_lead(lead, current_user)

    previous = db.query(QuoteVersion).filter(QuoteVersion.lead_id == lead.id).order_by(QuoteVersion.version_number.desc()).first()
    version_number = (previous.version_number if previous else 0) + 1
    subtotal_paise = 0
    item_rows = []
    for position, item in enumerate(body.items, start=1):
        quantity_milli = int((item.quantity * Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        unit_price_paise = rupees_to_paise(item.unit_price)
        line_total_paise = int((Decimal(quantity_milli) * Decimal(unit_price_paise) / Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        subtotal_paise += line_total_paise
        item_rows.append((position, item, quantity_milli, unit_price_paise, line_total_paise))

    discount_paise = rupees_to_paise(body.discount)
    tax_paise = rupees_to_paise(body.tax)
    total_paise = subtotal_paise - discount_paise + tax_paise
    if discount_paise > subtotal_paise or total_paise <= 0:
        raise HTTPException(400, "Quote total must be positive and discount cannot exceed subtotal")

    if previous and previous.status == "accepted":
        from app.models.finance import Payment, PaymentStatus
        paid = db.query(Payment.id).filter(Payment.quote_version_id == previous.id, Payment.status == PaymentStatus.paid).first()
        if paid:
            raise HTTPException(409, "A paid quote cannot be revised; create a separately approved change order")
        if previous.acceptance:
            previous.acceptance.revoked = True
    if previous and previous.status in {"approved", "sent", "accepted"}:
        previous.status = "superseded"
        previous.superseded_at = datetime.now(timezone.utc)

    quote = QuoteVersion(
        id=str(uuid.uuid4()), lead_id=lead.id, version_number=version_number,
        subtotal_paise=subtotal_paise, discount_paise=discount_paise,
        tax_paise=tax_paise, total_paise=total_paise,
        inclusions=body.inclusions, exclusions=body.exclusions,
        timeline_assumptions=body.timeline_assumptions, terms=body.terms,
        valid_until=body.valid_until, created_by=current_user.id,
    )
    db.add(quote)
    db.flush()
    for position, item, quantity_milli, unit_price_paise, line_total_paise in item_rows:
        db.add(QuoteItem(
            id=str(uuid.uuid4()), quote_version_id=quote.id, position=position,
            description=item.description, quantity_milli=quantity_milli, unit=item.unit,
            unit_price_paise=unit_price_paise, line_total_paise=line_total_paise,
            internal_cost_paise=rupees_to_paise(item.internal_cost) if item.internal_cost is not None else None,
        ))
    record_audit(db, action="quote.created", entity_type="quote", entity_id=quote.id,
                 actor_user_id=current_user.id, changes={"lead_id": lead.id, "version": version_number, "total_paise": total_paise})
    db.commit()
    db.refresh(quote)
    return success(quote_to_dict(quote, True), "Quote version created")


@router.post("/{quote_id}/approve")
def approve_quote(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    quote = db.query(QuoteVersion).filter(QuoteVersion.id == quote_id).with_for_update().first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    _authorize_lead(db.query(Lead).filter(Lead.id == quote.lead_id).first(), current_user)
    if quote.status != "draft":
        raise HTTPException(409, "Only a draft quote can be approved")
    if quote.created_by == current_user.id:
        raise HTTPException(403, "The quote creator cannot approve their own quote")
    quote.status = "approved"
    quote.approved_by = current_user.id
    quote.approved_at = datetime.now(timezone.utc)
    record_audit(db, action="quote.approved", entity_type="quote", entity_id=quote.id, actor_user_id=current_user.id)
    db.commit()
    return success(quote_to_dict(quote, True), "Quote approved")


@router.post("/{quote_id}/send")
def send_quote(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin, UserRole.employee)),
):
    quote = db.query(QuoteVersion).filter(QuoteVersion.id == quote_id).with_for_update().first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    lead = db.query(Lead).filter(Lead.id == quote.lead_id).first()
    _authorize_lead(lead, current_user)
    if quote.status != "approved":
        raise HTTPException(409, "Only an approved quote can be sent")
    if not lead.customer_id:
        raise HTTPException(400, "Link or register the customer before sending the quote")
    quote.status = "sent"
    quote.sent_at = datetime.now(timezone.utc)
    lead.sent_to_client = True
    record_audit(db, action="quote.sent", entity_type="quote", entity_id=quote.id, actor_user_id=current_user.id)
    db.commit()
    return success(quote_to_dict(quote, True), "Quote sent to customer")


@router.post("/{quote_id}/accept")
def accept_quote(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.customer)),
):
    quote = db.query(QuoteVersion).filter(QuoteVersion.id == quote_id).with_for_update().first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    lead = db.query(Lead).filter(Lead.id == quote.lead_id).with_for_update().first()
    _authorize_lead(lead, current_user)
    latest = db.query(func.max(QuoteVersion.version_number)).filter(QuoteVersion.lead_id == lead.id).scalar()
    if quote.version_number != latest or quote.status != "sent":
        raise HTTPException(409, "This quote version is no longer eligible for acceptance")
    valid_until = quote.valid_until
    if valid_until and valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=timezone.utc)
    if valid_until and valid_until < datetime.now(timezone.utc):
        raise HTTPException(409, "This quote has expired")
    if quote.acceptance:
        return success(quote_to_dict(quote), "Quote already accepted")

    db.add(QuoteAcceptance(
        id=str(uuid.uuid4()), quote_version_id=quote.id,
        customer_user_id=current_user.id, accepted_total_paise=quote.total_paise,
        accepted_terms_snapshot=quote.terms,
    ))
    quote.status = "accepted"
    lead.final_amount = quote.total_paise / 100
    lead.price_to_complete = quote.total_paise / 100
    lead.status = LeadStatus.payment
    invoice = Invoice(
        id=str(uuid.uuid4()),
        invoice_number=f"FC-{datetime.now(timezone.utc).year}-{quote.id[:8].upper()}",
        customer_user_id=current_user.id,
        lead_id=lead.id,
        quote_version_id=quote.id,
        currency=quote.currency,
        subtotal_paise=quote.subtotal_paise,
        discount_paise=quote.discount_paise,
        tax_paise=quote.tax_paise,
        total_paise=quote.total_paise,
        status="issued",
        notes="Generated from accepted quotation. Tax treatment remains subject to configured accounting policy.",
    )
    db.add(invoice)
    db.flush()
    for item in quote.items:
        db.add(InvoiceLine(
            id=str(uuid.uuid4()), invoice_id=invoice.id, position=item.position,
            description=item.description, quantity_milli=item.quantity_milli, unit=item.unit,
            unit_price_paise=item.unit_price_paise, line_total_paise=item.line_total_paise,
        ))
    record_audit(db, action="quote.accepted", entity_type="quote", entity_id=quote.id,
                 actor_user_id=current_user.id, changes={"accepted_total_paise": quote.total_paise, "invoice_id": invoice.id})
    db.commit()
    db.refresh(quote)
    return success(quote_to_dict(quote), "Quote accepted; payment can now be initiated")
