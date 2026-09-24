import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProjectType(str, enum.Enum):
    project_investment = "project_investment"
    agricultural_investment = "agricultural_investment"
    joint_project = "joint_project"
    one_time_service = "one_time_service"
    managing_farm = "managing_farm"
    lease = "lease"
    land_sale = "land_sale"


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    funded = "funded"
    active = "active"
    not_started = "not_started"
    started = "started"
    in_progress = "in_progress"
    almost_completed = "almost_completed"
    completed = "completed"
    settled = "settled"


class ProjectApprovalStatus(str, enum.Enum):
    pending_approval = "pending_approval"
    approved = "approved"
    rejected = "rejected"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SAEnum(ProjectType), nullable=False)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=True)   # The farm this project operates on
    customer_id = Column(String, ForeignKey("users.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    funded_amount = Column(Float, default=0.0)
    minimum_investment = Column(Float, nullable=False, default=150000.0)
    status = Column(SAEnum(ProjectStatus), nullable=False, default=ProjectStatus.draft)
    approval_status = Column(SAEnum(ProjectApprovalStatus), nullable=False, default=ProjectApprovalStatus.approved)
    posted_by = Column(String, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    crop_name = Column(String, nullable=True)
    subscription_end = Column(Date, nullable=True)
    assigned_ao_id = Column(String, ForeignKey("users.id"), nullable=True)
    prototype_id = Column(String, ForeignKey("prototypes.id"), nullable=True)

    # Financial breakdown & Commercial Model
    commercial_model_type = Column(String, nullable=True) # fixed_lease, fixed_plus_percentage, percentage_share
    fixed_lease_amount = Column(Float, default=0.0)
    revenue_share_percentage = Column(Float, default=0.0)
    settlement_base = Column(String, nullable=True) # revenue, net_realization, defined_profit
    total_revenue = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    landowner_settlement = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)

    cover_image_url = Column(String, nullable=True)   # Cloudinary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    lead = relationship("Lead", foreign_keys=[lead_id])
    farm = relationship("Farm", foreign_keys=[farm_id])
    customer = relationship("User", foreign_keys=[customer_id])
    assigned_ao = relationship("User", foreign_keys=[assigned_ao_id])
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    investments = relationship("Investment", back_populates="project")
