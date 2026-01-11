from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import SessionLocal
from schemas.user_schema import UserCreate, UserResponse, UserWithDetailsResponse
from services.user_service import UserService
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        service = UserService(UserRepository())
        user = service.create_user(db=db, user=payload)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/details", response_model=list[UserWithDetailsResponse])
def get_user_details(user_id: int, db: Session = Depends(get_db)):
    repository = UserRepository()
    result = repository.get_user_with_role_and_claims(db, user_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [
        UserWithDetailsResponse(
            user_name=row.user_name,
            user_email=row.user_email,
            role_description=row.role_description,
            claim_description=row.claim_description
        )
        for row in result
    ]
