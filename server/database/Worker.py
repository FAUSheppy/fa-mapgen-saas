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

class Worker(db.Model):

   __tablename__ = "workers"

   worker_id = Column(String, primary_key=True)
   last_seen = Column(Integer)
   supported_versions = Column(String)
   worker_type = Column(String)
