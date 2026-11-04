from flask import Blueprint, request, jsonify
from models import db, Asset, AssetTag
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from pydantic import ValidationError
from assets.schemas.asset_schema import AssetCreate, AssetUpdate
from utils import error_response


asset_bp = Blueprint("asset", __name__)

# 1. Create Asset
@asset_bp.route("", methods=["POST"])
def create_asset():

    try:
        data = AssetCreate.model_validate(
            request.get_json(silent=True)
        )

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    asset = Asset(
        asset_name=data.asset_name,
        asset_tag=data.asset_tag,
        category=data.category,
        location=data.location,
        purchase_date=data.purchase_date,
        purchase_cost=data.purchase_cost,
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

    try:
        data = AssetUpdate.model_validate(
            request.get_json(silent=True)
        )

        update_data = data.model_dump(exclude_unset=True)

        # Check whether any fields were provided
        if not update_data:
            return error_response(
                "Provide valid asset fields to update", 400
            )

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    # Apply updates
    for field, value in update_data.items():
        setattr(asset, field, value)

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