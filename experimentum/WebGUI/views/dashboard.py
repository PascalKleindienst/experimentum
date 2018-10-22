"""Contains all views/routes for the dashboard.

The dashboard should:
* List all available experiments
* List all migrations and their status
    - Upgrade migrations
    - Downgrade migrations
    - Refresh Migrations
"""
from experimentum.WebGUI.views.migrations import get_migration_status
from flask import Blueprint, render_template

blueprint = Blueprint('dashboard', __name__)


@blueprint.route('/')
def dashboard():
    """Display the dashboard template.

    Returns:
        str: HTML Template
    """
    return render_template('dashboard/index.jinja', migrations=get_migration_status())
