
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import date
from models import db, Asset, AssetTag
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
import math


load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///assets.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Common error response
def error_response(message, status_code):
    return jsonify({"error": message}), status_code


# Validate purchase cost
def validate_purchase_cost(cost):
    if cost is None:
        return None

    if isinstance(cost, bool):
        raise ValueError

    cost = float(cost)

    if not math.isfinite(cost) or cost < 0:
        raise ValueError

    return cost


# Validate purchase date
def validate_purchase_date(value):
    if value is None or value == "":
        return None

    if not isinstance(value, str):
        raise ValueError

    parsed_date = date.fromisoformat(value)

    if parsed_date.isoformat() != value:
        raise ValueError

    return parsed_date


@app.route("/")
def home():
    return "Welcome to the Asset Register API!"


# 1. Create assets
@app.route("/assets", methods=["POST"])
def create_asset():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response(
            "Request body must be valid JSON", 400
        )

    required_fields = ["asset_name", "asset_tag", "category"]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return error_response(
                f"{field} is required and must be a non-empty string", 400
            )

    max_lengths = {
        "asset_name": 100,
        "asset_tag": 50,
        "category": 100,
        "location": 100,
        "status": 30,
    }

    for field, max_length in max_lengths.items():
        value = data.get(field)

        if value is not None:
            if not isinstance(value, str):
                return error_response(
                    f"{field} must be a string", 400
                )

            if len(value.strip()) > max_length:
                return error_response(
                    f"{field} must not exceed {max_length} characters", 400
                )

    status = data.get("status", "Active")

    if status not in ("Active", "Inactive"):
        return error_response(
            "status must be Active or Inactive", 400
        )

    try:
        purchase_date = validate_purchase_date(
            data.get("purchase_date")
        )
    except (ValueError, TypeError):
        return error_response(
            "purchase_date must use YYYY-MM-DD format", 400
        )

    try:
        purchase_cost = validate_purchase_cost(
            data.get("purchase_cost")
        )
    except (ValueError, TypeError):
        return error_response(
            "purchase_cost must be a finite, non-negative number", 400
        )

    asset = Asset(
        asset_name=data["asset_name"].strip(),
        asset_tag=data["asset_tag"].strip(),
        category=data["category"].strip(),
        location=(
            data["location"].strip()
            if data.get("location") is not None
            else None
        ),
        purchase_date=purchase_date,
        purchase_cost=purchase_cost,
        status=status,
    )

    try:
        db.session.add(asset)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return error_response(
            "Asset could not be created due to a database constraint conflict.",
            409
        )

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception(
            "Database error while creating asset"
        )
        return error_response(
            "A database error occurred while creating the asset.", 500
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(
            "Unexpected error while creating asset"
        )
        return error_response(
            "An unexpected error occurred while creating asset.", 500
        )

    return jsonify(asset.to_dict()), 201


# 2. Get assets
@app.route("/assets", methods=["GET"])
def get_assets():

    query = Asset.query.filter_by(status="Active")

    asset_type = request.args.get("type")
    tag = request.args.get("tag")

    if asset_type:
        query = query.filter(Asset.category == asset_type)

    if tag:
        query = query.filter(
            Asset.id.in_(
                db.session.query(AssetTag.asset_id).filter_by(
                    tag=tag,
                    status="Active",
                )
            )
        )

    assets = query.order_by(Asset.id).all()

    return jsonify([asset.to_dict() for asset in assets]), 200


# 3. Get asset by ID
@app.route("/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    return jsonify(asset.to_dict()), 200


# 4. Update asset by ID
@app.route("/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response(
            "Request body must be valid JSON", 400
        )

    allowed_fields = {
        "asset_name", "asset_tag", "category",
        "location", "purchase_date", "purchase_cost", "status"
    }

    if not data or not set(data).issubset(allowed_fields):
        return error_response(
            "Provide valid asset fields to update", 400
        )

    # Validate required string fields
    required_string_fields = {
        "asset_name": 100,
        "asset_tag": 50,
        "category": 100,
    }

    for field, max_length in required_string_fields.items():

        if field in data:
            value = data[field]

            if not isinstance(value, str) or not value.strip():
                return error_response(
                    f"{field} cannot be empty and must be a string", 400
                )

            if len(value.strip()) > max_length:
                return error_response(
                    f"{field} must not exceed {max_length} characters", 400
                )

    # Validate location
    if "location" in data:
        location = data["location"]

        if location is not None and not isinstance(location, str):
            return error_response(
                "location must be a string or null", 400
            )

        if isinstance(location, str) and len(location.strip()) > 100:
            return error_response(
                "location must not exceed 100 characters", 400
            )

    # Validate status
    if "status" in data:
        if data["status"] not in ("Active", "Inactive"):
            return error_response(
                "status must be Active or Inactive", 400
            )

    # Validate purchase date before modifying the asset
    try:
        purchase_date = (
            validate_purchase_date(data["purchase_date"])
            if "purchase_date" in data
            else asset.purchase_date
        )
    except (ValueError, TypeError):
        return error_response(
            "purchase_date must use YYYY-MM-DD format", 400
        )

    # Validate purchase cost before modifying the asset
    try:
        purchase_cost = (
            validate_purchase_cost(data["purchase_cost"])
            if "purchase_cost" in data
            else asset.purchase_cost
        )
    except (ValueError, TypeError):
        return error_response(
            "purchase_cost must be a finite, non-negative number", 400
        )

    # Apply validated changes
    for field in ("asset_name", "asset_tag", "category"):
        if field in data:
            setattr(asset, field, data[field].strip())

    if "location" in data:
        asset.location = (
            data["location"].strip()
            if data["location"] is not None
            else None
        )

    if "status" in data:
        asset.status = data["status"]

    if "purchase_date" in data:
        asset.purchase_date = purchase_date

    if "purchase_cost" in data:
        asset.purchase_cost = purchase_cost

    # Save changes
    try:
        asset.updatedBy = "system"
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return error_response(
            "Asset update failed because of a database constraint conflict, such as a duplicate asset tag.",
            409
        )

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception(
            "Database error while updating asset %s", asset_id
        )
        return error_response(
            "A database error occurred while updating the asset.", 500
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(
            "Unexpected error while updating asset %s", asset_id
        )
        return error_response(
            "An unexpected error occurred while updating the asset.", 500
        )

    return jsonify(asset.to_dict()), 200


# 5. Deactivate asset
@app.route("/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    try:
        asset.status = "Inactive"
        asset.updatedBy = "system"
        db.session.commit()

    except Exception:
        db.session.rollback()
        app.logger.exception(
            "Failed to deactivate asset"
        )
        return error_response("Internal server error", 500)

    return jsonify({
        "message": "Asset deactivated successfully",
        "id": asset.id,
        "status": asset.status
    }), 200


# 6. Create asset tags
@app.route("/assets/<int:asset_id>/tags", methods=["POST"])
def add_asset_tags(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response(
            "Request body must be valid JSON", 400
        )

    tags = data.get("tags")

    if not isinstance(tags, list) or not tags:
        return error_response(
            "tags must be a non-empty list of strings", 400
        )

    if len(tags) > 50:
        return error_response(
            "A maximum of 50 tags can be submitted at once", 400
        )

    if any(
        not isinstance(tag, str) or not tag.strip()
        for tag in tags
    ):
        return error_response(
            "Every tag must be a non-empty string", 400
        )

    normalized_tags = list(dict.fromkeys(
        tag.strip() for tag in tags
    ))

    existing_tags = {
        item.tag
        for item in AssetTag.query.filter_by(
            asset_id=asset_id,
            status="Active",
        ).all()
    }

    new_tags = [
        tag for tag in normalized_tags
        if tag not in existing_tags
    ]

    try:
        created = []

        for tag in new_tags:
            item = AssetTag(
                asset_id=asset_id,
                tag=tag,
                createdBy="system",
                updatedBy="system",
            )

            db.session.add(item)
            created.append(item)

        db.session.commit()

    except Exception:
        db.session.rollback()
        app.logger.exception(
            "Failed to add asset tags"
        )
        return error_response("Internal server error", 500)

    return jsonify({
        "message": "Tags added successfully",
        "asset_id": asset_id,
        "tags": [item.tag for item in created],
    }), 201


# 7. Get asset tags by ID
@app.route("/assets/<int:asset_id>/tags", methods=["GET"])
def get_asset_tags(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    tags = AssetTag.query.filter_by(
        asset_id=asset_id,
        status="Active",
    ).order_by(AssetTag.id).all()

    return jsonify({
        "asset_id": asset_id,
        "tags": [item.tag for item in tags],
    }), 200


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
