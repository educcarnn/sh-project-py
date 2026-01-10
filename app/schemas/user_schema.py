from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role_id: int
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
