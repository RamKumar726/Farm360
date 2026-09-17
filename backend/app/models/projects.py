import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProjectType(str, enum.Enum):
    project_investment = "project_investment"
    agricultural_investment = "agricultural_investment"
    joint_project = "joint_project"


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    funded = "funded"
    active = "active"
    completed = "completed"
    settled = "settled"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SAEnum(ProjectType), nullable=False)
    total_amount = Column(Float, nullable=False)
    funded_amount = Column(Float, default=0.0)
    status = Column(SAEnum(ProjectStatus), nullable=False, default=ProjectStatus.draft)
    posted_by = Column(String, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    total_revenue = Column(Float, nullable=True)
    cover_image_url = Column(String, nullable=True)   # Cloudinary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    posted_by_user = relationship("User", foreign_keys=[posted_by])
    investments = relationship("Investment", back_populates="project")
