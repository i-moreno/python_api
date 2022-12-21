from fastapi import FastAPI

import psycopg2
from psycopg2.extras import RealDictCursor
import time

from . import models
from .database import engine
from .routers import posts, users, auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Database connection
while True:
    try:
        connection = psycopg2.connect(host='localhost', database='blog_api',
                                      user='postgres', password='itexico1', cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        print("Database connected successfully")
        break
    except Exception as error:
        print(f"Database connection failed {error}")
        time.sleep(4)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)



