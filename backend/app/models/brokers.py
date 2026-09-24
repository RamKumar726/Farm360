from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Broker(Base):
    __tablename__ = "brokers"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, unique=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    assigned_by = Column(String, ForeignKey("users.id"), nullable=True)
    specializations = Column(JSON, nullable=True)   # e.g. ["agricultural", "residential"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    zone = relationship("Zone", back_populates="brokers")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    user = relationship("User", foreign_keys=[user_id])
