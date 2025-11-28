import pytest
import os
import tempfile
from app import create_app, db
from app.utils.config import Config

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        MODELS_DIR = tempfile.mkdtemp()

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

    yield app

    # Cleanup - close database connections first
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    # Force close all connections
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
    except:
        pass

    # Close file descriptor and remove files
    try:
        os.close(db_fd)
        os.unlink(db_path)
    except:
        pass

    import shutil
    try:
        shutil.rmtree(TestConfig.MODELS_DIR)
    except:
        pass

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
