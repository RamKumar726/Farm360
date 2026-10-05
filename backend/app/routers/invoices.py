from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.billing import Invoice
from app.models.leads import Lead
from app.models.users import User, UserRole

router = APIRouter(prefix="/invoices", tags=["invoices"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


def _scope_invoices(query, user: User):
    if user.role == UserRole.founder:
        return query
    if user.role == UserRole.customer:
        return query.filter(Invoice.customer_user_id == user.id)
    if user.role == UserRole.zone_admin:
        return query.join(Lead, Invoice.lead_id == Lead.id).filter(
            (Lead.branch_id == user.branch_id) if user.branch_id else (Lead.zone_id == user.zone_id)
        )
    if user.role == UserRole.employee:
        return query.join(Lead, Invoice.lead_id == Lead.id).filter(
            (Lead.employee_id == user.id) | (Lead.assigned_employee_id == user.id)
        )
    raise HTTPException(403, "You cannot access invoices")


def invoice_to_dict(invoice: Invoice):
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "lead_id": invoice.lead_id,
        "quote_version_id": invoice.quote_version_id,
        "currency": invoice.currency,
        "subtotal": invoice.subtotal_paise / 100,
        "discount": invoice.discount_paise / 100,
        "tax": invoice.tax_paise / 100,
        "total": invoice.total_paise / 100,
        "paid": invoice.paid_paise / 100,
        "balance": max(0, invoice.total_paise - invoice.paid_paise) / 100,
        "status": invoice.status,
        "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
        "due_at": invoice.due_at.isoformat() if invoice.due_at else None,
        "lines": [{
            "id": line.id,
            "description": line.description,
            "quantity": line.quantity_milli / 1000,
            "unit": line.unit,
            "unit_price": line.unit_price_paise / 100,
            "line_total": line.line_total_paise / 100,
        } for line in invoice.lines],
    }


@router.get("")
def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_invoices(db.query(Invoice), current_user)
    total = query.count()
    rows = query.order_by(Invoice.issued_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success({"total": total, "items": [invoice_to_dict(row) for row in rows]})


@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = _scope_invoices(db.query(Invoice).filter(Invoice.id == invoice_id), current_user).first()
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return success(invoice_to_dict(invoice))
