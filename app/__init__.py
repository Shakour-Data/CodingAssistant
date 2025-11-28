from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.utils.config import Config
import os

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize CORS
    CORS(app)

    # Create models directory if it doesn't exist
    os.makedirs(app.config['MODELS_DIR'], exist_ok=True)
    os.makedirs(os.path.join(app.config['MODELS_DIR'], 'downloads'), exist_ok=True)
    os.makedirs(os.path.join(app.config['MODELS_DIR'], 'running'), exist_ok=True)

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    return app
