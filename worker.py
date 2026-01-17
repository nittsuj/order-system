from celery import Celery
from time import sleep

app = Celery("tasks",
             broker="redis://localhost:6379",
             backend="redis://localhost:6379")

@app.task
def processing_mail(email_address: str, order_id: int):
    sleep(5)
    msg = f"Order #{order_id} Processed."
    print(msg)
    return msg
