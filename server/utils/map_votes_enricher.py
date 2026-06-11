from sqlalchemy import func, case

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from database.db_import import db
from database.User import User
from database.MapVote import MapVote
from database.Map import Map

def enrich_maps_with_votes(maps, user_id=None):
    if not maps:
        return maps

    map_ids = [m.id for m in maps]

    # Current user's votes
    user_votes = {}

    if user_id:
        user_votes = {
            vote.map_id: vote.vote
            for vote in (
                db.session.query(MapVote)
                .filter(
                    MapVote.user_id == user_id,
                    MapVote.map_id.in_(map_ids),
                )
                .all()
            )
        }

    # Like/dislike counts
    stats = {
        row.map_id: row
        for row in (
            db.session.query(
                MapVote.map_id,
                func.sum(
                    case((MapVote.vote == 1, 1), else_=0)
                ).label("likes"),
                func.sum(
                    case((MapVote.vote == -1, 1), else_=0)
                ).label("dislikes"),
            )
            .filter(MapVote.map_id.in_(map_ids))
            .group_by(MapVote.map_id)
            .all()
        )
    }

    # Users who liked the map
    liked_by = {}

    liked_votes = (
        db.session.query(MapVote)
        .join(User)
        .filter(
            MapVote.map_id.in_(map_ids),
            MapVote.vote == 1,
        )
        .all()
    )

    for vote in liked_votes:
        liked_by.setdefault(vote.map_id, []).append(vote.user)

    # Attach computed attributes
    for m in maps:
        m.user_vote = user_votes.get(m.id)

        s = stats.get(m.id)

        likes = s.likes if s else 0
        dislikes = s.dislikes if s else 0

        m.like_count = likes
        m.dislike_count = dislikes

        m.total = likes + dislikes
        m.like_ratio = int(likes * 100 / m.total) if m.total else 0

        m.liked_by = liked_by.get(m.id, [])

    return maps