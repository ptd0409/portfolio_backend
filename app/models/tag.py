from app.db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.project_tag import project_tag

class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    projects = relationship("Project", secondary=project_tag, back_populates="tags")