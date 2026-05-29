import os
import json
import flask
import random
import subprocess
from io import BytesIO
import flask_sqlalchemy

import mapgen_style

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import func

import uuid

import boto3
from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    send_file,
    abort,
)
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    create_engine,
    select,
    ForeignKey,
    Float
)




app = Flask(__name__, static_folder=".", static_url_path="")

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class RequestQueue(db.Model):
    __tablename__ = "request_queue"

    options = Column(String, primary_key=True)
    date = Column(Integer, primary_key=True)

    requester = Column(String)
    request_id = Column(String)
    count = Column(Integer)
    finished = Column(Boolean)
    state = Column(Integer)

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


class MapOptions(db.Model):
    __tablename__ = "map_options"

    map_id = Column(
        String,
        ForeignKey("maps.id", ondelete="CASCADE"),
        primary_key=True,
    )

    map_size = Column(String)
    spawn_count = Column(Integer)
    num_teams = Column(Integer)

    style = Column(String)
    terrain_symmetry = Column(String)
    texture_style = Column(String)
    terrain_style = Column(String)
    resource_style = Column(String)
    prop_style = Column(String)

    reclaim_density = Column(Float)
    resource_density = Column(Float)

    map = relationship("Map", back_populates="options")

@app.route("/maps/search", methods=["POST"])
def search_maps():
    payload = request.get_json(force=True)

    epsilon = float(payload.pop("epsilon", 0.1))
    request_id = payload.pop("request_id", None)

    query = (
        db.session.query(Map)
        .options(joinedload(Map.options))
        .join(MapOptions)
    )

    filters = []

    for field in OPTION_FIELDS:
        if field not in payload:
            continue

        value = payload[field]
        column = getattr(MapOptions, field)

        if field in NUMERIC_FIELDS:
            filters.append(column >= value - epsilon)
            filters.append(column <= value + epsilon)
        else:
            filters.append(column == value)

    if request_id:
        filters.append(Map.request_id == request_id)

    if filters:
        query = query.filter(and_(*filters))
    
    maps = query.all()

    result = []

    for m in maps:
        map_data = {
            "id": m.id,
            "options": {
                field: getattr(m.options, field)
                for field in OPTION_FIELDS
            },
        }

        if request_id:
            map_data["request_id"] = request_id

        result.append(map_data)

    return jsonify(result)

OPTION_FIELDS = [
    "map_size",
    "spawn_count",
    "num_teams",
    "style",
    "terrain_symmetry",
    "texture_style",
    "terrain_style",
    "resource_style",
    "prop_style",
    "reclaim_density",
    "resource_density",
]

NUMERIC_FIELDS = {
    "spawn_count",
    "num_teams",
    "reclaim_density",
    "resource_density",
}


def build_options_dict(data):
    return {
        field: data.get(field)
        for field in OPTION_FIELDS
        if data.get(field) is not None
    }


# ---------------------------------------------------------------------------
# 1. HTML Form endpoint -> RequestQueue
# ---------------------------------------------------------------------------

@app.route("/request/new", methods=["POST"])
def create_request():

    options = build_options_dict(request.form)

    request_id = str(uuid.uuid4())

    for i in range(0, 20):

        options_full = mapgen_style.generate_map_config(options)

        queue_entry = RequestQueue(
            options=json.dumps(options_full, sort_keys=True),
            date=0,
            request_id=request_id,
            requester=request.remote_addr,
            count=2,
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


@app.route("/maps/<map_id>/image", methods=["GET"])
def get_map_image(map_id):

    bucket = os.environ["S3_BUCKET"]

    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    )

    key = f"{map_id}"

    try:
        obj = s3.get_object(
            Bucket=bucket,
            Key=key,
        )
    except Exception as e:
        raise e
        abort(404)

    return send_file(
        BytesIO(obj["Body"].read()),
        mimetype="image/png",
        download_name=key,
    )

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)
