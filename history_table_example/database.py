from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine("postgresql+psycopg2://user:password@0.0.0.0:5432/postgres")
SessionLocal = sessionmaker(bind=engine)


class BaseModel(DeclarativeBase):
    pass
