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

class MapOptions(db.Model):
    __tablename__ = "map_options"

    map_id = Column(
        String,
        ForeignKey("maps.id", ondelete="CASCADE"),
        primary_key=True,
    )

    map_size = Column(Integer)
    spawn_count = Column(Integer)
    num_teams = Column(Integer)

    style = Column(String)
    terrain_symmetry = Column(String)
    texture_style = Column(String)
    terrain_style = Column(String)
    resource_style = Column(String)
    prop_style = Column(String)
    version = Column(String)

    reclaim_density = Column(Float)
    resource_density = Column(Float)

    map = relationship("Map", back_populates="options")