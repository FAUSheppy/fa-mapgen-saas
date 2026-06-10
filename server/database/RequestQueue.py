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

class RequestQueue(db.Model):
    __tablename__ = "request_queue"

    options = Column(String, primary_key=True)
    date = Column(Integer, primary_key=True)

    requester = Column(String)
    request_id = Column(String)
    count = Column(Integer)
    finished = Column(Boolean)
    state = Column(Integer)