"""Contains all views/routes for the dashboard.

The dashboard should:
* List all available experiments
* List all migrations and their status
    - Upgrade migrations
    - Downgrade migrations
    - Refresh Migrations
"""
from experimentum.WebGUI.views.migrations import get_migration_status
from experimentum.Experiments import Experiment
from flask import Blueprint, current_app, render_template

blueprint = Blueprint('dashboard', __name__)


@blueprint.route('/')
def dashboard():
    """Display the dashboard template.

    Returns:
        str: HTML Template
    """
    data = {
        'experiments': Experiment.get_status(current_app.config.get('container')),
        'migrations': get_migration_status(),
    }

    return render_template('dashboard/index.jinja', **data)
