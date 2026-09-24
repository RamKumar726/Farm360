from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Proof(Base):
    __tablename__ = "proofs"

    id = Column(String, primary_key=True)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=False, index=True)
    image_url = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    submitted_by = Column(String, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_status = Column(String, nullable=False, default="submitted")

    work_order = relationship("WorkOrder", back_populates="proofs")
    submitter = relationship("User", foreign_keys=[submitted_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
