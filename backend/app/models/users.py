import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserRole(str, enum.Enum):
    founder = "founder"
    zone_admin = "zone_admin"
    employee = "employee"
    agri_officer = "agri_officer"
    farm_employee = "farm_employee"
    customer = "customer"
    real_estate = "real_estate"
    broker = "broker"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.customer)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    is_available = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    branch = relationship("Branch", back_populates="users", foreign_keys=[branch_id])
    zone = relationship("Zone", back_populates="users", foreign_keys=[zone_id])
    notifications = relationship("Notification", back_populates="user")
    attendance_records = relationship("Attendance", back_populates="user", foreign_keys="Attendance.user_id")
