from sqlalchemy.orm import Session
from models.role import Role

class RoleRepository:

    def get_by_id(self, db: Session, role_id: int):
        return db.query(Role).filter(Role.id == role_id).first()

    def get_by_description(self, db: Session, description: str):
        return (
            db.query(Role)
            .filter(Role.description == description)
            .first()
        )

    def create(self, db: Session, role: Role):
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
