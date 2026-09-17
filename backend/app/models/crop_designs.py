import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class CropDesign(Base):
    __tablename__ = "crop_designs"

    id = Column(String, primary_key=True, index=True)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False)
    agri_officer_id = Column(String, ForeignKey("users.id"), nullable=False)
    best_practices = Column(Text, nullable=True)
    land_suitability = Column(Text, nullable=True)
    timing = Column(Text, nullable=True)
    crop_time = Column(Text, nullable=True)
    estimated_yearly_cost = Column(Float, nullable=True)
    intercrop_design = Column(Text, nullable=True)
    recommended_machines = Column(Text, nullable=True)
    research_notes = Column(Text, nullable=True)
    approval_status = Column(SAEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.pending)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    farm = relationship("Farm", back_populates="crop_designs")
    agri_officer = relationship("User", foreign_keys=[agri_officer_id])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    crop_cycles = relationship("CropCycle", back_populates="crop_design")
