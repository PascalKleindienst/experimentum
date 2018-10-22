"""Provides an easy to use web interface via flask.

Uses the Application Factory Pattern to create a new flask app instance.
"""
from flask import Flask


def create_app(container):
    """Create a new flask app.

    Uses the Application Factory Pattern: http://flask.pocoo.org/docs/1.0/patterns/appfactories/

    Args:
        container (App): Main Service Container

    Returns:
        Flask: Flask App
    """
    app = Flask(__name__)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.config['TESTING'] = True
    app.config['container'] = container

    # Add Blueprints
    from .views import dashboard
    app.register_blueprint(dashboard.blueprint)

    return app
