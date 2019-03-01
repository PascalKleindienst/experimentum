"""Provides an easy to use web interface via flask.

Uses the Application Factory Pattern to create a new flask app instance.
"""
from flask import Flask, render_template
from werkzeug.serving import run_simple
import os


class Server(object):

    """Simple wrapper for the webserver."""

    def __init__(self, app, testing=False):
        """Init the server.

        Args:
            app (App): Main Service Container.
            testing (bool, optional): Defaults to False. Enable/Disable test mode.
        """
        self.app = app
        self.testing = testing

    def create_app(self):
        """Create a new flask application.

        Returns:
            Flask: Flask App
        """
        if self.testing:
            return create_app(self.app, {'TESTING': True})

        return create_app(self.app)

    def run(self, port=5000, debugger=False, reloader=True):
        """Run the server.

        Args:
            port (int, optional): Defaults to 5000. Port to run on.
            debugger (bool, optional): Defaults to False. Enable/Disable Debugger.
            reloader (bool, optional): Defaults to True. Enable/Disable Reloader.
        """
        run_simple(
            'localhost', port, self.create_app(), use_reloader=reloader,
            use_debugger=debugger, use_evalex=True, threaded=True
        )


def create_app(container, test_config=None):
    """Create a new flask app.

    Uses the Application Factory Pattern: http://flask.pocoo.org/docs/1.0/patterns/appfactories/

    Args:
        container (App): Main Service Container
        test_config (dict, optional): Defaults to None. Test Configuration

    Returns:
        Flask: Flask App
    """
    # Create Flask App
    app = Flask(__name__, instance_relative_config=True)
    app.jinja_env.auto_reload = True
    app.config.from_mapping(
        # Auto-reload templates on change
        TEMPLATES_AUTO_RELOAD=True,

        # Folder where plots are stored
        UPLOAD_FOLDER=os.path.abspath(os.path.join(container.root, '.tmp'))
    )
    app.config['container'] = container

    # load the instance config, if it exists, when not testing, or the test_config
    if test_config is None:
        app.config.update(container.config.get('app.webgui', {}))
    else:
        app.config.update(test_config)

    # 404 Page
    @app.errorhandler(404)
    def page_not_found(err):
        """Return 404 error page.

        Args:
            err (werkzeug.exceptions.NotFound): Error message

        Returns:
            Response: 404 Page
        """
        return render_template('404.jinja', msg=err), 404

    # Add Blueprints
    from .views import dashboard, migrations, experiments, plots
    app.register_blueprint(dashboard.blueprint)
    app.register_blueprint(migrations.blueprint, url_prefix='/migrations')
    app.register_blueprint(experiments.blueprint, url_prefix='/experiments')
    app.register_blueprint(plots.blueprint, url_prefix='/plots')

    return app
