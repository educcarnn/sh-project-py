from sqlalchemy.orm import Session
from sqlalchemy import select
from models.user import User
from models.role import Role
from models.claim import Claim
from models.user_claims import UserClaim

class UserRepository:

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def find_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_user_with_role_and_claims(self, db: Session, user_id: int):
        stmt = (
            select(
                User.name.label("user_name"),
                User.email.label("user_email"),
                Role.description.label("role_description"),
                Claim.description.label("claim_description")
            )
            .join(Role, Role.id == User.role_id)
            .join(UserClaim, UserClaim.user_id == User.id)
            .join(Claim, Claim.id == UserClaim.claim_id)
            .where(User.id == user_id)
        )

        return db.execute(stmt).all()
