from flask import Flask, jsonify
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
import os
from models import db
from routes import asset_bp
from pydantic import ValidationError
from exceptions import (
    AssetError,
    AssetNotFoundError,
    DuplicateAssetError,
    
)

load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///assets.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(
    asset_bp,
    url_prefix="/assets"
)


# 1. Handle Asset Not Found
@app.errorhandler(AssetNotFoundError)
def handle_asset_not_found(error):

    return jsonify({
        "success": False,
        "error": "AssetNotFoundError",
        "message": str(error)
    }), 404


# 2. Handle Duplicate Asset
@app.errorhandler(DuplicateAssetError)
def handle_duplicate_asset(error):

    return jsonify({
        "success": False,
        "error": "DuplicateAssetError",
        "message": str(error)
    }), 400


# 3. Handle Other Asset Errors
@app.errorhandler(AssetError)
def handle_asset_error(error):

    return jsonify({
        "success": False,
        "error": "AssetError",
        "message": str(error)
    }), 400


# 4. Handle Database Errors
@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):

    app.logger.exception("Database error occurred")

    return jsonify({
        "success": False,
        "error": "DatabaseError",
        "message": "An internal database error occurred"
    }), 500


# 5. Handle Unexpected Errors
@app.errorhandler(Exception)
def handle_unexpected_error(error):

    app.logger.exception("Unexpected error occurred")

    return jsonify({
        "success": False,
        "error": "InternalServerError",
        "message": "An unexpected server error occurred"
    }), 500

@app.errorhandler(ValidationError)
def handle_pydantic_validation_error(error):

    errors = [
        {
            "field": ".".join(
                str(part) for part in item["loc"]
            ) or "body",
            "message": item["msg"]
        }
        for item in error.errors()
    ]

    return jsonify({
        "success": False,
        "error": "AssetValidationError",
        "message": "Validation failed",
        "details": errors
    }), 400

@app.route("/")
def home():
    return "Welcome to the Asset Register API!"


if __name__ == "__main__":

    print("Starting Asset Register API...")

    with app.app_context():
        db.create_all()

    print("Database initialized successfully!")

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )
