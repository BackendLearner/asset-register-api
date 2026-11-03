from flask import Flask
from dotenv import load_dotenv
from models import db
from assets import assets_bp
import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///assets.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Register Parent Blueprint
app.register_blueprint(
    assets_bp,
    url_prefix="/assets"
)


@app.route("/")
def home():
    return "Welcome to the Asset Register API!"


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)