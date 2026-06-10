import flask
from flask import Blueprint

import boto3
import io
import os

bp = Blueprint("preview", __name__)

@bp.route("/maps/<map_id>/image", methods=["GET"])
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

    return flask.send_file(
        io.BytesIO(obj["Body"].read()),
        mimetype="image/png",
        download_name=key,
    )
