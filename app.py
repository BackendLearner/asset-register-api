from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import date
from models import db, Asset, AssetTag
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


@app.route("/hello")
def hello():
    return "Hello! Your API is working."


@app.route("/assets", methods=["POST"])
def create_asset():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required_fields = ["asset_name", "asset_tag", "category"]
    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({"error": f"{field} is required"}), 400

    purchase_date = None
    if data.get("purchase_date"):
        try:
            purchase_date = date.fromisoformat(data["purchase_date"])
        except (ValueError, TypeError):
            return jsonify({
                "error": "purchase_date must use YYYY-MM-DD format"
            }), 400

    purchase_cost = data.get("purchase_cost")
    if purchase_cost is not None:
        if isinstance(purchase_cost, bool):
            return jsonify({"error": "purchase_cost must be a number"}), 400
        try:
            purchase_cost = float(purchase_cost)
            if not math.isfinite(purchase_cost) or purchase_cost < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "error": "purchase_cost must be a non-negative number"
            }), 400

    asset = Asset(
        asset_name=data["asset_name"].strip(),
        asset_tag=data["asset_tag"].strip(),
        category=data["category"].strip(),
        location=data.get("location"),
        purchase_date=purchase_date,
        purchase_cost=purchase_cost,
        status="Active",
    )

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



@app.route("/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):
    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return jsonify({"error": "Asset not found"}), 404

    return jsonify(asset.to_dict()), 200



@app.route("/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):
    asset = db.session.get(Asset, asset_id)

    if asset is None or asset.status != "Active":
        return jsonify({"error": "Asset not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

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

    if "purchase_date" in data:
        try:
            asset.purchase_date = (
                date.fromisoformat(data["purchase_date"])
                if data["purchase_date"] else None
            )
        except (ValueError, TypeError):
            return jsonify({
                "error": "purchase_date must use YYYY-MM-DD format"
            }), 400

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
                    "error": "purchase_cost must be a non-negative number"
                }), 400

        asset.purchase_cost = cost

    for field in ("asset_name", "asset_tag", "category"):
        if field in data:
            setattr(asset, field, data[field].strip())

    for field in ("location", "status"):
        if field in data:
            setattr(asset, field, data[field])

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




if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)