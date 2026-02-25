from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    cover_image_url = Column(String, nullable=True)
    repo_url = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())
    tags = relationship(Tags, )