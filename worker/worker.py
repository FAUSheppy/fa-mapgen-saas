import os
import subprocess
import shutil
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker

import boto3

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DB_URL = os.environ["DB_URL"]

S3_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]
S3_SECRET_KEY = os.environ["S3_SECRET_KEY"]
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]

# Change as required
S3_BUCKET = os.environ.get("S3_BUCKET", "mapgen-output")

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

Base = declarative_base()


class RequestQueue(Base):
    __tablename__ = "request_queue"

    options = Column(String, primary_key=True)
    date = Column(Integer, primary_key=True)

    requester = Column(String)
    count = Column(Integer)
    finished = Column(Boolean)


class Map(Base):
    __tablename__ = "maps"

    id = Column(String, primary_key=True)  # filename
    options = Column(String)


engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# -----------------------------------------------------------------------------
# Placeholder generator
# -----------------------------------------------------------------------------

def generate_dev(options, count):

    cmd = [
        "docker",
        "run",
        "-v",
        "./output:/output",
        "--rm",
        "harbor-registry.atlantishq.de/atlantishq/neroxis-mapgen",
        "--out-path",
        "/output/",
        "--num-to-generate",
        "1",
        "--spawn-count=14"
    ]

    print("Generating more maps...")
    print("Running:", " ".join(cmd))

    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Generator failed: {e}")

def generate(options: str, count: int) -> None:
    
    cmd = [
        "/opt/java/openjdk/bin/java",
        "-jar",
        "/NeroxisMapGenerator.jar",
        "--out-path",
        "./output/",
        "--num-to-generate", "1"
    ]
    subprocess.run(cmd)

# -----------------------------------------------------------------------------
# S3
# -----------------------------------------------------------------------------


def create_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    )


def upload_pngs(session, s3_client, options: str):
    output_dir = Path("./output")

    png_files = list(output_dir.rglob("*.png"))

    for png_file in png_files:

        filename = png_file.name

        print(f"Uploading {png_file} -> s3://{S3_BUCKET}/{filename}")

        s3_client.upload_file(
            Filename=str(png_file),
            Bucket=S3_BUCKET,
            Key=filename,  # remove path, upload filename only
        )

        session.merge(
            Map(
                id=filename,
                options=options,
            )
        )

        shutil.rmtree(png_file.parent)


def main():
    session = Session()
    s3_client = create_s3_client()

    try:
        requests = session.scalars(
            select(RequestQueue).where(RequestQueue.finished.is_(False))
        ).all()

        for request in requests:
            print(
                f"Processing request: options={request.options}, "
                f"date={request.date}"
            )

            if os.environ.get("DEV_SETUP"):
                generate_dev(request.options, request.count)
            else:
                generate(request.options, request.count)

            upload_pngs(
                session=session,
                s3_client=s3_client,
                options=request.options,
            )

            # request.finished = True

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    main()
