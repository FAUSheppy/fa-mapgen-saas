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

class Map(db.Model):
    __tablename__ = "maps"

    id = Column(String, primary_key=True)
    request_id = Column(String)

    options = relationship(
        "MapOptions",
        back_populates="map",
        uselist=False,
        cascade="all, delete-orphan",
    )

    votes = relationship(
        "MapVote",
        back_populates="map",
        cascade="all, delete-orphan",
    )
