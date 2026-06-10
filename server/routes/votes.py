
import flask
from flask import Blueprint, jsonify

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

import datetime
import json
import uuid

from database.db_import import db
from database.RequestQueue import RequestQueue
from database.User import User
from database.MapVote import MapVote

import utils.flask_wrappers

bp = Blueprint("votes", __name__)

@bp.route("/vote", methods=["GET", "POST"])
@utils.flask_wrappers.with_username()
def vote(username):
    if flask.request.method == "POST":
        payload = flask.request.get_json(force=True)
        mapid = payload["mapid"]
        
        vote = int(payload["vote"])
        valid_votes = [1, 0, -1]
        if vote not in valid_votes:
            return (f"Invalid Vote {vote} only {valid_votes} are allowed.", 400)

        user = User.get_or_create(username)
        map_vote = MapVote(map_id=mapid,
                           user_id=username, 
                           vote=vote,
                           updated_at=datetime.datetime.now())
        db.session.merge(map_vote)
        db.session.commit()
        return flask.jsonify(map_vote.to_dict())
    else:
        # query all all likes from that user
        votes = db.session.query(MapVote).filter(MapVote.user_id==username).all()
        return flask.jsonify(votes)
