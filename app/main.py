from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi.params import Body

from typing import Optional
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy.orm import Session
from . import models
from . database import engine, get_db

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class Post(BaseModel):
    title: str
    content: str
    published: bool = False


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


@app.get("/posts")
async def get_post(db:Session = Depends(get_db)):
  # cursor.execute("""SELECT * FROM posts""")
  # posts = cursor.fetchall()
  posts = db.query(models.Post).all()
  return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(payload: Post, db: Session = Depends(get_db)):
  # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (payload.title, payload.content, payload.published))
  # new_post = cursor.fetchone()
  # ** it's equal to -> title=payload.title, content=payload.content and so on
  new_post = models.Post(**payload.dict())
  db.add(new_post) # Add the newly created post to db
  db.commit() # Commit changes to db
  db.refresh(new_post) # Retrieve and store the new post in new_post variable
  return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
  # cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id)))
  # post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id).first()

  if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

  return {"data": post}


@app.put("/posts/{id}")
def update_post(id: int, payload: Post, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *  """, (payload.title, payload.content, payload.published, str(id)))
    # updated_post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id)

  if not post.first():
      raise HTTPException(status_code=404, detail="Post not found")

  post.update(payload.dict(), synchronize_session=False)
  db.commit()
  update_post = post.first()

  return {"data": update_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
  # cursor.execute(""" DELETE from posts WHERE id = %s RETURNING * """, (str(id)))
  # deleted_post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id)

  if not post.first():
      raise HTTPException(status_code=404, detail="Post not found")

  post.delete(synchronize_session=False)
  db.commit()