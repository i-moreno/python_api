from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import posts, users, votes, auth
from .config import settings

# Since we are using alembic for migrations
# we can autogenerate tables from models module, so we don't need this command anymore
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allowed origins
origins = ["*"]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(votes.router)
app.include_router(auth.router)



