from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from worker import processing_order

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

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
