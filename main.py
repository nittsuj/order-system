from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

import models
import schemas
from database import engine, SessionLocal, get_db

from typing import List
import time

from routes import products
# Issue: Docker tries to start web and db simultaneously,
# but db takes 5-10s
# this prevents crashing & errors
while True:
    try:
        models.Base.metadata.create_all(engine)
        print("SUCCESSFULL")
        break
    except OperationalError as e:
        print("TRYING")
        time.sleep(2)

app = FastAPI()

app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "System Order is Running"}
