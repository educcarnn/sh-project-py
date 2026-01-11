from models.user import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import date
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def _generate_password(self) -> str:
        return secrets.token_urlsafe(12)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password[:72])

    def create_user(self, db: Session, user: UserCreate):
        raw_password = user.password or self._generate_password()
        password_hash = self._hash_password(raw_password)

        db_user = User(
            name=user.name,
            email=user.email,
            role_id=user.role_id,
            password=password_hash,
            created_at=date.today(),
            updated_at=None
        )

        return self.repository.create(db, db_user)
