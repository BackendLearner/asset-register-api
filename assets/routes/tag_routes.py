from flask import Blueprint, request, jsonify
from models import db, Asset, AssetTag
from utils import error_response

tag_bp = Blueprint("tags", __name__)


# 6. Create Asset Tags
@tag_bp.route("/<int:asset_id>/tags", methods=["POST"])
def add_asset_tags(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("Request body must be valid JSON", 400)

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
            status="Active"
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
                updatedBy="system"
            )

            db.session.add(item)
            created.append(item)

        db.session.commit()

    except Exception:
        db.session.rollback()
        return error_response("Internal server error", 500)

    return jsonify({
        "message": "Tags added successfully",
        "asset_id": asset_id,
        "tags": [item.tag for item in created]
    }), 201


# 7. Get Asset Tags
@tag_bp.route("/<int:asset_id>/tags", methods=["GET"])
def get_asset_tags(asset_id):

    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return error_response("Asset not found", 404)

    tags = AssetTag.query.filter_by(
        asset_id=asset_id,
        status="Active"
    ).order_by(AssetTag.id).all()

    return jsonify({
        "asset_id": asset_id,
        "tags": [item.tag for item in tags]
    }), 200