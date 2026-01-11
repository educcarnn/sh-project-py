from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    description: str

    class Config:
        from_attributes = True
