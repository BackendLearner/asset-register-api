from flask import Flask, jsonify
from dotenv import load_dotenv
from models import db
from assets import assets_bp

from exceptions.asset_exceptions import (
    AssetError,
    AssetNotFoundError,
    DuplicateAssetError
)

from sqlalchemy.exc import SQLAlchemyError

import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///assets.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(
    assets_bp,
    url_prefix="/assets"
)


# Handle Asset Not Found
@app.errorhandler(AssetNotFoundError)
def handle_asset_not_found(error):

    return jsonify({
        "success": False,
        "error": "AssetNotFoundError",
        "message": str(error)
    }), 404


# Handle Duplicate Asset
@app.errorhandler(DuplicateAssetError)
def handle_duplicate_asset(error):

    return jsonify({
        "success": False,
        "error": "DuplicateAssetError",
        "message": str(error)
    }), 409


# Handle Other Asset Errors
@app.errorhandler(AssetError)
def handle_asset_error(error):

    return jsonify({
        "success": False,
        "error": "AssetError",
        "message": str(error)
    }), 400


# Handle Database Errors
@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):

    app.logger.exception("Database error occurred")

    return jsonify({
        "success": False,
        "error": "DatabaseError",
        "message": "An internal database error occurred"
    }), 500


@app.route("/")
def home():
    return "Welcome to the Asset Register API!"


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)