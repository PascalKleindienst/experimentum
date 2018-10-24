# -*- coding: utf-8 -*-
"""Contains all views/routes for the migrations.

Available Routes for:
    * Upgrading Migrations
    * Downgrading Migrations
    * Refreshing Migrations
    * Getting Migration Status
"""
from flask import Blueprint, current_app, jsonify, render_template, request
from experimentum.WebGUI.helpers import ansi_escape, capture_print


blueprint = Blueprint('migrations', __name__)


def get_migration_status():
    """Get the current migration status.

    Returns:
        list: list of migrations with their status (i.e. migrated or not)
    """
    status = current_app.config.get('container').make('migrator').status(printing=False)
    status = list(map(lambda s: [ansi_escape(s[0]), ansi_escape(s[1]).lower()], status))

    return status


@blueprint.route('/upgrade')
def upgrade():
    """Upgrade the migration and send a json status message.

    Returns:
        Response: json status message
    """
    response = None
    try:
        with capture_print(escape=True) as content:
            current_app.config.get('container').make('migrator').up()

        response = {'message': content.get_text(), 'status': 'success'}
    except SystemExit:
        response = {'message': content.get_text(), 'status': 'error'}

    return jsonify(response)


@blueprint.route('/downgrade')
def downgrade():
    """Downgrade the migration and send a json status message.

    Returns:
        Response: json status message
    """
    response = None
    try:
        with capture_print(escape=True) as content:
            current_app.config.get('container').make('migrator').down()

        response = {'message': content.get_text(), 'status': 'success'}
    except SystemExit:
        response = {'message': content.get_text(), 'status': 'error'}

    if '×' in response['message']:
        response['status'] = 'error'

    return jsonify(response)


@blueprint.route('/refresh')
def refresh():
    """Refresh all migrations and send a json status message.

    Returns:
        Response: json status message
    """
    current_app.config.get('container').make('migrator').refresh()
    return jsonify({'message': '› Refreshed all migrations', 'status': 'success'})


@blueprint.route('/make', methods=['POST'])
def make():
    """Make a new migration.

    Returns:
        Response: json status message
    """
    response = None
    try:
        with capture_print(escape=True) as content:
            current_app.config.get('container').make('migrator').make(request.form['name'])

        response = {'message': content.get_text(), 'status': 'success'}
    except SystemExit:
        response = {'message': content.get_text(), 'status': 'error'}

    return jsonify(response)


@blueprint.route('/status')
def status():
    """Return the migration status as an html template.

    Returns:
        Response: HTML migration status template
    """
    return jsonify(render_template('dashboard/migrations.jinja', migrations=get_migration_status()))
