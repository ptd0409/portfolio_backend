from app.db.base import Base
from sqlalchemy import Table, Column, Integer, ForeignKey

project_tag = Table(
    "project_tag",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
)