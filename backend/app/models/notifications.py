import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NotificationType(str, enum.Enum):
    new_lead = "new_lead"
    work_order_created = "work_order_created"
    work_order_assigned = "work_order_assigned"
    work_order_completed = "work_order_completed"
    proof_submitted = "proof_submitted"
    payment_due = "payment_due"
    payment_received = "payment_received"
    prescription_sent = "prescription_sent"
    visit_scheduled = "visit_scheduled"
    investment_project_posted = "investment_project_posted"
    land_sale_listed = "land_sale_listed"
    partner_accepted = "partner_accepted"
    partner_rejected = "partner_rejected"
    visit_completed = "visit_completed"
    incident_reported = "incident_reported"
    approval_required = "approval_required"
    crop_health_update = "crop_health_update"
    revenue_credited = "revenue_credited"


class NotificationChannel(str, enum.Enum):
    in_app = "in_app"
    whatsapp = "whatsapp"
    both = "both"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(SAEnum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(SAEnum(NotificationChannel), nullable=False, default=NotificationChannel.both)
    sent_via_whatsapp = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
