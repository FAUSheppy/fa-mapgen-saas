#!/usr/bin/env python3

import json
import logging
import os
import sys
import time
from contextlib import contextmanager

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:password@localhost/generation_queue",
)

K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "default")
JOB_IMAGE = os.getenv("JOB_IMAGE", "your-image:latest")
JOB_NAME_PREFIX = os.getenv("JOB_NAME_PREFIX", "mapgen")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# -----------------------------------------------------------------------------
# SQLAlchemy setup
# -----------------------------------------------------------------------------

Base = declarative_base()


class GenerationQueue(Base):
    __tablename__ = "generation_queue"

    options = Column(String, primary_key=True)
    count = Column(Integer)


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# -----------------------------------------------------------------------------
# Kubernetes setup
# -----------------------------------------------------------------------------

def load_k8s():
    try:
        config.load_incluster_config()
        logging.info("Loaded in-cluster Kubernetes config")
    except config.ConfigException:
        config.load_kube_config()
        logging.info("Loaded local kubeconfig")


batch_v1 = None


def create_job(options_dict, unique_suffix):
    args = []

    for key, value in options_dict.items():
        if isinstance(value, bool):
            value = str(value).lower()
        else:
            value = str(value)

        args.append(f"--{key}={value}")

    job_name = f"{JOB_NAME_PREFIX}-{unique_suffix}"

    job_manifest = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(
            backoff_limit=0,
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    restart_policy="Never",
                    init_containers=[
                        client.V1Container(
                            name="mapgen",
                            image=JOB_IMAGE,
                            args=args,
                        )
                    ],
                    containers=[
                        client.V1Container(
                            name="pause",
                            image="busybox",
                            command=["sh", "-c", "echo done"],
                        )
                    ],
                )
            ),
        ),
    )

    logging.info("Creating job %s", job_name)

    batch_v1.create_namespaced_job(
        namespace=K8S_NAMESPACE,
        body=job_manifest,
    )

    return job_name


def wait_for_job(job_name):
    while True:
        job = batch_v1.read_namespaced_job_status(
            name=job_name,
            namespace=K8S_NAMESPACE,
        )

        if job.status.succeeded:
            logging.info("Job %s succeeded", job_name)
            return True

        if job.status.failed:
            logging.error("Job %s failed", job_name)
            return False

        time.sleep(5)


def cleanup_job(job_name):
    try:
        batch_v1.delete_namespaced_job(
            name=job_name,
            namespace=K8S_NAMESPACE,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground"
            ),
        )
        logging.info("Deleted job %s", job_name)

    except ApiException as e:
        logging.warning("Failed to delete job %s: %s", job_name, e)


# -----------------------------------------------------------------------------
# Queue processing
# -----------------------------------------------------------------------------

def process_queue():
    with session_scope() as session:

        rows = (
            session.execute(
                select(GenerationQueue).limit(BATCH_SIZE)
            )
            .scalars()
            .all()
        )

        if not rows:
            logging.info("Queue empty")
            return

        for idx, row in enumerate(rows):
            logging.info("Processing queue entry")

            try:
                options_dict = json.loads(row.options)

                if not isinstance(options_dict, dict):
                    raise ValueError("options JSON is not an object")

            except Exception as e:
                logging.error(
                    "Failed to parse options JSON: %s",
                    e,
                )
                continue

            job_name = create_job(
                options_dict=options_dict,
                unique_suffix=f"{int(time.time())}-{idx}",
            )

            success = wait_for_job(job_name)

            if success:
                session.delete(row)
                session.commit()
                logging.info("Deleted processed queue entry")

            cleanup_job(job_name)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    global batch_v1

    load_k8s()

    batch_v1 = client.BatchV1Api()

    while True:
        try:
            process_queue()
        except Exception:
            logging.exception("Unhandled error during queue processing")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
