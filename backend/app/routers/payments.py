import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.config import RAZORPAY_KEY_ID
from app.database import get_db
from app.models.finance import Payment, PaymentPurpose, PaymentStatus
from app.models.investments import Investment, InvestmentStatus, InvestmentVerificationStage
from app.models.leads import Lead, LeadStatus, LeadType
from app.models.work_orders import WorkOrder, WorkOrderStatus, WorkOrderType, PaymentStatus as WorkOrderPaymentStatus
from app.models.users import User, UserRole
from app.utils.razorpay_client import create_order, verify_payment_signature

router = APIRouter(prefix="/payments", tags=["payments"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class PaymentConfirmation(BaseModel):
    gateway_order_id: str
    gateway_payment_id: str
    gateway_signature: str


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
        id=row_id, payer_user_id=user.id, purpose=purpose, amount_paise=paise,
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
    amount = lead.final_amount if lead.final_amount is not None else lead.price_to_complete
    if not amount or amount <= 0:
        raise HTTPException(400, "No agreed payment amount is set")
    purpose = PaymentPurpose.service_enquiry if lead.type == LeadType.service_enquiry else PaymentPurpose.lead
    if db.query(Payment).filter(Payment.payer_user_id == user.id, Payment.lead_id == lead.id, Payment.status == PaymentStatus.paid).first():
        raise HTTPException(409, "This lead has already been paid")
    return success(_new_order(user, purpose, amount, db, lead_id=lead.id))


@router.post("/investments/{investment_id}/order")
def create_investment_order(investment_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
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


@router.post("/confirm")
def confirm_payment(body: PaymentConfirmation, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.gateway_order_id == body.gateway_order_id).with_for_update().first()
    if not payment:
        raise HTTPException(404, "Payment order not found")
    if payment.payer_user_id != user.id:
        raise HTTPException(403, "Payment order does not belong to this account")
    if payment.status == PaymentStatus.paid:
        if payment.gateway_payment_id != body.gateway_payment_id:
            raise HTTPException(409, "Order was already confirmed with another payment")
        return success({"status": "paid", "payment_id": payment.id}, "Payment already confirmed")
    if not verify_payment_signature(body.gateway_order_id, body.gateway_payment_id, body.gateway_signature):
        payment.status = PaymentStatus.failed
        db.commit()
        raise HTTPException(400, "Payment signature verification failed")

    payment.status = PaymentStatus.paid
    payment.gateway_payment_id = body.gateway_payment_id
    payment.gateway_signature = body.gateway_signature
    payment.paid_at = datetime.now(timezone.utc)
    if payment.purpose in (PaymentPurpose.lead, PaymentPurpose.service_enquiry):
        lead = db.query(Lead).filter(Lead.id == payment.lead_id).with_for_update().first()
        if not lead or lead.customer_id != user.id or lead.status != LeadStatus.payment:
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
            _close_won_lead(lead, user, db)
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
    db.commit()
    return success({"status": "paid", "payment_id": payment.id}, "Payment confirmed")


@router.get("")
def list_payments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Payment)
    if user.role == UserRole.customer:
        query = query.filter(Payment.payer_user_id == user.id)
    rows = query.order_by(Payment.created_at.desc()).limit(100).all()
    return success([{"id": p.id, "purpose": p.purpose.value, "amount": p.amount_paise / 100,
                     "status": p.status.value, "lead_id": p.lead_id, "investment_id": p.investment_id,
                     "created_at": str(p.created_at), "paid_at": str(p.paid_at) if p.paid_at else None} for p in rows])
