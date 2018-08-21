============
Installation
============

Since experimentum is in its development stage you have to install it from its GitHub repository.

.. code-block:: bash

    pip install https://github.com/PascalKleindienst/experimentum/archive/master.tar.gz

or

.. code-block:: bash

    pip install git+ssh://git@github.com/PascalKleindienst/experimentum.git#egg=experimentum

.. note::
    The different ``dbapi`` packages are not part of the package dependencies, so you must install them in order to connect to corresponding databases:

    * PostgreSQL: ``psycopg2``
    * MySQL: ``PyMySQL`` or ``mysqlclient``
    * Oracle: ``cx_oracle``
    * Microsoft SQL Server: ``pyodbc`` or ``pymssql``
    * SQLite: The ``sqlite3`` module is bundled with Python by default

Getting Started
---------------
All you need to get you started is an ``app.json`` config file and creating a new class derived from the ``experimentum.Experiments.App`` class where you set the path to the config folder.
To start the framework just call the ``run``-method of the new ``App`` class.

All needed files and a derived ``App`` class can be generated with the ``experimentum-quickstart`` command (see `Quickstart`_)

Example ``MyApp`` class:

.. code-block:: python

    from experimentum.Experiments import App

    class MyApp(App):

        """Main Entry Point of the Framework.

        Arguments:
            config_path {string} -- Path to config files (default: {'.'})
        """
        config_path = 'config'

    if __name__ == '__main__':
        app = MyApp('MyApp')  # Name of the app.
        app.run()

Quickstart
----------
.. automodule:: experimentum.quickstart
