import os
import sys
import subprocess
import re
import datetime
import json
import time
import shutil
from pathlib import Path

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
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

import boto3

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DB_URL = os.environ.get("DB_URL") or os.environ.get("database-url")

S3_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]
S3_SECRET_KEY = os.environ["S3_SECRET_KEY"]
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]

DEBUG = os.environ.get("DEBUG") == "1"

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
    request_id = Column(String)
    count = Column(Integer)
    finished = Column(Boolean)
    state = Column(Integer)


class Map(Base):
    __tablename__ = "maps"

    id = Column(String, primary_key=True)  # filename
    request_id = Column(String)
    options = relationship(
        "MapOptions",
        back_populates="map",
        uselist=False,
        cascade="all, delete-orphan",
    )



class MapOptions(Base):
    __tablename__ = "map_options"

    map_id = Column(
        String,
        ForeignKey("maps.id", ondelete="CASCADE"),
        primary_key=True,
    )

    map_size = Column(Integer)
    spawn_count = Column(Integer)
    num_teams = Column(Integer)

    style = Column(String)
    terrain_symmetry = Column(String)
    texture_style = Column(String)
    terrain_style = Column(String)
    resource_style = Column(String)
    prop_style = Column(String)
    version = Column(String)

    reclaim_density = Column(Float)
    resource_density = Column(Float)

    map = relationship("Map", back_populates="options")


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
        '--map-size=15km', '--spawn-count', '14'
    ]

    if DEBUG:
        print("Generating more maps...")
        print("Running:", " ".join(cmd))

    try:
        if DEBUG:
            subprocess.run(cmd)
        else:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except subprocess.CalledProcessError as e:
        if DEBUG:
            print(f"Generator failed: {e}")

def generate(options: str, count: int) -> None:
    
    allowed = re.compile(r"[^A-Za-z0-9._]")

    version = options.pop("version", None)

    binary = "/NeroxisGen_1.21.1.jar"
    if version:
        version = allowed.sub("", str(version))
        binary = f"/NeroxisGen_{version}.jar"

    cmd = [
        "/opt/java/openjdk/bin/java",
        "-jar",
        binary,
        "--out-path",
        "./output/",
        "--num-to-generate", str(int(count))
    ]

    

    
    for key, value in options.items():

        safe_key = allowed.sub("", str(key))
        safe_value = allowed.sub("", str(value))
    
        if not safe_key:
            continue
    
        cmd.extend([
            f"--{safe_key.replace('_', '-')}",
            str(safe_value),
        ])

    import sys
    if DEBUG:
        print(cmd, file=sys.stderr)
        subprocess.run(cmd, timeout=180)
    else:
        proc = subprocess.run(
            cmd,
            timeout=180,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return proc

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


def upload_pngs(session, s3_client, options, request_id):
    output_dir = Path("./output")

    png_files = list(output_dir.rglob("*.png"))

    options = json.loads(options)
    for png_file in png_files:

        filename = png_file.name

        if DEBUG:
            print(f"Uploading {png_file} -> s3://{S3_BUCKET}/{filename}")

        s3_client.upload_file(
            Filename=str(png_file),
            Bucket=S3_BUCKET,
            Key=filename,  # remove path, upload filename only
        )

        map_options = MapOptions(
            map_size=options.get("map_size"),
            spawn_count=options.get("spawn_count"),
            num_teams=options.get("num_teams"),
            style=options.get("style"),
            terrain_symmetry=options.get("terrain_symmetry"),
            texture_style=options.get("texture_style"),
            terrain_style=options.get("terrain_style"),
            resource_style=options.get("resource_style"),
            prop_style=options.get("prop_style"),
            reclaim_density=options.get("reclaim_density"),
            resource_density=options.get("resource_density"),
            version=options.get("version"),
        )

        session.merge(
            Map(
                id=filename,
                options=map_options,
                request_id=request_id
            )
        )

        if not os.environ.get("DEV_SETUP"):
            shutil.rmtree(png_file.parent)

    return len(png_files)


def main():

    start_time = datetime.datetime.now()
    session = Session()
    s3_client = create_s3_client()
    with session.begin():

        requests = session.scalars(
            select(RequestQueue).where(RequestQueue.finished.is_(False))
        ).all()

        requests = session.scalars(
            select(RequestQueue)
            .where(
                RequestQueue.finished.is_(False),
                RequestQueue.state.is_(None),
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        ).all()
    
        for req in requests:
            req.state = 1

        for request in requests:
            if DEBUG:
                print(
                    f"Processing request: options={request.options}, "
                    f"date={request.date}"
                )

            options = json.loads(request.options)
            if DEBUG:
                print(options)

            if os.environ.get("DEV_SETUP"):
                generate_dev(options, request.count)
            else:
                try:
                    proc = generate(options, request.count)
                except subprocess.TimeoutExpired:
                    if DEBUG:
                        print("Generation killed after exceeding 180s.")
                    else:
                        print(json.dumps({
                            "status": "aborted",
                            "reason": "timeout",
                            "message": "Generation killed after exceeding 180s.",
                            "request_id": request.request_id,
                            "date": request.date
                        }), file=sys.stderr)
                    request.finished = True
                    session.commit()
                    return
                except subprocess.CalledProcessError as exc:
                    if DEBUG:
                        print(f"Process failed with exit code {exc.returncode}")
                    else:
                        print(json.dumps({
                            "status": "aborted",
                            "reason": "process_failed",
                            "message": f"Process failed with exit code {exc.returncode}",
                            "exit_code": exc.returncode,
                            "stderr": exc.stderr,
                            "stderr": exc.stdout,
                            "request_id": request.request_id,
                            "date": request.date
                        }))
                    request.finished = True
                    session.commit()
                    return


            uploaded_maps = upload_pngs(
                session=session,
                s3_client=s3_client,
                options=request.options,
                request_id=request.request_id
            )

            request.finished = True

            if not DEBUG:
                print(json.dumps({
                    "status": "completed",
                    "request_id": request.request_id,
                    "date": request.date,
                    "requested_maps": request.count,
                    "stdout": proc.stdout,
                    "options": options,
                    "uploaded_maps": uploaded_maps,
                    "duration": (datetime.datetime.now() - start_time).total_seconds()

                }), file=sys.stderr)

        session.commit()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    while True:
        time.sleep(1)
        main()
