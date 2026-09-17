import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Integer, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class InvestmentType(str, enum.Enum):
    project = "project"
    agricultural = "agricultural"
    joint_project = "joint_project"


class InvestmentStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    locked = "locked"
    completed = "completed"
    settled = "settled"


class Investment(Base):
    __tablename__ = "investments"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    type = Column(SAEnum(InvestmentType), nullable=False)
    amount = Column(Float, nullable=False)
    bond_period = Column(Integer, nullable=True)   # in months
    status = Column(SAEnum(InvestmentStatus), nullable=False, default=InvestmentStatus.pending)
    revenue_share_percentage = Column(Float, nullable=True)
    expected_return = Column(Float, nullable=True)
    actual_return = Column(Float, nullable=True)
    settlement_date = Column(Date, nullable=True)
    agreement_url = Column(String, nullable=True)  # Cloudinary URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    project = relationship("Project", back_populates="investments")
    customer = relationship("Customer", back_populates="investments")
