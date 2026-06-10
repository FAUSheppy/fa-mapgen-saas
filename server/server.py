import os
import flask

from database.db_import import db

app = flask.Flask(__name__, static_folder=".", static_url_path="")

# config & DB init #
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL") or os.getenv("database-url")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

import routes.map_preview
app.register_blueprint(routes.map_preview.bp)

import routes.maps
app.register_blueprint(routes.maps.bp)

import routes.misc
app.register_blueprint(routes.misc.bp)

import routes.requesting
app.register_blueprint(routes.requesting.bp)

import routes.votes
app.register_blueprint(routes.votes.bp)

def create_app():
    db.create_all()

if __name__ == "__main__":

    with app.app_context():
        create_app()

    app.run(host="0.0.0.0", port=5000, debug=True)
