import flask
from flask import Blueprint, jsonify

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

import datetime
import json
import uuid

from database.db_import import db
from database.RequestQueue import RequestQueue
from database.Map import Map

import utils.mapgen_style
import utils.constants

bp = Blueprint("requests", __name__)

def _build_options_dict(data):
    return {
        field: data.get(field) for field in utils.constants.OPTION_FIELDS
        if data.get(field) is not None
    }

@bp.route("/request/new", methods=["POST"])
def create_request():

    options = _build_options_dict(flask.request.json)

    request_id = str(uuid.uuid4())
    for i in range(0, 20):

        options_full = utils.mapgen_style.generate_map_config(options)

        queue_entry = RequestQueue(
            options=json.dumps(options_full, sort_keys=True),
            date=datetime.datetime.now().timestamp() - i*1000,
            request_id=request_id,
            requester=flask.request.remote_addr,
            count=1,
            finished=False,
        )

        db.session.add(queue_entry)
        
    db.session.commit()

    return jsonify(
        {
            "status": "queued",
            "request_id": request_id,
        }
    )