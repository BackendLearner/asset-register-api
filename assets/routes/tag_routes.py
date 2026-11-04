from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils import error_response
from assets.repository import AssetRepository

tag_bp = Blueprint("tags", __name__)

asset_repository = AssetRepository()

# 6. Create Asset Tags
@tag_bp.route("/<int:asset_id>/tags", methods=["POST"])
def add_asset_tags(asset_id):

    asset = asset_repository.get_by_id(asset_id)

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

    try:
        created = asset_repository.add_tags(
            asset_id,
            normalized_tags
        )

    except IntegrityError:
        return error_response(
            "Database constraint conflict", 409
        )

    except SQLAlchemyError:
        return error_response(
            "Database error occurred", 500
        )

    return jsonify({
        "message": "Tags added successfully",
        "asset_id": asset_id,
        "tags": [item.tag for item in created]
    }), 201


# 7. Get Asset Tags
@tag_bp.route("/<int:asset_id>/tags", methods=["GET"])
def get_asset_tags(asset_id):

    asset = asset_repository.get_by_id(asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    tags = asset_repository.get_tags(asset_id)

    return jsonify({
        "asset_id": asset_id,
        "tags": [item.tag for item in tags]
    }), 200

    