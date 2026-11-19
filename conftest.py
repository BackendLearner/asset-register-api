import pytest
from flask import Flask

from app import app as original_app
from routes import asset_bp
from models import db


@pytest.fixture
def client():

    test_app = Flask(__name__)

    test_app.config["TESTING"] = True
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(test_app)

    test_app.register_blueprint(
        asset_bp,
        url_prefix="/assets"
    )

    # Reuse the original application's error handlers
    for exception, handler in original_app.error_handler_spec[None][None].items():
        test_app.register_error_handler(exception, handler)

    with test_app.app_context():
        db.create_all()

        yield test_app.test_client()

        db.session.remove()
        db.drop_all()
        db.engine.dispose()