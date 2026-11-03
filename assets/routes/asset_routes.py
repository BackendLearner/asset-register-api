from flask import Blueprint, request, jsonify
from models import db, Asset, AssetTag
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils import (
    error_response,
    validate_purchase_cost,
    validate_purchase_date
)

asset_bp = Blueprint("asset", __name__)


# 1. Create Asset
@asset_bp.route("", methods=["POST"])
def create_asset():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("Request body must be valid JSON", 400)

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
        "location": 100
    }

    for field, max_length in max_lengths.items():
        value = data.get(field)

        if value is not None:
            if not isinstance(value, str):
                return error_response(f"{field} must be a string", 400)

            if len(value.strip()) > max_length:
                return error_response(
                    f"{field} must not exceed {max_length} characters", 400
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
            if data.get("location") is not None else None
        ),
        purchase_date=purchase_date,
        purchase_cost=purchase_cost,
        status="Active"
    )

    try:
        db.session.add(asset)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return error_response("Database constraint conflict", 409)

    except SQLAlchemyError:
        db.session.rollback()
        return error_response("Database error occurred", 500)

    except Exception:
        db.session.rollback()
        return error_response("Unexpected error occurred", 500)

    return jsonify(asset.to_dict()), 201


# 2. Get All Assets
@asset_bp.route("", methods=["GET"])
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
                    status="Active"
                )
            )
        )

    assets = query.order_by(Asset.id).all()

    return jsonify([asset.to_dict() for asset in assets]), 200


# 3. Get Asset By ID
@asset_bp.route("/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    return jsonify(asset.to_dict()), 200


# 4. Update Asset
@asset_bp.route("/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("Request body must be valid JSON", 400)

    allowed_fields = {
        "asset_name", "asset_tag", "category",
        "location", "purchase_date", "purchase_cost", "status"
    }

    if not data or not set(data).issubset(allowed_fields):
        return error_response("Provide valid asset fields to update", 400)

    required_string_fields = {
        "asset_name": 100,
        "asset_tag": 50,
        "category": 100
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

    if "location" in data:
        location = data["location"]

        if location is not None and not isinstance(location, str):
            return error_response("location must be a string or null", 400)

        if isinstance(location, str) and len(location.strip()) > 100:
            return error_response(
                "location must not exceed 100 characters", 400
            )

    if "status" in data:
        if data["status"] not in ("Active", "Inactive"):
            return error_response("status must be Active or Inactive", 400)

    try:
        purchase_date = (
            validate_purchase_date(data["purchase_date"])
            if "purchase_date" in data else asset.purchase_date
        )
    except (ValueError, TypeError):
        return error_response(
            "purchase_date must use YYYY-MM-DD format", 400
        )

    try:
        purchase_cost = (
            validate_purchase_cost(data["purchase_cost"])
            if "purchase_cost" in data else asset.purchase_cost
        )
    except (ValueError, TypeError):
        return error_response(
            "purchase_cost must be a finite, non-negative number", 400
        )

    for field in ("asset_name", "asset_tag", "category"):
        if field in data:
            setattr(asset, field, data[field].strip())

    if "location" in data:
        asset.location = (
            data["location"].strip()
            if data["location"] is not None else None
        )

    if "status" in data:
        asset.status = data["status"]

    if "purchase_date" in data:
        asset.purchase_date = purchase_date

    if "purchase_cost" in data:
        asset.purchase_cost = purchase_cost

    try:
        asset.updatedBy = "system"
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return error_response("Database constraint conflict", 409)

    except SQLAlchemyError:
        db.session.rollback()
        return error_response("Database error occurred", 500)

    except Exception:
        db.session.rollback()
        return error_response("Unexpected error occurred", 500)

    return jsonify(asset.to_dict()), 200


# 5. Deactivate Asset
@asset_bp.route("/<int:asset_id>", methods=["DELETE"])
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
        return error_response("Internal server error", 500)

    return jsonify({
        "message": "Asset deactivated successfully",
        "id": asset.id,
        "status": asset.status
    }), 200