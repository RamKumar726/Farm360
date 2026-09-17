from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=False)
    responsible_employee_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    branch = relationship("Branch", back_populates="zones")
    responsible_employee = relationship("User", foreign_keys=[responsible_employee_id])
    users = relationship("User", back_populates="zone", foreign_keys="User.zone_id")
    leads = relationship("Lead", back_populates="zone")
    farms = relationship("Farm", back_populates="zone")
    brokers = relationship("Broker", back_populates="zone")
    work_partners = relationship("WorkPartner", back_populates="zone")
    attendance_records = relationship("Attendance", back_populates="zone")
