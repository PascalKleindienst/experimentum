# -*- coding: utf-8 -*-
"""Dispatch and configure the flask web app.

Starting the Server
-------------------
Use the ```webgui`` command to dispatch a new server instance
(http://flask.pocoo.org/docs/1.0/patterns/appdispatch/#app-dispatch).


Options:

--debug      Enable the Debugger.
--port       Specifiy the port to run server on.
--no-reload  Disable the reload when file changes are detected.
-h, --help   Show the help message.
"""
from experimentum.Commands import command
from experimentum.WebGUI import create_app


@command(
    'Start a new web server to act as a GUI on localhost:5000.',
    arguments={
        '--port': {
            'help': 'Port number to start the server on', 'default': 5000, 'type': int
        },
        '--no-reload': {
            'help': 'Disable reload when file changes are detected', 'dest': 'reload', 'action': 'store_false'
        },
        '--debug': {
            'help': 'Enable the debugger', 'dest': 'debug', 'action': 'store_true'
        }
    },
    help='Starts a web server on localhost'
)
def start(app, args):
    """Start a simple server and run the flask app.

    Args:
        app (App): Main Service Container
        args (argparse.Namespace): Command Arguments and Options.
    """
    reloader = False if hasattr(args, 'reload') and args.reload is False else True
    debugger = True if hasattr(args, 'debug') and args.debug is True else False

    server = app.make('server')
    server.run(args.port, debugger, reloader)