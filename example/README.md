# Experimentum Example Application <!-- omit in toc -->
This folder contains an example application to illustrate how the framework can be used to create/execute experiments and how to analyze and visualize them. This README will roughly explain how to such an example was created with the framework.

## Table of Contents <!-- omit in toc -->
- [Prerequisite](#prerequisite)
- [Initialization](#initialization)
- [Database Schema](#database-schema)
  - [Migrations](#migrations)
    - [Creating Migrations](#creating-migrations)
    - [Running Migrations](#running-migrations)
    - [Reverting Migrations](#reverting-migrations)
    - [Status of Migrations](#status-of-migrations)
  - [Repositories](#repositories)
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
After the framework is initialized with the `experimentum-quickstart` command, it is time to setup the needed database tables. By default the framework will use a *SQLite* database, but this can be changed in the `config/storage.json` configuration file *(more information can be found in the [documentation](https://pascalkleindienst.github.io/experimentum/configuration.html#storage-configuration))*. To (re-)create the tables run the following command, which will effectivly delete and then create all tables again:

~~~console
$ python main.py migration:refresh
--- Downgrading Migrations ---

--- Upgrading Migrations ---
› Migrated 20190409115619_create_experiments
› Migrated 20190409115620_create_testcase
› Migrated 20190409115621_create_performance
~~~

### Migrations
#### Creating Migrations
For our example experiment we want to extend the default testcase table with some columns to save our experiment results. Changing the database schema is done through [migrations](https://pascalkleindienst.github.io/experimentum/migrations.html). First, we need to make a new migration file. This can easily be done with the following command:

~~~console
$ python main.py migration:make "Add Testcase Data"
~~~

The migration file contains two methods which need to be filled. The first one is the `up`-method, which handles the new changes to the database schema. In this example, a new `integer` column called `value` is called.

~~~python
def up(self):
    """Run the migrations."""
    with self.schema.table('testcases') as table:
        table.integer('value')
~~~

The second method is called `down` and it will revert the changes made in the `up`-method:
~~~python
def down(self):
    """Revert the migrations."""
    with self.schema.table('testcases') as table:
        table.drop_column('value')
~~~

#### Running Migrations
To run the migrations, simply execute the following command:
~~~console
$ python main.py migration:up
~~~

#### Reverting Migrations
If you want to revert to an older version of your database schema simply run the down command:

~~~console
$ python main.py migration:down
~~~

#### Status of Migrations
The status information if migrations, i.e. whether they were already executed or not, is saved locally in the `migrations/.version` file. If you work in a team, make sure to share this file with them. To display the status in a human-readable format, run the following command:

~~~console
$ python main.py migration:status
+-----------------------------------+--------+
| Migration                         | Ran?   |
|-----------------------------------+--------|
| 20190409115619_create_experiments | Yes    |
| 20190409115620_create_testcase    | Yes    |
| 20190409115621_create_performance | Yes    |
| 20190411131223_add_testcase_data  | No     |
+-----------------------------------+--------+
~~~

### Repositories
While [migrations](https://pascalkleindienst.github.io/experimentum/migrations.html) define the data schema on the database side, [repositories](https://pascalkleindienst.github.io/experimentum/repositories.html) act like an in-memory domain object collections, that connect the domain and data mapping layers. Objects can be easily added to and removed from the [repositories](https://pascalkleindienst.github.io/experimentum/repositories.html), due to the mapping code of the [repositories](https://pascalkleindienst.github.io/experimentum/repositories.html) which will ensure that the right operations are executed behind the scenes.

Each table you created with migrations is represented by a [repority](https://pascalkleindienst.github.io/experimentum/repositories.html). Therefore, we have to modify the `TestCaseRepository` according to the changes we made in the previous migration *(i.e. add the `value` column)*. To do that we simply have to set the value via the constructor like this:

~~~python
class TestCaseRepository(AbstractRepository.implementation):
    # ...
    def __init__(self, iteration, value, experiment_id=None):
        """Set attributes."""
        self.iteration = iteration
        self.value = value  # Our custom column we created earlier
        self.experiment_id = experiment_id
~~~


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

Now the new command can be used to display the lorem-ipsum sentences:
~~~console
$ python main.py lorem 2
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod temporinvidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
~~~