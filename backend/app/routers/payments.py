import uuid
import hashlib
import hmac
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.config import RAZORPAY_KEY_ID, RAZORPAY_WEBHOOK_SECRET, FEATURE_INVESTMENTS, PAYMENT_MODE
from app.database import get_db
from app.models.finance import Payment, PaymentPurpose, PaymentStatus, PaymentWebhookEvent
from app.models.investments import Investment, InvestmentStatus, InvestmentVerificationStage
from app.models.leads import Lead, LeadStatus, LeadType
from app.models.work_orders import WorkOrder, WorkOrderStatus, WorkOrderType, PaymentStatus as WorkOrderPaymentStatus
from app.models.users import User, UserRole
from app.utils.razorpay_client import create_order, verify_payment_signature, fetch_payment
from app.models.quotes import QuoteVersion
from app.services.audit_service import record_audit
from app.models.billing import Invoice, PaymentAllocation

router = APIRouter(prefix="/payments", tags=["payments"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class PaymentConfirmation(BaseModel):
    gateway_order_id: str
    gateway_payment_id: str
    gateway_signature: str


def verify_webhook_signature(raw_body: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _new_order(user: User, purpose: PaymentPurpose, amount_rupees: float, db: Session, **refs):
    if not RAZORPAY_KEY_ID:
        raise HTTPException(status_code=503, detail="Online payments are not configured")
    paise = int(round(amount_rupees * 100))
    if paise <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")
    existing_query = db.query(Payment).filter(
        Payment.payer_user_id == user.id,
        Payment.purpose == purpose,
        Payment.amount_paise == paise,
        Payment.status == PaymentStatus.created,
    )
    for field, value in refs.items():
        existing_query = existing_query.filter(getattr(Payment, field) == value)
    existing = existing_query.order_by(Payment.created_at.desc()).first()
    if existing:
        return {"payment_id": existing.id, "key_id": RAZORPAY_KEY_ID,
                "order_id": existing.gateway_order_id, "amount": existing.amount_paise,
                "currency": "INR"}
    row_id = str(uuid.uuid4())
    try:
        order = create_order(paise, receipt=row_id.replace("-", "")[:40])
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Payment provider could not create an order") from exc
    payment = Payment(
        id=row_id, payer_user_id=user.id, purpose=purpose, amount_paise=paise, currency="INR",
        gateway_order_id=order["id"], **refs,
    )
    db.add(payment)
    db.commit()
    return {"payment_id": payment.id, "key_id": RAZORPAY_KEY_ID, "order_id": order["id"],
            "amount": paise, "currency": order.get("currency", "INR")}


@router.post("/leads/{lead_id}/order")
def create_lead_order(lead_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.is_deleted == False).with_for_update().first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    if user.role != UserRole.customer or lead.customer_id != user.id:
        raise HTTPException(403, "Only the customer on this lead can pay")
    if lead.status != LeadStatus.payment:
        raise HTTPException(400, "This lead is not ready for payment")
    accepted_quote = db.query(QuoteVersion).filter(
        QuoteVersion.lead_id == lead.id,
        QuoteVersion.status == "accepted",
    ).order_by(QuoteVersion.version_number.desc()).first()
    if not accepted_quote or not accepted_quote.acceptance or accepted_quote.acceptance.revoked:
        raise HTTPException(400, "An exact approved quote version must be accepted before payment")
    invoice = db.query(Invoice).filter(
        Invoice.quote_version_id == accepted_quote.id,
        Invoice.customer_user_id == user.id,
    ).with_for_update().first()
    if not invoice or invoice.status not in {"issued", "partially_paid"}:
        raise HTTPException(409, "No payable invoice is available for this quote")
    amount = accepted_quote.total_paise / 100
    purpose = PaymentPurpose.service_enquiry if lead.type == LeadType.service_enquiry else PaymentPurpose.lead
    if db.query(Payment).filter(Payment.payer_user_id == user.id, Payment.lead_id == lead.id, Payment.status == PaymentStatus.paid).first():
        raise HTTPException(409, "This lead has already been paid")
    return success(_new_order(user, purpose, amount, db, lead_id=lead.id, quote_version_id=accepted_quote.id, invoice_id=invoice.id))


@router.post("/investments/{investment_id}/order")
def create_investment_order(investment_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not FEATURE_INVESTMENTS:
        raise HTTPException(404, "Investments are coming soon")
    from app.models.customers import Customer
    customer = db.query(Customer).filter(Customer.user_id == user.id).first()
    if not customer or user.role != UserRole.customer:
        raise HTTPException(403, "Customer account required")
    investment = db.query(Investment).filter(Investment.id == investment_id, Investment.customer_id == customer.id).with_for_update().first()
    if not investment:
        raise HTTPException(404, "Investment interest not found")
    if investment.verification_stage != InvestmentVerificationStage.payment_gateway:
        raise HTTPException(400, "Investment approvals must be complete before payment")
    if investment.status != InvestmentStatus.pending:
        raise HTTPException(400, "This investment is not awaiting payment")
    if db.query(Payment).filter(Payment.payer_user_id == user.id, Payment.investment_id == investment.id, Payment.status == PaymentStatus.paid).first():
        raise HTTPException(409, "This investment has already been paid")
    amount = investment.proposed_amount or investment.amount
    return success(_new_order(user, PaymentPurpose.investment, amount, db, investment_id=investment.id))


def _apply_captured_payment(payment: Payment, gateway_payment_id: str, gateway_signature: str | None, db: Session) -> None:
    """Apply a verified captured payment and its business transition once."""
    if payment.status == PaymentStatus.paid:
        if payment.gateway_payment_id != gateway_payment_id:
            raise HTTPException(409, "Order was already confirmed with another payment")
        return
    payment.status = PaymentStatus.paid
    payment.gateway_payment_id = gateway_payment_id
    payment.gateway_signature = gateway_signature
    payment.paid_at = datetime.now(timezone.utc)
    payer = db.query(User).filter(User.id == payment.payer_user_id).first()
    if not payer:
        raise HTTPException(409, "Payment account no longer exists")
    if payment.purpose in (PaymentPurpose.lead, PaymentPurpose.service_enquiry):
        lead = db.query(Lead).filter(Lead.id == payment.lead_id).with_for_update().first()
        if not lead or lead.customer_id != payer.id or lead.status != LeadStatus.payment:
            raise HTTPException(409, "Lead state changed before payment confirmation")
        agreed_amount = lead.final_amount if lead.final_amount is not None else lead.price_to_complete
        if int(round((agreed_amount or 0) * 100)) != payment.amount_paise:
            raise HTTPException(409, "The payment order no longer matches the agreed quotation")
        lead.payment_confirmed_at = payment.paid_at
        if payment.purpose == PaymentPurpose.service_enquiry:
            work_order = db.query(WorkOrder).filter(WorkOrder.lead_id == lead.id).first()
            if not work_order:
                work_order = WorkOrder(
                    id=str(uuid.uuid4()), lead_id=lead.id, farm_id=None,
                    type=WorkOrderType.cleaning, status=WorkOrderStatus.pending,
                    notes=f"Customer service request: {lead.farm_details or lead.services_needed or 'Service enquiry'}",
                    created_by=lead.assigned_employee_id or lead.employee_id,
                    payment_status=WorkOrderPaymentStatus.paid,
                )
                db.add(work_order)
        else:
            # Payment closes a normal service lead and creates its linked project
            # in the same transaction. Service enquiries remain open until work
            # is accepted, then their work-order close route creates the project.
            from app.services.lead_service import transition_lead
            from app.routers.leads import _close_won_lead
            transition_lead(lead, LeadStatus.closed_won)
            _close_won_lead(lead, payer, db)
    elif payment.purpose == PaymentPurpose.investment:
        investment = db.query(Investment).filter(Investment.id == payment.investment_id).with_for_update().first()
        if not investment or investment.verification_stage != InvestmentVerificationStage.payment_gateway:
            raise HTTPException(409, "Investment approval changed before payment confirmation")
        if investment.status != InvestmentStatus.pending:
            raise HTTPException(409, "Investment is no longer awaiting payment")
        agreed_amount = investment.proposed_amount or investment.amount
        if int(round(agreed_amount * 100)) != payment.amount_paise:
            raise HTTPException(409, "The payment order no longer matches the approved investment amount")
        from app.models.projects import Project, ProjectStatus
        project = db.query(Project).filter(Project.id == investment.project_id).with_for_update().first()
        if not project:
            raise HTTPException(409, "Investment project no longer exists")
        available = project.total_amount - (project.funded_amount or 0)
        if agreed_amount > available:
            raise HTTPException(409, "The remaining project allocation changed; contact the FarmCare team")
        investment.amount = payment.amount_paise / 100
        investment.status = InvestmentStatus.active
        investment.verification_stage = InvestmentVerificationStage.completed
        project.funded_amount = (project.funded_amount or 0) + investment.amount
        if project.funded_amount >= project.total_amount:
            project.funded_amount = project.total_amount
            project.status = ProjectStatus.funded
        from app.services.investment_service import calculate_revenue_share, calculate_expected_return
        calculate_revenue_share(investment, db)
        investment.expected_return = calculate_expected_return(investment, project)
    record_audit(
        db, action="payment.captured", entity_type="payment", entity_id=payment.id,
        actor_user_id=payment.payer_user_id,
        changes={"gateway_order_id": payment.gateway_order_id, "gateway_payment_id": gateway_payment_id,
                 "amount_paise": payment.amount_paise, "currency": payment.currency},
    )
    if payment.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).with_for_update().first()
        if not invoice or invoice.customer_user_id != payment.payer_user_id:
            raise HTTPException(409, "Invoice ownership does not match this payment")
        allocation = db.query(PaymentAllocation).filter(
            PaymentAllocation.payment_id == payment.id,
            PaymentAllocation.invoice_id == invoice.id,
        ).first()
        if not allocation:
            allocated = min(payment.amount_paise, max(0, invoice.total_paise - invoice.paid_paise))
            db.add(PaymentAllocation(
                id=str(uuid.uuid4()), payment_id=payment.id,
                invoice_id=invoice.id, amount_paise=allocated,
            ))
            invoice.paid_paise += allocated
        invoice.status = "paid" if invoice.paid_paise >= invoice.total_paise else "partially_paid"


def _verify_provider_payment(payment: Payment, provider_payment: dict) -> None:
    if provider_payment.get("order_id") != payment.gateway_order_id:
        raise HTTPException(409, "Provider payment does not belong to this order")
    if provider_payment.get("status") != "captured" or not provider_payment.get("captured"):
        raise HTTPException(409, "Payment has not been captured by the provider")
    if int(provider_payment.get("amount") or 0) != payment.amount_paise:
        raise HTTPException(409, "Provider payment amount does not match the order")
    if provider_payment.get("currency") != payment.currency:
        raise HTTPException(409, "Provider payment currency does not match the order")


@router.post("/confirm")
def confirm_payment(body: PaymentConfirmation, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.gateway_order_id == body.gateway_order_id).with_for_update().first()
    if not payment:
        raise HTTPException(404, "Payment order not found")
    if payment.payer_user_id != user.id:
        raise HTTPException(403, "Payment order does not belong to this account")
    if not verify_payment_signature(body.gateway_order_id, body.gateway_payment_id, body.gateway_signature):
        raise HTTPException(400, "Payment signature verification failed")
    try:
        provider_payment = fetch_payment(body.gateway_payment_id)
    except Exception as exc:
        raise HTTPException(502, "Payment provider verification is temporarily unavailable") from exc
    _verify_provider_payment(payment, provider_payment)
    _apply_captured_payment(payment, body.gateway_payment_id, body.gateway_signature, db)
    db.commit()
    return success({"status": "paid", "payment_id": payment.id}, "Payment confirmed")


@router.post("/webhook", include_in_schema=False)
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(503, "Payment webhook is not configured")
    raw_body = await request.body()
    if not verify_webhook_signature(raw_body, x_razorpay_signature, RAZORPAY_WEBHOOK_SECRET):
        raise HTTPException(400, "Invalid webhook signature")
    payload_hash = hashlib.sha256(raw_body).hexdigest()
    event_id = x_razorpay_event_id or payload_hash
    existing = db.query(PaymentWebhookEvent).filter(PaymentWebhookEvent.id == event_id).first()
    if existing:
        return success({"duplicate": True, "processed": existing.processed})
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "Invalid webhook JSON") from exc

    event_type = str(payload.get("event") or "unknown")
    payment_entity = ((payload.get("payload") or {}).get("payment") or {}).get("entity") or {}
    refund_entity = ((payload.get("payload") or {}).get("refund") or {}).get("entity") or {}
    gateway_order_id = payment_entity.get("order_id")
    gateway_payment_id = payment_entity.get("id") or refund_entity.get("payment_id")
    event = PaymentWebhookEvent(
        id=event_id, event_type=event_type, payload_sha256=payload_hash,
        signature_valid=True, gateway_order_id=gateway_order_id,
        gateway_payment_id=gateway_payment_id,
    )
    db.add(event)
    db.flush()
    try:
        payment = None
        if gateway_order_id:
            payment = db.query(Payment).filter(Payment.gateway_order_id == gateway_order_id).with_for_update().first()
        elif gateway_payment_id:
            payment = db.query(Payment).filter(Payment.gateway_payment_id == gateway_payment_id).with_for_update().first()

        if event_type in {"payment.captured", "order.paid"}:
            if not payment:
                raise ValueError("No local payment order matches the captured payment")
            _verify_provider_payment(payment, payment_entity)
            _apply_captured_payment(payment, payment_entity["id"], x_razorpay_signature, db)
        elif event_type == "payment.failed" and payment and payment.status != PaymentStatus.paid:
            payment.status = PaymentStatus.failed
            record_audit(db, action="payment.failed", entity_type="payment", entity_id=payment.id,
                         changes={"gateway_payment_id": gateway_payment_id})
        elif event_type == "refund.processed" and payment:
            refunded = int(refund_entity.get("amount") or 0)
            payment.refunded_amount_paise = min(payment.amount_paise, payment.refunded_amount_paise + refunded)
            if payment.refunded_amount_paise >= payment.amount_paise:
                payment.status = PaymentStatus.refunded
            record_audit(db, action=event_type, entity_type="payment", entity_id=payment.id,
                         changes={"refund_paise": refunded, "total_refunded_paise": payment.refunded_amount_paise})
        event.processed = True
        event.processed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        event = PaymentWebhookEvent(
            id=event_id, event_type=event_type, payload_sha256=payload_hash,
            signature_valid=True, processed=False, processing_error=str(exc)[:2000],
            gateway_order_id=gateway_order_id, gateway_payment_id=gateway_payment_id,
        )
        db.merge(event)
        db.commit()
        raise HTTPException(409, "Webhook was authentic but could not be reconciled") from exc
    return success({"processed": True, "event": event_type})


@router.get("")
def list_payments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Payment)
    if user.role == UserRole.customer:
        query = query.filter(Payment.payer_user_id == user.id)
    elif user.role == UserRole.zone_admin:
        query = query.join(Lead, Payment.lead_id == Lead.id).filter(
            (Lead.branch_id == user.branch_id) if user.branch_id else (Lead.zone_id == user.zone_id)
        )
    elif user.role == UserRole.employee:
        query = query.join(Lead, Payment.lead_id == Lead.id).filter(
            (Lead.employee_id == user.id) | (Lead.assigned_employee_id == user.id)
        )
    elif user.role != UserRole.founder:
        raise HTTPException(403, "You cannot access payments")
    rows = query.order_by(Payment.created_at.desc()).limit(100).all()
    return success([{"id": p.id, "purpose": p.purpose.value, "amount": p.amount_paise / 100,
                     "currency": p.currency, "refunded_amount": p.refunded_amount_paise / 100,
                     "quote_version_id": p.quote_version_id, "payment_mode": PAYMENT_MODE,
                     "status": p.status.value, "lead_id": p.lead_id, "investment_id": p.investment_id,
                     "created_at": str(p.created_at), "paid_at": str(p.paid_at) if p.paid_at else None} for p in rows])
