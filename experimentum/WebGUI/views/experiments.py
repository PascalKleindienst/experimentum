# -*- coding: utf-8 -*-
"""Contains all views/routes for the experiments.

It should call ``experiments:run`` to run an experiment,
show the ouput log and performance table, and show the
generated plots and charts if available.

Available Routes for:
    * Running Experiments
    * Showing Plots and Charts of experiments
"""
from flask import Blueprint, Response, request, render_template, current_app, abort
from experimentum.WebGUI.helpers import CapturedContent
from threading import Thread
import json
import os

blueprint = Blueprint('experiments', __name__)


def run_experiment(exp_thread, capturer, experiment):
    """Experiment runner, which monitors and yields the thread output.

    Args:
        exp_thread (Thread): Thread which runs the experiment.
        capturer (CapturedContent): Capturer the capture the thread output.
        experiment (Experiment): experiment measurement.
    """
    from time import sleep
    from experimentum.WebGUI.helpers import ansi_escape

    yield 'data: {}\n\n'.format(json.dumps({'type': 'started'}))

    while exp_thread.isAlive():
        sleep(.1)  # artifical delay, otherwise loop runs to fast and misses some output :/
        error = capturer.has_error()
        content = capturer.get_text()

        # if there is data in the output stream, yield it to the event stream
        if content:
            data = {'data': content, 'error': error, 'type': 'log'}
            yield 'data: {}\n\n'.format(json.dumps(data))
            capturer.clear()

    # get performance table
    points = experiment.performance.export(metrics=True)
    table = ansi_escape(experiment.performance.formatter.get_table(points, 'html'))
    yield 'data: {}\n\n'.format(json.dumps({'table': table, 'type': 'table'}))

    # Revert streams back to normal and finish event stream.
    capturer.revert()
    data = {
        'start': experiment.repos['experiment'].start.isoformat(),
        'finished': experiment.repos['experiment'].finished.isoformat(),
        'config_file': experiment.repos['experiment'].config_file,
        'config_content': experiment.repos['experiment'].config_content
    }
    yield 'data: {}\n\n'.format(json.dumps({'data': data, 'type': 'finished'}))


@blueprint.route('/run/<experiment>', methods=['GET', 'POST'])
def run(experiment):
    """Run an experiment.

    Args:
        experiment (str): Name of the experiment

    Returns:
        str|Response: HTML template, or event stream for experiment log
    """
    # Try to load the experiment
    try:
        exp = current_app.config.get('container').make('experiment', experiment)
    except SystemExit:
        abort(404)

    # Show results page for experiment
    if request.method == 'POST':
        context = {
            'iterations': request.form['iterations'],
            'config': request.form['config'],
            'experiment': experiment
        }
        return render_template('experiments/result.jinja', **context)

    # Run experiment and stream output log
    elif request.headers.get('accept') == 'text/event-stream':
        # Use submitted config and iteration
        exp.show_progress = True
        exp.config_file = request.args.get('config')
        iterations = int(request.args.get('iterations', 100))

        # Run the experiment in a seperate thread, so we can monitor its output
        capturer = CapturedContent(True)
        exp_thread = Thread(target=lambda: exp.start(iterations))
        exp_thread.deamon = True
        exp_thread.start()

        return Response(
            run_experiment(exp_thread, capturer, exp),
            content_type='text/event-stream'
        )

    # Show experiment form
    return render_template('experiments/form.jinja', name=experiment, config=exp.config_file or '')


@blueprint.route('/plots/<experiment>')
def plots(experiment):
    """Show plots and charts for experiment.

    Args:
        experiment (str): Name of experiment

    Returns:
        str: HTML template
    """
    from werkzeug.utils import secure_filename

    path = os.path.join(current_app.config['UPLOAD_FOLDER'], experiment)
    if not os.path.exists(path):
        os.makedirs(path)

    plots = [f for f in os.listdir(path) if not f.startswith('.')]
    data = {
        'experiment': experiment,
        'plots': map(lambda f: secure_filename(f), plots)
    }

    return render_template('experiments/plots.jinja', **data)


# @blueprint.route('/streaming')
# def stream():
#     from flask import current_app, stream_with_context
#     def stream_template(template_name, **context):
#         current_app.update_template_context(context)
#         t = current_app.jinja_env.get_template(template_name)
#         rv = t.stream(context)
#         # uncomment if you don't need immediate reaction
#         # rv.enable_buffering(5)
#         return rv

#     def generate():
#         from time import sleep
#         sleep(1.5)
#         for idx, item in enumerate(data):
#             yield {'data': item, 'error': idx == 3}
#             sleep(.3)  # artifical delay

#     return Response(stream_with_context(stream_template('streaming.html', rows=generate())))
