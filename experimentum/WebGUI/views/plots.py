"""Contains all views/routes for the plots.

Available Routes for:
    * Generating plots of an experiment
    * Exporting plots of an experiment
    * Serving plot image files
"""
from flask import Blueprint, current_app, send_from_directory, jsonify, url_for, send_file,\
    abort, redirect
from werkzeug.utils import secure_filename
import os
import shutil
import tempfile


blueprint = Blueprint('plots', __name__)


def generate_plots(directory, container, experiment):
    """Generate all plots for an experiment.

    Args:
        directory (str): Plot Upload directory.
        container (App): Service Container.
        experiment (str): Name of the experiment.

    Returns:
        list: list of status messages.
    """
    # Find plots for experiment and generate them
    messages = []
    config = container.config.get('plots', {})

    # create experiment plot dir if not exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    for name, cfg in config.items():
        if cfg.get('experiment') == experiment:
            # try to plot and save as svg
            try:
                plot = container.make('plot', name)
                plt = plot.plotting()
                plt.savefig(os.path.join(directory, name + '.svg'))

                messages.append({
                    'message': 'Generated plot: ' + name,
                    'status': 'success',
                    'file': url_for('plots.image', experiment=experiment, filename=name + '.svg')
                })
            except Exception as exc:
                messages.append({'message': 'Error generating plot {}: {}'.format(name, exc), 'status': 'error', 'file': None})

    return messages


@blueprint.route('/export/<experiment>')
def export(experiment):
    """Download all plots for an experiment.

    Args:
        experiment (str): Name of the experiment.

    Returns:
        Response: File Download
    """
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], experiment)
    tmpfile = os.path.join(tempfile.gettempdir(), 'export-' + experiment)
    shutil.make_archive(tmpfile, 'zip', directory)

    try:
        return send_file(tmpfile + '.zip', as_attachment=True)
    except Exception as exc:
        current_app.config.get('container').log.error(exc)
        abort(400)


@blueprint.route('/generate/<experiment>')
def generate(experiment):
    """Generate all plots for an experiment.

    Args:
        experiment (str): Name of the experiment.

    Returns:
        Response: Redirects to plot overview.
    """
    # Find plots for experiment and generate them
    container = current_app.config.get('container')
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], experiment)
    generate_plots(directory, container, experiment)
    return redirect(url_for('experiments.plots', experiment=experiment))


@blueprint.route('/generate_ajax/<experiment>')
def generate_ajax(experiment):
    """Genereate all plots for an experiment.

    Args:
        experiment (str): Name of the experiment.

    Returns:
        str: JSON with status messages
    """
    # Find plots for experiment and generate them
    container = current_app.config.get('container')
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], experiment)
    messages = generate_plots(directory, container, experiment)
    return jsonify(messages)


@blueprint.route('/image/<experiment>/<filename>')
def image(experiment, filename):
    """Serve plot images from the plot graphics directory.

    Args:
        experiment (str): Name of the experiment.
        filename (str): Name of the plot.

    Returns:
        obj: Plot graphics
    """
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER'], experiment),
        secure_filename(filename)
    )
