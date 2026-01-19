from celery import Celery
import models
from time import sleep
from database import SessionLocal
import os

broker_url= os.getenv('CELERY_BROKER_URL','redis://localhost:6379/0')
backend_url= os.getenv('CELERY_RESULT_BACKEND','redis://localhost:6379/0')

app = Celery("tasks",
             broker=broker_url,
             backend=backend_url)

@app.task
def processing_order(order_id: int):
    sleep(5)

    db = SessionLocal()
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if order:
            order.status = "completed"
            db.commit()
            return f"Order #{order_id} Completed and Status Updated."
        else:
            return f"Order #{order_id} not found."
            
    except Exception as e:
        return f"Error updating order: {str(e)}"
        
    finally:
        db.close()
