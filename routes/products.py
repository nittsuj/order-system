import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from worker import processing_order
import schemas

import redis

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# connects to redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

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

# READ ALL
@router.get("/", 
         response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# READ ONE
@router.get("/{product_id}",
            response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session=Depends(get_db)):
    cache_key = f"product_{product_id}"
    cached_product = redis_client.get(cache_key)

    if cached_product:
        print(f"CACHE HIT: Product #{product_id} taken from Redis")
        return json.loads(cached_product)
    
    print(f"CACHE MISS: Product #{product_id} taken from DB")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_dict = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
    }
    
    redis_client.set(cache_key, json.dumps(product_dict), ex=60)
    
    return product

@router.put("/{product_id}",
            response_model=schemas.ProductResponse)
def update_product(product_id: int, product_update: schemas.ProductCreate, db: Session=Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = product_update.name
    product.price = product_update.price
    product.stock = product_update.stock
    
    db.commit()
    db.refresh(product)
    
    # Implement Redis: Delete old cache
    cache_key = f"product_{product_id}"
    redis_client.delete(cache_key)
    print(f"Cache for Product #{product_id} has been Updated")

    return product

@router.delete("/{product_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    
    # Implement Redis: Delete old cache
    cache_key = f"product_{product_id}"
    redis_client.delete(cache_key)
    print(f"Cache for Product #{product_id} has been Deleted")

    return None

@router.post("/buy/{product_id}")
def buy_product(product_id: int, db: Session = Depends(get_db)):
    # Database Locking, to solve race condition
    product = db.query(models.Product).filter(models.Product.id == product_id).with_for_update().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock > 0:    
        product.stock -= 1
        db.commit()
        db.refresh(product)
            
        # Implement Redis: Delete old cache
        cache_key = f"product_{product_id}"
        redis_client.delete(cache_key)

        processing_order.delay(order_id=product.id)
        
        return {
            "status": "success", 
            "message": "Order placed! Processing in background.",
            "remaining_stock": product.stock
        }
    
    else:
        return {"status": "failed", 
                "message": "Out of stock!"}
