# -*- coding: utf-8 -*-
"""Dispatch and configure the flask web app.

Starting the Server
-------------------
Use the ```webgui`` command to dispatch a new server instance
(http://flask.pocoo.org/docs/1.0/patterns/appdispatch/#app-dispatch).
"""
from experimentum.Commands import command
from experimentum.WebGUI import create_app
from werkzeug.serving import run_simple


@command(
    'Start a new web server to act as a GUI on localhost:5000.',
    help='Starts a web server on localhost'
)
def start(app, args):
    """Start a simple server and run the flask app.

    Args:
        app (App): Main Service Container
        args (argparse.Namespace): Command Arguments and Options.
    """
    run_simple(
        'localhost', 5000, create_app(app), use_reloader=True,
        use_debugger=True, use_evalex=True, threaded=True
    )
