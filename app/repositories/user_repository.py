from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role
from app.models.claim import Claim
from app.models.user_claims import UserClaim

class UserRepository:

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_user_with_role_and_claims(self, db: Session, user_id: int):
        stmt = (
            select(
                User.name,
                User.email,
                Role.description.label("role"),
                Claim.description.label("claim")
            )
            .join(Role, Role.id == User.role_id)
            .join(UserClaim, UserClaim.user_id == User.id)
            .join(Claim, Claim.id == UserClaim.claim_id)
            .where(User.id == user_id)
        )

        return db.execute(stmt).all()
