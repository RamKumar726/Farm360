import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class IssueStatus(str, enum.Enum):
    open = "open"
    under_review = "under_review"
    escalated = "escalated"
    resolved = "resolved"
    closed = "closed"


class IssueSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Issue(Base):
    __tablename__ = "issues"

    id = Column(String, primary_key=True, index=True)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=True)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    reported_by = Column(String, ForeignKey("users.id"), nullable=False)      # customer / farm employee
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)        # agri officer / employee
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(SAEnum(IssueSeverity), nullable=False, default=IssueSeverity.medium)
    status = Column(SAEnum(IssueStatus), nullable=False, default=IssueStatus.open)
    resolution_notes = Column(Text, nullable=True)
    photo_urls = Column(Text, nullable=True)    # JSON list of Cloudinary URLs
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    farm = relationship("Farm", foreign_keys=[farm_id])
    work_order = relationship("WorkOrder", foreign_keys=[work_order_id])
    project = relationship("Project", foreign_keys=[project_id])
    reporter = relationship("User", foreign_keys=[reported_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
