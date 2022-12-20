from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from typing import Optional
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None


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
async def get_post():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()

    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(payload: Post):
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (payload.title, payload.content, payload.published))
    new_post = cursor.fetchone()
    connection.commit()

    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
  cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id)))
  post = cursor.fetchone()

  if not post:
      response.status_code = status.HTTP_404_NOT_FOUND

  return {"data": post}


@app.put("/posts/{id}")
def update_post(id: int, payload: Post):
    cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *  """, (payload.title, payload.content, payload.published, str(id)))
    updated_post = cursor.fetchone()
    connection.commit()

    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
  cursor.execute(""" DELETE from posts WHERE id = %s RETURNING * """, (str(id)))
  deleted_post = cursor.fetchone()
  connection.commit()

  if not deleted_post:
      raise HTTPException(status_code=404, detail="Post not found")
