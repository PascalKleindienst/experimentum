# Experimentum Example Application
This folder contains an example application to illustrate how the framework can be used to create/execute experiments and how to analyze and visualize them. This README will roughly explain how to such an example was created with the framework.

## Table of Contents
- [Experimentum Example Application](#experimentum-example-application)
  - [Table of Contents](#table-of-contents)
  - [Prerequisite](#prerequisite)
  - [Initialization](#initialization)
  - [Custom Command](#custom-command)

## Prerequisite
You already have installed Python & pip and the experimentum framework.

## Initialization
At first we need to initialize the base files and folders. To do that the frameworks provides the `experimentum-quickstart` command:

~~~console
$ experimentum-quickstart --root example
Welcome to the experimentum 1.0.0 quickstart utility.

Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets)

Selected root path: example

› Enter the name of the config folder [config]:
› Enter the name of the migrations folder [migrations]:
› Enter the name of the repositories folder [repositories]:
› Enter the name of the experiments folder [experiments]:
› Enter the name of the logs folder [logs]:
› Enter the name of the app: Example App
› Enter the description of the app []: This is an example on how to use the experimentum framework.
› Enter the name of the program [main.py]:

Creating folders ...
Creating main entry point ...
Creating config files ...
Creating migrations ...
Creating repositories ...
Done.
~~~

## Custom Command
To create a new custom command for the framework we create a new `commands` package and place a `LoremIpsum.py` file inside it which contains our command. This is not required as the command handlers only must either be derived from `AbstractCommand` or a function with the decorator `AbstractCommand.command()`. But placing all commands inside a dedicated package or module keeps things well-organized. A shortened example for a command which displays some 'lorem ipsum' text could look like this:

~~~python
from experimentum.Commands import command


@command(
    'Displays between one and ten lorem ipsum sentences.',
    arguments={
        'sentences': {'type': int, 'action': 'store', 'help': 'Number of sentences'}
    }
)
def lorem(app, args):
    """Display lorem ipsum text."""
    content = [
        "Lorem ipsum dolor sit amet, ...",
        "At vero eos et accusam et justo duo dolores et ea rebum.",
        # ...
    ]

    # Clamp sentences between 1 and 10
    sentences = max(0, min(args.sentences, 10))

    print(' '.join(content[:sentences])
~~~

Lastly we need to register our commands so the framework knows about them. Therefore, in the `main.py` file we add the following method to the `ExampleApp` class:

~~~python
def register_commands(self):
    """Register Custom Commands.

    Returns:
        dict: { Name of command : Command Handler }
    """
    from commands.LoremIpsum import lorem

    return {
        'lorem': lorem
    }
~~~

Now, if `python main.py lorem 2` is called for example it will display two "lorem ipsum"-sentences.