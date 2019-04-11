# Experimentum Example Application <!-- omit in toc -->
This folder contains an example application to illustrate how the framework can be used to create/execute experiments and how to analyze and visualize them. This README will roughly explain how to such an example was created with the framework.

## Table of Contents <!-- omit in toc -->
- [Prerequisite](#prerequisite)
- [Initialization](#initialization)
- [Database Schema](#database-schema)
  - [Creating Migrations](#creating-migrations)
  - [Running Migrations](#running-migrations)
  - [Creating Repositories](#creating-repositories)
- [Creating an experiment](#creating-an-experiment)
  - [Running an experiment](#running-an-experiment)
- [Creating Plots](#creating-plots)
  - [Generating Plots](#generating-plots)
- [Starting the Web-Interface](#starting-the-web-interface)
- [Adding Custom Commands](#adding-custom-commands)

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

## Database Schema
After the framework is initialized with the `experimentum-quickstart` command, it is time to setup the needed database tables. By default the framework will use a *SQLite* database, but this can be changed in the `config/storage.json` configuration file *(more information can be found in the [documentation](https://pascalkleindienst.github.io/experimentum/configuration.html#storage-configuration))*. To create the tables run the following command:

~~~console
$ python main.py migration:refresh
--- Downgrading Migrations ---

--- Upgrading Migrations ---
› Migrated 20190409115619_create_experiments
› Migrated 20190409115620_create_testcase
› Migrated 20190409115621_create_performance
~~~

### Creating Migrations
For our example experiment we want to extend the default testcase table with some columns to save our experiment results. Changing the database schema is done through [migrations](https://pascalkleindienst.github.io/experimentum/migrations.html). First, we need to make a new migration file. This can easily be done with the following command:

~~~console
$ python main.py migration:make "Add Testcase Data"
~~~

The migration file contains two methods which need to be filled. The first one is the `up`-method, which handles the new changes to the database schema. In this example, a new `integer` column called `random_value` is called.

~~~python
def up(self):
    """Run the migrations."""
    with self.schema.table('testcases') as table:
        table.integer('random_value')
~~~

The second method is called `down` and it will revert the changes made in the `up`-method:
~~~python
def down(self):
    """Revert the migrations."""
    with self.schema.table('testcases') as table:
        table.drop_column('random_value')
~~~

### Running Migrations
~~~console
$ python main.py migration:up
~~~

### Creating Repositories


## Creating an experiment

### Running an experiment

## Creating Plots
### Generating Plots

## Starting the Web-Interface

## Adding Custom Commands
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

    # Clamp sentences to content range
    sentences = max(0, min(args.sentences, len(content)-1))

    print(' '.join(content[:sentences]))
~~~

Lastly we need to register our commands so the framework knows about them. Therefore, in the `main.py` file we add the following method to the `ExampleApp` class:

~~~python
class ExampleApp(App):
    # ...
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

Now, if `python main.py lorem 2` is called for example, it will display two "lorem ipsum"-sentences.