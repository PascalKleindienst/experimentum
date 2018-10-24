"""Contains all views/routes for the experiments.

It should call ``experiments:run`` to run an experiment,
show the ouput log and performance table, and show the
generated plots and charts if available.

Available Routes for:
    * Running Experiments
    * Showing Plots and Charts of experiments
"""
from flask import Blueprint, Response, request, render_template

blueprint = Blueprint('experiments', __name__)

# Fake output data
data = [
    ' * Loading Experiment "XYZ": okay',
    ' * Config File: foo.json',
    ' * Iterations: 100',
    ' * Could not load plot "XYZ": NotFoundException in xyz.py on line 42',
    ' * Loading Plot "abc": okay',
    ' * Loading Plot "uvw": okay',
    ' * Generating Plot "abc": okay',
    ' * Generating Plot "uvw": okay'
]


def run_experiment():
    """Fake runner for experiments, yields output log to event-stream."""
    import json
    from time import sleep
    sleep(1.5)  # artifical delay

    for idx, item in enumerate(data):
        yield "data: {}\n\n".format(json.dumps({'data': item, 'error': idx == 3}))
        sleep(.3)  # artifical delay

    yield 'data: finished\n\n'


@blueprint.route('/run/<experiment>', methods=['GET', 'POST'])
def run(experiment):
    """Run an experiment.

    Args:
        experiment (str): Name of the experiment

    Returns:
        str|Response: HTML template, or event stream for experiment log
    """
    # Show results page for experiment
    if request.method == 'POST':
        context = {
            'iterations': request.form['iterations'],
            'config': request.form['config']
        }
        return render_template('experiments/result.jinja', **context)

    # Run experiment and stream output log
    if request.headers.get('accept') == 'text/event-stream':
        return Response(run_experiment(), content_type='text/event-stream')

    # Show experiment form
    return render_template('experiments/form.jinja', name=experiment)


@blueprint.route('/plots/<experiment>')
def plots(experiment):
    """Show plots and charts for experiment.

    Args:
        experiment (str): Name of experiment

    Returns:
        str: HTML template
    """
    return render_template('experiments/results.jinja')


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
