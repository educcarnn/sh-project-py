from sqlalchemy.orm import Session
from models.role import Role
from repositories.role_repository import RoleRepository

def seed_roles(db: Session):
    repository = RoleRepository()
    default_roles = ["ADMIN", "USER"]

    for role_name in default_roles:
        exists = repository.get_by_description(db, role_name)
        if not exists:
            repository.create(db, Role(description=role_name))
