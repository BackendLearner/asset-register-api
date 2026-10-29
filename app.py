from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import date
from models import db, Asset, AssetTag
from sqlalchemy.exc import IntegrityError
import os
import math
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///assets.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return "Welcome to the Asset Register API!"


# 1. Create assets
@app.route("/assets", methods=["POST"])
def create_asset():
    data = request.get_json(silent=True)

    # 1. Validate request body
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    # 2. Validate required fields
    required_fields = ["asset_name", "asset_tag", "category"]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "error": f"{field} is required and must be a non-empty string"
            }), 400

    # 3. Reject unexpected fields
    allowed_fields = {
        "asset_name", "asset_tag", "category",
        "location", "purchase_date", "purchase_cost", "status"
    }

    unknown_fields = set(data) - allowed_fields

    if unknown_fields:
        return jsonify({
            "error": "Unknown fields provided",
            "fields": sorted(unknown_fields)
        }), 400

    # 4. Validate string lengths
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
                return jsonify({
                    "error": f"{field} must be a string"
                }), 400

            if len(value.strip()) > max_length:
                return jsonify({
                    "error": f"{field} must not exceed {max_length} characters"
                }), 400

    # 5. Validate status
    status = data.get("status", "Active")

    if status not in ("Active", "Inactive"):
        return jsonify({
            "error": "status must be Active or Inactive"
        }), 400

    # 6. Validate purchase date
    purchase_date = None

    if data.get("purchase_date") not in (None, ""):
        if not isinstance(data["purchase_date"], str):
            return jsonify({
                "error": "purchase_date must use YYYY-MM-DD format"
            }), 400

        try:
            purchase_date = date.fromisoformat(data["purchase_date"])

            if purchase_date.isoformat() != data["purchase_date"]:
                raise ValueError

        except ValueError:
            return jsonify({
                "error": "purchase_date must use YYYY-MM-DD format"
            }), 400

    #  Validate purchase cost
    purchase_cost = data.get("purchase_cost")

    if purchase_cost is not None:
        if isinstance(purchase_cost, bool):
            return jsonify({
                "error": "purchase_cost must be a number"
            }), 400

        try:
            purchase_cost = float(purchase_cost)
            if not math.isfinite(purchase_cost) or purchase_cost < 0:
                raise ValueError

        except (ValueError, TypeError):
            return jsonify({
                "error": "purchase_cost must be a finite, non-negative number"
            }), 400

    #  Create asset
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
        status="Active",
    )

    # Save to database and handle errors
    try:
        db.session.add(asset)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Asset could not be created due to a database constraint conflict."
        }), 409

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Database error while creating asset")
        return jsonify({
            "error": "A database error occurred while creating the asset."
        }), 500

    except Exception:
        db.session.rollback()
        app.logger.exception("Unexpected error while creating asset")
        return jsonify({
            "error": "An unexpected error occurred while creating asset."
        }), 500

    return jsonify(asset.to_dict()), 201

    #  Return success response
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


# 3. GET asset by Id
@app.route("/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):
    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return jsonify({"error": "Asset not found"}), 404

    return jsonify(asset.to_dict()), 200


# 4. Update assets by ID
@app.route("/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):
    # 1. Check whether asset exists and is active
    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return jsonify({"error": "Asset not found"}), 404

    # 2. Validate request body
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    # 3. Validate allowed fields
    allowed_fields = {
        "asset_name", "asset_tag", "category",
        "location", "purchase_date", "purchase_cost", "status"
    }

    if not data or not set(data).issubset(allowed_fields):
        return jsonify({
            "error": "Provide valid asset fields to update"
        }), 400

    for field in ("asset_name", "asset_tag", "category"):
        if field in data and (
            not isinstance(data[field], str) or not data[field].strip()
        ):
            return jsonify({
                "error": f"{field} cannot be empty"
            }), 400

    if unknown_fields:
        return jsonify({
            "error": "Invalid fields provided",
            "fields": sorted(unknown_fields)
        }), 400

    # 4. Validate required string fields when provided
    required_string_fields = {
        "asset_name": 100,
        "asset_tag": 50,
        "category": 100,
    }

    for field, max_length in required_string_fields.items():
        if field in data:
            value = data[field]

            if not isinstance(value, str) or not value.strip():
                return jsonify({
                    "error": f"{field} cannot be empty and must be a string"
                }), 400

            if len(value.strip()) > max_length:
                return jsonify({
                    "error": f"{field} must not exceed {max_length} characters"
                }), 400

    # 5. Validate optional location
    if "location" in data:
        location = data["location"]

        if location is not None and not isinstance(location, str):
            return jsonify({
                "error": "location must be a string or null"
            }), 400

        if isinstance(location, str) and len(location.strip()) > 100:
            return jsonify({
                "error": "location must not exceed 100 characters"
            }), 400

    # 6. Validate status
    if "status" in data:
        if data["status"] not in ("Active", "Inactive"):
            return jsonify({
                "error": "status must be Active or Inactive"
            }), 400

    # 7. Validate purchase date
    if "purchase_date" in data:
        purchase_date = data["purchase_date"]

        if purchase_date is None or purchase_date == "":
            asset.purchase_date = None
        else:
            if not isinstance(purchase_date, str):
                return jsonify({
                    "error": "purchase_date must use YYYY-MM-DD format"
                }), 400

            try:
                parsed_date = date.fromisoformat(purchase_date)

                if parsed_date.isoformat() != purchase_date:
                    raise ValueError

                asset.purchase_date = parsed_date

            except ValueError:
                return jsonify({
                    "error": "purchase_date must use YYYY-MM-DD format"
                }), 400

    # 8. Validate purchase cost
    if "purchase_cost" in data:
        cost = data["purchase_cost"]

        if cost is not None:
            if isinstance(cost, bool):
                return jsonify({
                    "error": "purchase_cost must be a number"
                }), 400

            try:
                cost = float(cost)

                if not math.isfinite(cost) or cost < 0:
                    raise ValueError

            except (ValueError, TypeError):
                return jsonify({
                    "error": "purchase_cost must be a finite, non-negative number"
                }), 400

        asset.purchase_cost = cost

    # 9. Update validated fields
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

    # 10. Save changes and handle database errors
    try:
        asset.updatedBy = "system"
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Asset update failed because of a database constraint conflict, such as a duplicate asset tag."
        }), 409

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception(
            "Database error while updating asset %s", asset_id
        )
        return jsonify({
            "error": "A database error occurred while updating the asset."
        }), 500

    except Exception:
        db.session.rollback()
        app.logger.exception(
            "Unexpected error while updating asset %s", asset_id
        )
        return jsonify({
            "error": "An unexpected error occurred while updating the asset."
        }), 500

    return jsonify(asset.to_dict()), 200

    # 11. Return updated asset
    return jsonify(asset.to_dict()), 200


# 5. Deactivate assets
@app.route("/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id):
    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return jsonify({"error": "Asset not found"}), 404

    try:
        asset.status = "Inactive"
        asset.updatedBy = "system"
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to deactivate asset")
        return jsonify({"error": "Internal server error"}), 500

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
        return jsonify({"error": "Asset not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

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
        app.logger.exception("Failed to add asset tags")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "message": "Tags added successfully",
        "asset_id": asset_id,
        "tags": [item.tag for item in created],
    }), 201

# 7. Get asset tags by id
@app.route("/assets/<int:asset_id>/tags", methods=["GET"])
def get_asset_tags(asset_id):
    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return jsonify({"error": "Asset not found"}), 404

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