"""Provides an easy to use web interface via flask.

Uses the Application Factory Pattern to create a new flask app instance.
"""
from flask import Flask, render_template
from werkzeug.serving import run_simple
import os


class Server(object):

    def __init__(self, app):
        self.app = app

    def create_app(self):
        return create_app(self.app)

    def run(self, port=5000, debugger=False, reloader=True):
        run_simple(
            'localhost', port, self.create_app(), use_reloader=reloader,
            use_debugger=debugger, use_evalex=True, threaded=True
        )


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
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(container.root, '.tmp'))
    # app.config['TESTING'] = True
    app.config['container'] = container

    # 404 Page
    @app.errorhandler(404)
    def page_not_found(e):
        """Return 404 error page.

        Args:
            e (werkzeug.exceptions.NotFound): Error message

        Returns:
            Response: 404 Page
        """
        return render_template('404.jinja', msg=e), 404

    # Add Blueprints
    from .views import dashboard, migrations, experiments, plots
    app.register_blueprint(dashboard.blueprint)
    app.register_blueprint(migrations.blueprint, url_prefix='/migrations')
    app.register_blueprint(experiments.blueprint, url_prefix='/experiments')
    app.register_blueprint(plots.blueprint, url_prefix='/plots')

    return app
