import enum
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Float, Text, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base


class OutsourcingContractStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class OutsourcingContract(Base):
    __tablename__ = "outsourcing_contracts"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    partner_id = Column(String, ForeignKey("work_partners.id"), nullable=False)
    scope = Column(Text, nullable=False)
    terms = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    document_url = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(SAEnum(OutsourcingContractStatus), nullable=False, default=OutsourcingContractStatus.active)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
