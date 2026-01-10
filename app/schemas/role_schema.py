from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    description: str

    class Config:
        orm_mode = True
