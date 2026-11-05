
from flask import Blueprint, request, jsonify

from assets.repository import AssetRepository


tag_bp = Blueprint("tags", __name__)

asset_repository = AssetRepository()


# 6. Create Asset Tags
@tag_bp.route("/<int:asset_id>/tags", methods=["POST"])
def add_asset_tags(asset_id):

    
    asset_repository.get_by_id(asset_id)

    # Validate request body
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    tags = data.get("tags")

    if not isinstance(tags, list) or not tags:
        return jsonify({
            "error": "tags must be a non-empty list of strings"
        }), 400

    if len(tags) > 50:
        return jsonify({
            "error": "A maximum of 50 tags can be submitted at once"
        }), 400

    if any(
        not isinstance(tag, str) or not tag.strip()
        for tag in tags
    ):
        return jsonify({
            "error": "Every tag must be a non-empty string"
        }), 400

    
    normalized_tags = list(dict.fromkeys(
        tag.strip() for tag in tags
    ))

    # Repository handles database operations and exceptions
    created = asset_repository.add_tags(
        asset_id,
        normalized_tags
    )

    return jsonify({
        "message": "Tags added successfully",
        "asset_id": asset_id,
        "tags": [item.tag for item in created]
    }), 201


# 7. Get Asset Tags
@tag_bp.route("/<int:asset_id>/tags", methods=["GET"])
def get_asset_tags(asset_id):

    # Check whether the asset exists and is active
    asset_repository.get_by_id(asset_id)

    # Retrieve active tags
    tags = asset_repository.get_tags(asset_id)

    return jsonify({
        "asset_id": asset_id,
        "tags": [item.tag for item in tags]
    }), 200
