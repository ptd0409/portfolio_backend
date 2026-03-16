from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=5000)

class ContactRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }