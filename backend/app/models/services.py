from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func
from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    subtitle = Column(Text, nullable=True)
    features = Column(JSON, nullable=False, default=list)
    steps = Column(JSON, nullable=False, default=list)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
