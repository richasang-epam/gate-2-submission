from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    from app.api.routes import api_bp
    from app.dashboard.routes import dashboard_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp)

    return app
