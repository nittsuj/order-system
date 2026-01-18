from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from worker import processing_order
import schemas

router = APIRouter(
    prefix="orders",
    tags=["orders"]
)

@app.get("/", 
         response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.post("/", 
          response_model=schemas.OrderResponse, 
          status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == order.users_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_order = models.Order(status=order.status, users_id=order.users_id)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order
