import flask
from flask import Blueprint, jsonify

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

import utils.mapgen_style

from database.db_import import db
from database.MapOptions import MapOptions
from database.Map import Map

import utils.constants
import boto3
import os
import botocore

bp = Blueprint("maps", __name__)

@bp.route("/maps/search", methods=["POST"])
def search_maps():

    payload = flask.request.get_json(force=True)

    # TODO query for maps liked by user
    liked_by_user = flask.request.args.get("liked_by_user")

    # TODO order by amount of likes
    order_by_likes = flask.request.args.get("order_by_likes")

    epsilon = float(payload.pop("epsilon", 0.02))
    epsilon_players = 2
    epsilon_map_size = 128
    request_id = payload.pop("request_id", None)

    query = (
        db.session.query(Map)
        .options(joinedload(Map.options))
        .join(MapOptions)
    )

    # TODO allow or filters #
    filters = []

    for field in utils.constants.OPTION_FIELDS:

        if field not in payload:
            continue

        value = payload[field]
        column = getattr(MapOptions, field)

        if field in utils.constants.NUMERIC_FIELDS:

            epsilon_tmp = epsilon

            if field == "spawn_count":
                epsilon_tmp = epsilon_players
            elif field == "map_size":
                epsilon_tmp = epsilon_map_size
                value = utils.mapgen_style.convert_to_grid_units(value)

            # do not move this up, grid values are int, km are not! #
            value = int(value)
            
            print(field)
            print(field, value)

            filters.append(column >= value - epsilon_tmp)
            filters.append(column <= value + epsilon_tmp)
        else:
            filters.append(column == value)

    if request_id and not filters:
        filters.append(Map.request_id == request_id)

    if filters:
        query = query.filter(and_(*filters))

    if not request_id:
        query = query.order_by(func.random())
    
    maps = query.limit(40).all()

    result = []

    for m in maps:

        s3 = boto3.client(
            "s3",
            config=botocore.config.Config(
                signature_version="s3v4"
            ),
            endpoint_url=os.environ["S3_ENDPOINT"],
            aws_access_key_id=os.environ["S3_ACCESS_KEY"],
            region_name="euw",
            aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        )

        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": os.environ["S3_BUCKET"],
                "Key": f"{m.id}",

            },
            ExpiresIn=300,
        )

        map_data = {
            "id": m.id,
            "options": {
                field: getattr(m.options, field)
                for field in utils.constants.OPTION_FIELDS
            },
            "presigned_image_url": url, # TODO included presigned URL to s3web.anycast.atlantishq.de or equivalent
        }

        if request_id:
            map_data["request_id"] = request_id

        if "map_size" in map_data:
            map_size_km = int(map_data["map_size"]*512/10)
            map_data["map_size"] = f"{map_size_km}x{map_size_km}"

        result.append(map_data)

    return jsonify(result)