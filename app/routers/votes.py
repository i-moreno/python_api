from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2
from ..database import get_db


router = APIRouter(prefix="/votes", tags=["Votes"])

@router.post("/", status_code=status.HTTP_200_OK)
async def vote_post(vote: schemas.Vote, db: Session = Depends(get_db), user = Depends(oauth2.get_current_user)):
  post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
  if not post:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post doesn't exist")

  query = db.query(models.Vote).filter(
    models.Vote.post_id == vote.post_id,
    models.Vote.user_id == user.id
    )

  found_vote = query.first()

  if vote.dir == 1 and found_vote:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already liked this post")

  if vote.dir == 1:
    new_vote =  models.Vote(post_id=vote.post_id, user_id = user.id)
    db.add(new_vote)
    db.commit()
    return {"message": "Vote added"}
  else:
    vote = query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Vote removed"}
