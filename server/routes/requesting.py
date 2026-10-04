import flask
import sys
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
import routes.map_preview

bp = Blueprint("requests", __name__)

def _build_options_dict(data):
    return {
        field: data.get(field) for field in utils.constants.OPTION_FIELDS + [ "map_name"]
        if data.get(field) is not None
    }

@bp.route("/request/new", methods=["POST"])
def create_request():

    options = _build_options_dict(flask.request.json)

    request_id = str(uuid.uuid4())
    CREATE_COUNT = 20
    map_name = options.get("map_name")

    if map_name:
        print(f"Generating specific map: {map_name}")
        CREATE_COUNT = 1

    for i in range(0, CREATE_COUNT):

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

@bp.route("/request/preview/<mapid>", methods=["GET"])
def request_preview(mapid):


    # check exists #
    try:
        return routes.map_preview.get_map_image(mapid + "_preview.png")
    except Exception: # todo
        print(f"{mapid} doesnt exist yet", file=sys.stderr)
        pass

    options = _build_options_dict({"map_name": mapid})
    request_id = str(uuid.uuid4())
    options_full = utils.mapgen_style.generate_map_config(options)
    queue_entry = RequestQueue(
        options=json.dumps(options_full, sort_keys=True),
        date=datetime.datetime.now().timestamp(),
        request_id=request_id,
        requester=flask.request.remote_addr,
        count=1,
        finished=False,
    )
    db.session.add(queue_entry)
    db.session.commit()

    # wait for request to finish #
    while True:

        rq = db.session.query(RequestQueue).filter(RequestQueue.request_id==request_id,
                RequestQueue.finished).first()
        if rq:
            map_name = json.loads(rq.options)["map_name"]
            return routes.map_preview.get_map_image(map_name + "_preview.png")

