from fastapi import HTTPException, status, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, oauth2
from ..schemas import PostBase, PostCreate, PostResponse, PostWithVotes
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=List[PostWithVotes])
async def get_post(db: Session = Depends(get_db), user = Depends(oauth2.get_current_user), limit: int = 10, skip:int=0, search: Optional[str]=""):
  # cursor.execute("""SELECT * FROM posts""")
  # posts = cursor.fetchall()
  votes_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
  post_with_votes = votes_query.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

  return post_with_votes


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(payload: PostCreate, db: Session = Depends(get_db), user =  Depends(oauth2.get_current_user)):
  # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (payload.title, payload.content, payload.published))
  # new_post = cursor.fetchone()
  # ** it's equal to -> title=payload.title, content=payload.content and so on

  req_body = payload.dict()
  req_body["author_id"] = user.id

  new_post = models.Post(**req_body)
  db.add(new_post)  # Add the newly created post to db
  db.commit()  # Commit changes to db
  db.refresh(new_post)  # Retrieve and store the new post in new_post variable
  return new_post


@router.get("/{id}", response_model=PostWithVotes)
def get_post(id: int, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
  # cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id)))
  # post = cursor.fetchone()
  votes_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
  post = votes_query.filter(models.Post.id == id).first()

  if not post:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

  return post


@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, payload: PostBase, db: Session = Depends(get_db), user = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *  """, (payload.title, payload.content, payload.published, str(id)))
    # updated_post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id)

  if not post.first():
    raise HTTPException(status_code=404, detail="Post not found")

  if post.first().author_id != user.id:
    raise HTTPException(status_code=403, detail="Not authorized to perform this action")

  post.update(payload.dict(), synchronize_session=False)
  db.commit()
  update_post = post.first()

  return update_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user= Depends(oauth2.get_current_user)):
  # cursor.execute(""" DELETE from posts WHERE id = %s RETURNING * """, (str(id)))
  # deleted_post = cursor.fetchone()
  post = db.query(models.Post).filter(models.Post.id == id)

  if not post.first():
    raise HTTPException(status_code=404, detail="Post not found")

  if post.first().author_id != user.id:
    raise HTTPException(status_code=403, detail="Not authorized to perform this action")

  post.delete(synchronize_session=False)
  db.commit()
