import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    default_db_uri = f"sqlite:///{os.path.join(basedir, 'tweets.db')}"

    database_url = os.getenv("DATABASE_URL", default_db_uri)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True, "pool_recycle": 300},
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "change-this-jwt-secret"),
        SECRET_KEY=os.getenv("SECRET_KEY", "change-this-flask-secret"),
        PROPAGATE_EXCEPTIONS=True,
    )

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import bp as api_bp

    app.register_blueprint(api_bp)

    return app
