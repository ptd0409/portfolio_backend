from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.base import Base;

class ContactMessage(Base):
    __tablename__ = "contact_message"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)