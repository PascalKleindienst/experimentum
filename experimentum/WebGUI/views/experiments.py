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

blueprint = Blueprint('experiments', __name__)


def run_experiment(exp_thread, capturer):
    """Experiment runner, which monitors and yields the thread output.

    Args:
        exp_thread (Thread): Thread which runs the experiment.
        capturer (CapturedContent): Capturer the capture the thread output.
    """
    from time import sleep

    while exp_thread.isAlive():
        sleep(.1)  # artifical delay, otherwise loop runs to fast and misses some output :/
        error = capturer.has_error()
        content = capturer.get_text()

        # if there is data in the output stream, yield it to the event stream
        if content:
            yield 'data: {}\n\n'.format(json.dumps({'data': content, 'error': error}))
            capturer.clear()

    # Revert streams back to normal and finish event stream.
    capturer.revert()
    yield 'data: finished\n\n'


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
            'config': request.form['config']
        }
        return render_template('experiments/result.jinja', **context)

    # Run experiment and stream output log
    if request.headers.get('accept') == 'text/event-stream':
        # TODO: Use submitted config and iteration
        exp.show_progress = True

        # Run the experiment in a seperate thread, so we can monitor its output
        capturer = CapturedContent(True)
        func1_thread = Thread(target=lambda: exp.start(5))
        func1_thread.deamon = True
        func1_thread.start()

        return Response(run_experiment(func1_thread, capturer), content_type='text/event-stream')

    # Show experiment form
    return render_template('experiments/form.jinja', name=experiment, config=exp.config_file)


@blueprint.route('/plots/<experiment>')
def plots(experiment):
    """Show plots and charts for experiment.

    Args:
        experiment (str): Name of experiment

    Returns:
        str: HTML template
    """
    return render_template('experiments/plots.jinja')


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
