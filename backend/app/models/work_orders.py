import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Float, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WorkOrderType(str, enum.Enum):
    cleaning = "cleaning"
    securing = "securing"
    irrigation = "irrigation"
    electric = "electric"
    harvest = "harvest"
    soil_water_test = "soil_water_test"
    cropping = "cropping"
    land_leveling = "land_leveling"
    pruning = "pruning"
    fertilizer_pestcontrol = "fertilizer_pestcontrol"
    monitoring = "monitoring"
    construction = "construction"


class WorkOrderStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    partner_accepted = "partner_accepted"
    in_progress = "in_progress"
    completed = "completed"
    verified = "verified"
    failed = "failed"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    partial = "partial"
    paid = "paid"
    reduced = "reduced"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(String, primary_key=True, index=True)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False)
    agri_officer_id = Column(String, ForeignKey("users.id"), nullable=True)
    type = Column(SAEnum(WorkOrderType), nullable=False)
    status = Column(SAEnum(WorkOrderStatus), nullable=False, default=WorkOrderStatus.pending)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    outsourcing_partner_id = Column(String, ForeignKey("work_partners.id"), nullable=True)
    farm_employee_id = Column(String, ForeignKey("users.id"), nullable=True)
    payment_status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    farm = relationship("Farm", back_populates="work_orders")
    agri_officer = relationship("User", foreign_keys=[agri_officer_id])
    farm_employee = relationship("User", foreign_keys=[farm_employee_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    outsourcing_partner = relationship("WorkPartner", back_populates="work_orders")
    visits = relationship("Visit", back_populates="work_order")
    prescriptions = relationship("Prescription", back_populates="work_order")
