from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from core.database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)
