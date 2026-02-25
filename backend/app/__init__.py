from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from .config import Config
from .models import db
from .swagger_config import SWAGGER_CONFIG, SWAGGER_TEMPLATE


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    from .routes import register_routes

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
