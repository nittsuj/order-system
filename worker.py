from celery import Celery
from time import sleep
import os

broker_url= os.getenv('CELERY_BROKER_URL','redis://localhost:6379/0')
backend_url= os.getenv('CELERY_RESULT_BACKEND','redis://localhost:6379/0')

app = Celery("tasks",
             broker=broker_url,
             backend=backend_url)

@app.task
def processing_order(order_id: int):
    sleep(5)
    msg = f"Order #{order_id} Processed."
    print(msg)
    return msg
