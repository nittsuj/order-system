from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from worker import processing_order
import schemas

router = APIRouter(
    prefix="users",
    tags=["users"]
)

@router.post("/",
          response_model=schemas.UserResponse,
          status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(get_db)):
    user_exist = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/",
         response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users
