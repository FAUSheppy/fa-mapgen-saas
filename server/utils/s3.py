import os
import boto3
import botocore

def presigned_url_for_map(m):

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

    return url