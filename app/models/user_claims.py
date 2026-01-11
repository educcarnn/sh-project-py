from sqlalchemy import Column, Integer, ForeignKey, BigInteger
from core.database import Base

class UserClaim(Base):
    __tablename__ = "user_claims"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    claim_id = Column(BigInteger, ForeignKey("claims.id"), primary_key=True)
