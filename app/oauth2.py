from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from . import schemas, database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY
# Algorithm
# Expiration Time

SECRET_KEY = "959gfjks59s923ka94sls9549s9a9sk49aks90459skd94ks92kd04kas9023kjd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

  # Add expiration time
  to_encode.update({"exp": expire})

  encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  return encoded


def verify_access_token(token: str, credentials_exception):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    id: str = payload.get("user_id")

    if not id:
      raise credentials_exception

    token_data = {"id": id}
  except JWTError as e:
    print(e)
    raise credentials_exception

  return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Could not validate credentials",
    headers={"WWWW-Authenticate":"Bearer"}
    )

  token = verify_access_token(token, credentials_exception)
  user =  db.query(models.User).filter(models.User.id == token["id"]).first()

  return user
