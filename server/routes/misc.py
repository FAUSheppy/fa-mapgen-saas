
import flask
from flask import Blueprint, jsonify

from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload

import datetime
import json
import uuid

from database.db_import import db
from database.RequestQueue import RequestQueue
from database.MapVote import MapVote
from database.Map import Map
from database.User import User

import utils.flask_wrappers
import utils.curators

bp = Blueprint("misc", __name__)

@bp.route("/queue", methods=["GET"])
def get_queue_size():
    count = db.session.query(RequestQueue).filter(RequestQueue.finished==False).count()
    return flask.jsonify({"count": count })


@bp.route("/stats", methods=["GET"])
def status():
    stats = db.session.execute(
        select(
            select(func.count())
            .select_from(RequestQueue)
            .where(RequestQueue.finished.is_(False))
            .scalar_subquery()
            .label("request_queue"),

            select(func.count())
            .select_from(Map)
            .scalar_subquery()
            .label("maps"),

            select(func.count())
            .select_from(MapVote)
            .scalar_subquery()
            .label("map_votes"),

            select(func.count())
            .select_from(User)
            .scalar_subquery()
            .label("users"),
        )
    ).one()

    return flask.jsonify({
        "request_queue": stats.request_queue,
        "maps": stats.maps,
        "map_votes": stats.map_votes,
        "users": stats.users,
    })

@bp.route("/whoami", methods=["GET"])
@utils.flask_wrappers.with_username()
def whoami(username):
    return flask.jsonify({
        "user_id": username,
        "is_curator": username in utils.curators.CURATORS
    })
