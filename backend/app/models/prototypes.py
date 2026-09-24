from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Prototype(Base):
    __tablename__ = "prototypes"

    id = Column(String, primary_key=True, index=True)
    crop_name = Column(String, nullable=False)        # e.g., Rice, Banana
    total_duration_days = Column(Integer, nullable=False, default=120)
    project_type = Column(String, nullable=False)     # managed, lease, one_time
    water_schedule_days = Column(Integer, nullable=True, default=15)
    fertilizer_schedule_days = Column(Integer, nullable=True, default=25)
    ao_visit_schedule_days = Column(Integer, nullable=True, default=15)
    harvest_day = Column(Integer, nullable=True, default=120)
    description = Column(Text, nullable=True)
    created_by_ao_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    created_by_ao = relationship("User", foreign_keys=[created_by_ao_id])
