
from flask import Blueprint, request, jsonify
from models import Asset

from pydantic import ValidationError
from assets.schemas.asset_schema import AssetCreate, AssetUpdate
from assets.repository import AssetRepository


asset_bp = Blueprint("asset", __name__)

asset_repository = AssetRepository()


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

    asset_repository.create(asset)

    return jsonify(asset.to_dict()), 201


# 2. Get All Assets
@asset_bp.route("", methods=["GET"])
def get_assets():

    asset_type = request.args.get("type")
    tag = request.args.get("tag")

    assets = asset_repository.list(
        asset_type=asset_type,
        tag=tag
    )

    return jsonify([
        asset.to_dict() for asset in assets
    ]), 200


# 3. Get Asset By ID
@asset_bp.route("/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):

    asset = asset_repository.get_by_id(asset_id)

    return jsonify(asset.to_dict()), 200


# 4. Update Asset
@asset_bp.route("/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):

    asset = asset_repository.get_by_id(asset_id)

    try:
        data = AssetUpdate.model_validate(
            request.get_json(silent=True)
        )

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return jsonify({
                "error": "Provide valid asset fields to update"
            }), 400

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    asset_repository.update(asset, update_data)

    return jsonify(asset.to_dict()), 200


# 5. Deactivate Asset
@asset_bp.route("/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id):

    asset = asset_repository.get_by_id(asset_id)

    asset_repository.deactivate(asset)

    return jsonify({
        "message": "Asset deactivated successfully",
        "id": asset.id,
        "status": asset.status
    }), 200
