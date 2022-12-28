from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# """ Connection using RAW SQL """
#       Database connection
# while True:
#   try:
#       connection = psycopg2.connect(host='localhost', database='',
#                                     user='postgres', password='', cursor_factory=RealDictCursor)
#       cursor = connection.cursor()
#       print("Database connected successfully")
#       break
#   except Exception as error:
#       print(f"Database connection failed {error}")
#       time.sleep(4)


# Database connection using SQL Alchemy
SQL_ALCHEMY_DB_URL = f'postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}/{settings.db_name}'
engine = create_engine(SQL_ALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
