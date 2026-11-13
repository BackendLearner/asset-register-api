
from flask import Blueprint, request, jsonify

from models import Asset
from schemas import AssetCreate, AssetUpdate, AssetTagCreate
from repository import AssetRepository
from exceptions import AssetValidationError


asset_bp = Blueprint("assets", __name__)

asset_repository = AssetRepository()


# 1. Create Asset
@asset_bp.route("", methods=["POST"])
def create_asset():

    data = AssetCreate.model_validate(
        request.get_json(silent=True)
    )

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

    return jsonify(
        asset_repository.asset_to_dict(asset)
    ), 201


# 2. Get All Assets
@asset_bp.route("", methods=["GET"])
def get_assets():

    assets = asset_repository.list(
        asset_type=request.args.get("type"),
        tag=request.args.get("tag")
    )

    return jsonify(assets), 200


# 3. Get Asset By ID
@asset_bp.route("/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):

    asset = asset_repository.get_by_id(asset_id)

    return jsonify(
        asset_repository.asset_to_dict(asset)
    ), 200


# 4. Update Asset
@asset_bp.route("/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):

    asset = asset_repository.get_by_id(asset_id)

    data = AssetUpdate.model_validate(
        request.get_json(silent=True)
    )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise AssetValidationError([
            {
                "field": "body",
                "message": "Provide valid asset fields to update"
            }
        ])

    asset_repository.update(asset, update_data)

    return jsonify(
        asset_repository.asset_to_dict(asset)
    ), 200


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


# 6. Add Multiple Asset Tags
@asset_bp.route("/<int:asset_id>/tags", methods=["POST"])
def add_asset_tags(asset_id):

    data = AssetTagCreate.model_validate(
        request.get_json(silent=True)
    )

    created_tags = asset_repository.add_tags(
        asset_id,
        data.tags
    )

    return jsonify({
        "message": "Tags added successfully",
        "asset_id": asset_id,
        "tags": [
            asset_repository.tag_to_dict(tag)
            for tag in created_tags
        ]
    }), 201


# 7. Get Active Asset Tags
@asset_bp.route("/<int:asset_id>/tags", methods=["GET"])
def get_asset_tags(asset_id):

    tags = asset_repository.get_tags(asset_id)

    return jsonify({
        "asset_id": asset_id,
        "tags": [
            asset_repository.tag_to_dict(tag)
            for tag in tags
        ]
    }), 200
