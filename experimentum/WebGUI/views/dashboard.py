"""Contains all views/routes for the dashboard.

The dashboard lists:
* all available experiments
* all migrations and their status
  * Upgrade migrations
  * Downgrade migrations
  * Refresh Migrations
"""
from experimentum.WebGUI.views.migrations import get_migration_status
from experimentum.Experiments import Experiment
from flask import Blueprint, current_app, render_template
from sqlalchemy.exc import InvalidRequestError

blueprint = Blueprint('dashboard', __name__)


@blueprint.route('/')
def dashboard():
    """Displays the dashboard template.

    Returns:
        str: HTML Template
    """
    data = {}

    try:
        data = {
            'experiments': Experiment.get_status(current_app.config.get('container')),
            'migrations': get_migration_status(),
        }
    except InvalidRequestError as exc:
        current_app.config.get('container').log.critical(exc)
        data = {
            'error': 'There seems to be an error with your database. \
            Please try to refresh your migrations and restart the webgui to resolve this problem.',
            'migrations': get_migration_status(),
        }

    return render_template('dashboard/index.jinja', **data)
