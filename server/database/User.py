from database.db_import import db
import utils.curators

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
    is_curator = Column(Boolean)

    votes = relationship("MapVote", back_populates="user")

    @classmethod
    def get_or_create(cls, user_id):

        user = db.session.get(cls, user_id)

        if user is None:
            user = cls(id=user_id, name=user_id, is_curator=user_id in utils.curators.CURATORS)
            db.session.add(user)
            db.session.commit()

        return user

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_curator": self.is_curator
        }