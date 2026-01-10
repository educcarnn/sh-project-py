from sqlalchemy.orm import Session
from app.models.role import Role

class RoleRepository:

    def get_by_id(self, db: Session, role_id: int):
        return db.query(Role).filter(Role.id == role_id).first()
