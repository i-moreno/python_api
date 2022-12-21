from fastapi import HTTPException, status, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models
from ..schemas import PostBase, PostCreate, PostResponse
from ..database import get_db

router = APIRouter()

@router.get("/posts", response_model=List[PostResponse])
async def get_post(db: Session = Depends(get_db)):
  # cursor.execute("""SELECT * FROM posts""")
  # posts = cursor.fetchall()
  posts = db.query(models.Post).all()
  return posts


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(payload: PostCreate, db: Session = Depends(get_db)):
  # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (payload.title, payload.content, payload.published))
  # new_post = cursor.fetchone()
  # ** it's equal to -> title=payload.title, content=payload.content and so on
  new_post = models.Post(**payload.dict())
  db.add(new_post)  # Add the newly created post to db
  db.commit()  # Commit changes to db
  db.refresh(new_post)  # Retrieve and store the new post in new_post variable
  return new_post


@router.get("/posts/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
  # cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id)))
  # post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id).first()

  if not post:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

  return post


@router.put("/posts/{id}", response_model=PostResponse)
def update_post(id: int, payload: PostBase, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *  """, (payload.title, payload.content, payload.published, str(id)))
    # updated_post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id)

  if not post.first():
      raise HTTPException(status_code=404, detail="Post not found")

  post.update(payload.dict(), synchronize_session=False)
  db.commit()
  update_post = post.first()

  return update_post


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
  # cursor.execute(""" DELETE from posts WHERE id = %s RETURNING * """, (str(id)))
  # deleted_post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id)

  if not post.first():
      raise HTTPException(status_code=404, detail="Post not found")

  post.delete(synchronize_session=False)
  db.commit()
