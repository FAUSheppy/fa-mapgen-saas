import os
import flask
import random
import subprocess

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


app = Flask(__name__, static_folder=".", static_url_path="")

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///maps.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database model
class Map(db.Model):
    __tablename__ = "maps"

    id = db.Column(db.String, primary_key=True)
    viewed = db.Column(db.Integer, nullable=False, default=0)
    options = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "viewed": self.viewed,
            "options": self.options,
        }


def generate():

    available_maps = Map.query.filter(Map.viewed < 3).count()

    if available_maps < 100:
        cmd = [
            "docker",
            "run",
            "-v",
            "./output:/output",
            "--rm",
            "neroxis-mapgen",
            "--out-path",
            "/output/",
            "--num-to-generate",
            "20",
            "--spawn-count=14"
        ]

        print("Generating more maps...")
        print("Running:", " ".join(cmd))

        try:
            subprocess.Popen(cmd)
        except subprocess.CalledProcessError as e:
            print(f"Generator failed: {e}")

    # Remove exhausted maps
    Map.query.filter(Map.viewed >= 3).delete()
    db.session.commit()

    # Sync database with output directories
    output_dir = "./output"

    if not os.path.exists(output_dir):
        return

    existing_ids = {
        row.id for row in db.session.query(Map.id).all()
    }

    for entry in os.listdir(output_dir):
        full_path = os.path.join(output_dir, entry)

        if not os.path.isdir(full_path):
            continue

        if entry not in existing_ids:
            db.session.add(
                Map(
                    id=entry,
                    viewed=0,
                    options=""
                )
            )

    db.session.commit()


@app.route("/display", methods=["GET"])
def display_maps():

    generate()

    eligible_maps = Map.query.filter(Map.viewed < 3).all()

    if not eligible_maps:
        return jsonify({
            "maps": [],
            "message": "No maps available"
        }), 404

    selected_maps = random.sample(
        eligible_maps,
        min(18, len(eligible_maps))
    )

    for map_obj in selected_maps:
        map_obj.viewed += 1

    db.session.commit()


    return flask.render_template(
        "display.html",
        maps=selected_maps
    )

@app.route("/api", methods=["GET"])
def api_stub():

    map_id = request.args.get("id")

    return jsonify({
        "id": map_id
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)
