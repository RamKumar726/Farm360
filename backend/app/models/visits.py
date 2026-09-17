import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class VisitType(str, enum.Enum):
    new_lead_visit = "new_lead_visit"
    auto_visit = "auto_visit"
    assign_visit = "assign_visit"
    sale_visit = "sale_visit"
    random_visit = "random_visit"


class VisitStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class Visit(Base):
    __tablename__ = "visits"

    id = Column(String, primary_key=True, index=True)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=True)
    farm_employee_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(SAEnum(VisitType), nullable=False)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    proof_photos = Column(JSON, nullable=True)    # list of Cloudinary URLs
    proof_video_url = Column(String, nullable=True)
    status = Column(SAEnum(VisitStatus), nullable=False, default=VisitStatus.pending)
    notes = Column(Text, nullable=True)
    visited_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    work_order = relationship("WorkOrder", back_populates="visits")
    farm_employee = relationship("User", foreign_keys=[farm_employee_id])
    farm = relationship("Farm", back_populates="visits")
