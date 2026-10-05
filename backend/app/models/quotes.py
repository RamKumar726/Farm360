import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class QuoteVersion(Base):
    __tablename__ = "quote_versions"
    __table_args__ = (UniqueConstraint("lead_id", "version_number", name="uq_quote_lead_version"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="draft", index=True)
    currency = Column(String(3), nullable=False, default="INR")
    subtotal_paise = Column(Integer, nullable=False)
    discount_paise = Column(Integer, nullable=False, default=0)
    tax_paise = Column(Integer, nullable=False, default=0)
    total_paise = Column(Integer, nullable=False)
    inclusions = Column(Text, nullable=True)
    exclusions = Column(Text, nullable=True)
    timeline_assumptions = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    superseded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan", order_by="QuoteItem.position")
    acceptance = relationship("QuoteAcceptance", back_populates="quote", uselist=False, cascade="all, delete-orphan")


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quote_version_id = Column(String, ForeignKey("quote_versions.id"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    quantity_milli = Column(Integer, nullable=False, default=1000)
    unit = Column(String, nullable=False, default="item")
    unit_price_paise = Column(Integer, nullable=False)
    line_total_paise = Column(Integer, nullable=False)
    internal_cost_paise = Column(Integer, nullable=True)

    quote = relationship("QuoteVersion", back_populates="items")


class QuoteAcceptance(Base):
    __tablename__ = "quote_acceptances"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quote_version_id = Column(String, ForeignKey("quote_versions.id"), nullable=False, unique=True)
    customer_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    accepted_total_paise = Column(Integer, nullable=False)
    accepted_terms_snapshot = Column(Text, nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revoked = Column(Boolean, nullable=False, default=False)

    quote = relationship("QuoteVersion", back_populates="acceptance")
