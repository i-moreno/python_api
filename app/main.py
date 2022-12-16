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
                                  user='postgres', password='', cursor_factory=RealDictCursor)
    cursor = connection.cursor()
    print("Database connected successfully")
    break
  except Exception as error:
    print(f"Database connection failed {error}")
    time.sleep(4)

# Storing post inside a List for demo purposes
my_posts = [
  {"id":1, "title": "Post A", "content": "Great post to be honest"},
  {"id":2, "title": "Post B", "content": "Medium post to be honest"},
  ]


def find_post(post_id):
  for idx, post in enumerate(my_posts):
    if post["id"] == int(post_id):
      return [idx, post]
  return None


@app.get("/posts")
async def get_post():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(payload:Post):
  post = payload.dict()
  post["id"] = randrange(0, 10000)
  my_posts.append(post)
  return{"data":post}


@app.get("/posts/{id}")
def get_post(id:int, response: Response):
  _, post = find_post(id)

  if not post:
    response.status_code = status.HTTP_404_NOT_FOUND

  return{"data": post}


@app.put("/posts/{id}")
def update_post(id: int, payload: Post):
  idx, post = find_post(id)
  if not post:
    raise HTTPException(status_code=404, detail="Post not found")

  post_dict = payload.dict()
  post_dict["id"] = id
  my_posts[idx] = post_dict
  return {"data": post_dict}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
  _, post = find_post(id)
  if not post:
    raise HTTPException(status_code=404, detail="Post not found")

  my_posts[:] = (post for post in my_posts if post["id"] != int(id))

  return {"data": my_posts}
