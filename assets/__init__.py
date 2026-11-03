from flask import Blueprint

# Parent Blueprint
assets_bp = Blueprint("assets", __name__)

# Import child blueprints
from .routes.asset_routes import asset_bp
from .routes.tag_routes import tag_bp

# Register child blueprints
assets_bp.register_blueprint(asset_bp)

assets_bp.register_blueprint(tag_bp)