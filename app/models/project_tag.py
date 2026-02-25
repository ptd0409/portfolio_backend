from app.db.base import Base
from sqlalchemy import Column, Integer, ForeignKey

class ProjectTag(Base):
    __tablename__ = "project_tag"
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)