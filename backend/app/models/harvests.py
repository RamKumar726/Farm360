import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, Date, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class HarvestStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=True)
    crop_cycle_id = Column(String, ForeignKey("crop_cycles.id"), nullable=True)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    crop_name = Column(String, nullable=True)
    harvest_date = Column(Date, nullable=True)
    # Yield data
    yield_quantity = Column(Float, nullable=True)       # in kg / quintals
    yield_unit = Column(String, default="kg")
    market_price_per_unit = Column(Float, nullable=True)
    gross_revenue = Column(Float, nullable=True)        # yield × market_price
    buyer_name = Column(String, nullable=True)
    sale_reference = Column(String, nullable=True)
    is_revenue_received = Column(Boolean, nullable=False, default=False)
    revenue_payment_reference = Column(String, nullable=True)
    revenue_received_at = Column(DateTime(timezone=True), nullable=True)
    harvesting_cost = Column(Float, nullable=True)
    transport_cost = Column(Float, nullable=True)
    other_expenses = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)           # gross - all costs
    # Landowner settlement
    landowner_share_pct = Column(Float, nullable=True)  # percentage share agreed
    landowner_settlement_amount = Column(Float, nullable=True)
    status = Column(SAEnum(HarvestStatus), nullable=False, default=HarvestStatus.scheduled)
    notes = Column(Text, nullable=True)
    proof_photos = Column(Text, nullable=True)           # JSON list of Cloudinary URLs
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    project = relationship("Project", foreign_keys=[project_id])
    farm = relationship("Farm", foreign_keys=[farm_id])
    work_order = relationship("WorkOrder", foreign_keys=[work_order_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
