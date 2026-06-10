from database.db_import import db

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    SmallInteger,
    DateTime,
    String,
    create_engine,
    select,
    ForeignKey,
    Float
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

class User(db.Model):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # OIDC subject
    name = Column(String)

    votes = relationship("MapVote", back_populates="user")