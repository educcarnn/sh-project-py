from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role_id: int = Field(..., example=1, description="ID do role (1=Admin, 2=User, 3=Manager)")
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
    created_at: date
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True

class UserWithDetailsResponse(BaseModel):
    user_name: str
    user_email: str
    role_description: str
    claim_description: str
