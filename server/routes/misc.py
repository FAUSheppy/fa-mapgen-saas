
import flask
from flask import Blueprint, jsonify

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

import datetime
import json
import uuid

from database.db_import import db
from database.RequestQueue import RequestQueue
from database.MapVote import MapVote

import utils.flask_wrappers


bp = Blueprint("misc", __name__)

@bp.route("/queue", methods=["GET"])
def get_queue_size():
    count = db.session.query(RequestQueue).filter(RequestQueue.finished==False).count()
    return flask.jsonify({"count": count })

@bp.route("/whoami", methods=["GET"])
@utils.flask_wrappers.with_username()
def whoami(username):
    return flask.jsonify({"user_id": username})