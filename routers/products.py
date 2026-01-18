from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from worker import processing_order
import schemas

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", 
          response_model=schemas.ProductResponse, 
          status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=product.name,
        price=product.price,
        stock=product.stock
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/", 
         response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.post("/buy/{product_id}")
def buy_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).with_for_update().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock > 0:    
        product.stock -= 1
        db.commit()
        db.refresh(product)
        
        process_order.delay(order_id=product.id) # Tetap sama
        
        return {
            "status": "success", 
            "message": "Order placed! Processing in background.",
            "remaining_stock": product.stock
        }
    
    else:
        return {"status": "failed", "message": "Out of stock!"}
