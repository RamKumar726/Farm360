import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LandType(str, enum.Enum):
    agricultural = "agricultural"
    residential = "residential"
    commercial = "commercial"
    industrial = "industrial"
    mixed = "mixed"


class LandSaleStatus(str, enum.Enum):
    draft = "draft"
    site_visit = "site_visit"
    quoted = "quoted"
    listed = "listed"
    broadcast = "broadcast"
    interested = "interested"
    agreement = "agreement"
    registered = "registered"
    sold = "sold"
    cancelled = "cancelled"


class LandSale(Base):
    __tablename__ = "land_sales"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    real_estate_user_id = Column(String, ForeignKey("real_estate_users.id"), nullable=True)
    land_type = Column(SAEnum(LandType), nullable=False)
    area = Column(Float, nullable=True)            # in acres/sqft
    location = Column(String, nullable=True)
    facing = Column(String, nullable=True)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    listed_price = Column(Float, nullable=True)
    status = Column(SAEnum(LandSaleStatus), nullable=False, default=LandSaleStatus.draft)
    broker_ids = Column(JSON, nullable=True)        # list of broker ids notified
    description = Column(Text, nullable=True)
    photos = Column(JSON, nullable=True)            # Cloudinary URLs
    listed_at = Column(DateTime(timezone=True), nullable=True)
    sold_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    customer = relationship("Customer", back_populates="land_sales")
    real_estate_user = relationship("RealEstateUser", back_populates="land_sales")
