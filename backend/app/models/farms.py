from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    location = Column(String, nullable=True)
    area = Column(Float, nullable=True)          # in acres
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    soil_type = Column(String, nullable=True)
    water_source = Column(String, nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    customer = relationship("Customer", back_populates="farms")
    zone = relationship("Zone", back_populates="farms")
    agreements = relationship("Agreement", back_populates="farm")
    work_orders = relationship("WorkOrder", back_populates="farm")
    prescriptions = relationship("Prescription", back_populates="farm")
    crop_designs = relationship("CropDesign", back_populates="farm")
    crop_cycles = relationship("CropCycle", back_populates="farm")
    visits = relationship("Visit", back_populates="farm")
