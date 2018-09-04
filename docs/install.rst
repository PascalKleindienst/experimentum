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
In order to use the experimentum framework, you'll have to take care of some initial setup. You'll need to auto-generate some
code that creates the config files, migrations, repositories and other application-specific settings.

From the command line, ``cd`` into a directory where you would like to store your code, and then run the following command::

    experimentum-quickstart

After you answered the questions it will create the files and folders in this directory. If you want to create the project in
a subdirectory you can add the ``--root`` option to the command, like so::

    experimentum-quickstart --root myproject

This willl create a **myproject** directory in your current directoy.

The quickstart command will have created the following::

    /
        config/
            app.json
            storage.json
        experiments/
            __init__.py
        logs/
        migrations/
            {TIMESTAMP}_create_experiments.py
            {TIMESTAMP}_create_testcase.py
            {TIMESTAMP}_create_performance.py
        repositories/
            __init__.py
            ExperimentRepository.py
            PerformanceRepository.py
            TestcaseRepository.py
        main.py

These files are:

main.py
    The main entry point of the framework. It lets you interact with the experimentum framework via the command line.

config/
    Contains all configuration files. You can place you own configuration files here. All \*.json files will be loaded
    by the framework and available via the :py:class:`~experimentum.Config.Config` class under the
    :py:attr:`~experimentum.Experiments.App.App.config` attribute of the :py:class:`~experimentum.App.App` class.

config/app.json and storage.json
    Framework related settings. For more information see :ref:`configuration`

experiments/
    Here you can place your experiments and their configrations.

logs/
    Contains the log files.

migrations/
    Your migration files are placed here.

migrations/{TIMESTAMP}_create_experiments.py
    Migration for creating the experiments table.

migrations/{TIMESTAMP}_create_testcase.py
    Migration for creating the testcase table.

migrations/{TIMESTAMP}_create_performance.py
    Migration for creating the performance table.

repositories/ExperimentRepository.py
    Repository for experiment data.

repositories/TestcaseRepository.py
    Repository for testcase data.

repositories/PerformanceRepository.py
    Repository for performance data.

