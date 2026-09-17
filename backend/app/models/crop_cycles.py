from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id = Column(String, primary_key=True, index=True)
    crop_design_id = Column(String, ForeignKey("crop_designs.id"), nullable=False)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False)
    cycle_name = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    auto_generated = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    crop_design = relationship("CropDesign", back_populates="crop_cycles")
    farm = relationship("Farm", back_populates="crop_cycles")
