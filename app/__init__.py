# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Initialise the SQLAlchemy object (shared across the app)
db = SQLAlchemy()


def create_app():
    """Application factory for the PancrePal Flask app."""
    # Load environment variables from .env file if it exists
    load_dotenv()

    app = Flask(__name__)

    # ------------------------------
    # ✅ Basic App Configuration
    # ------------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # Database URL (defaults to Postgres but falls back safely)
    default_db_uri = "postgresql://pancre_user:postgres@localhost:5432/pancrepal_db"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pancrepal_demo.db"

    # Disable overhead from modification tracking
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ------------------------------
    # ✅ Initialise the database
    # ------------------------------
    db.init_app(app)

    # ------------------------------
    # ✅ Register Blueprints
    # ------------------------------
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # ------------------------------
    # ✅ Create tables on first run
    # ------------------------------
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables ready.")
            print("Connected to:", app.config["SQLALCHEMY_DATABASE_URI"])
        except Exception as e:
            print("⚠️ Database connection failed:", e)

    # ------------------------------
    # ✅ Optional Health Route (for testing)
    # ------------------------------
    @app.route("/health")
    def health():
        return {"status": "ok", "database": str(db.engine.url)}

    # ------------------------------
    # ✅ Return the Flask app instance
    # ------------------------------
    return app
