import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = Column(String, nullable=False, unique=True, index=True)
    customer_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True, index=True)
    quote_version_id = Column(String, ForeignKey("quote_versions.id"), nullable=False, unique=True)
    currency = Column(String(3), nullable=False, default="INR")
    subtotal_paise = Column(Integer, nullable=False)
    discount_paise = Column(Integer, nullable=False, default=0)
    tax_paise = Column(Integer, nullable=False, default=0)
    total_paise = Column(Integer, nullable=False)
    paid_paise = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="issued", index=True)
    notes = Column(Text, nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    due_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceLine.position")
    allocations = relationship("PaymentAllocation", back_populates="invoice")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    quantity_milli = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    unit_price_paise = Column(Integer, nullable=False)
    line_total_paise = Column(Integer, nullable=False)

    invoice = relationship("Invoice", back_populates="lines")


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"
    __table_args__ = (UniqueConstraint("payment_id", "invoice_id", name="uq_payment_invoice_allocation"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False, index=True)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False, index=True)
    amount_paise = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    invoice = relationship("Invoice", back_populates="allocations")
