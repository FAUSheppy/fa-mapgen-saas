import flask
from flask import Blueprint, jsonify

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

import utils.mapgen_style
import utils.flask_wrappers
import utils.map_votes_enricher
import utils.s3

from database.db_import import db
from database.MapOptions import MapOptions
from database.MapVote import MapVote
from database.User import User
from database.Map import Map

import utils.constants
import boto3
import os
import botocore
import time

bp = Blueprint("maps", __name__)


@bp.route("/maps/search", methods=["POST"])
@utils.flask_wrappers.with_username()
def search_maps(username):

    payload = flask.request.get_json(force=True)
    epsilon = float(payload.pop("epsilon", 0.02))
    epsilon_players = 2
    epsilon_map_size = 128
    request_id = payload.pop("request_id", None)
    seed = payload.pop("ray_id", None)

    query = (
        db.session.query(Map)
        .options(joinedload(Map.options))
        .join(MapOptions)
    )

    filters = []

    # prepare map option filters #
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
            else:
                value = float(value)
            
            print(field)
            print(field, value)

            filters.append(column >= value - epsilon_tmp)
            filters.append(column <= value + epsilon_tmp)
        else:
            filters.append(column == value)

    # prepare curator/player filters #
    if payload.get("curators", False):
        query = query.filter(
            db.session.query(MapVote)
            .join(User)
            .filter(
                MapVote.map_id == Map.id,
                MapVote.vote == 1,
                User.is_curator.is_(True),
            )
            .exists()
        )

    if payload.get("user") or payload.get("voted_self", False):
        search_user = payload.get("user") or username
        query = query.filter(
            db.session.query(MapVote)
            .join(User)
            .filter(
                MapVote.map_id == Map.id,
                User.id.ilike(f"{search_user}"),
            )
            .exists()
        )

    # apply request id if present #
    if request_id and not filters:
        filters.append(Map.request_id == request_id)

    # apply filters #
    if filters:
        query = query.filter(and_(*filters))

    # introduce variation to search #
    if not request_id and not "order_by_likes" in payload:
        seed = seed or hex(time.time_ns())
        query = query.order_by(
            func.md5(
                func.concat(Map.id, "-", seed)
            )
        )
    elif "order_by_likes" in payload:

        likes_subq = (
            db.session.query(
                MapVote.map_id,
                func.count().label("like_count"),
            )
            .filter(MapVote.vote == 1)
            .group_by(MapVote.map_id)
            .subquery()
        )

        query = (
            query.outerjoin(
                likes_subq,
                likes_subq.c.map_id == Map.id,
            )
            .order_by(likes_subq.c.like_count.desc().nullslast())
        )

    # decide limit based on search params #
    limit = 40
    if payload.get("voted_self"):
        limit = 1000
    elif payload.get("curators"):
        limit = 100
    elif payload.get("user"):
        limit = 300

    maps = query.limit(limit).all()

    # load your own votes for the maps if logged in #
    utils.map_votes_enricher.enrich_maps_with_votes(maps, username)

    result = []
    for m in maps:

        # get presigned url #
        url = utils.s3.presigned_url_for_map(m)

        # build map data #
        map_data = {
            "id": m.id,
            "options": {
                field: getattr(m.options, field)
                for field in utils.constants.OPTION_FIELDS
            },
            "vote": m.user_vote,
            "like_count": m.like_count,
            "dislike_count": m.dislike_count,
            "total_votes_balance": m.total,
            "like_ratio": m.like_ratio,
            "liked_by": [ u.to_dict() for u in m.liked_by ],
            "presigned_image_url": url,
        }

        if request_id:
            map_data["request_id"] = request_id

        if "map_size" in map_data:
            map_size_km = int(map_data["map_size"]*512/10)
            map_data["map_size"] = f"{map_size_km}x{map_size_km}"

        result.append(map_data)


    response = {
        "result" : result,
        "seed" : seed
    }

    return jsonify(response)
