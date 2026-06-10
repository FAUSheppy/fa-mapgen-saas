from database.db_import import db
from database.User import User
from database.Map import Map


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

class MapVote(db.Model):
    __tablename__ = "map_votes"

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    map_id = Column(
        String,
        ForeignKey("maps.id", ondelete="CASCADE"),
        primary_key=True,
    )

    vote = Column(SmallInteger, nullable=False)  # 1 = like, -1 = dislike

    updated_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="votes")
    map = relationship("Map", back_populates="votes")

    def to_dict(self):

        return {
            "user_id": self.user_id,
            "map_id": self.map_id,
            "vote": self.vote,
            "updated_at": self.updated_at
        }