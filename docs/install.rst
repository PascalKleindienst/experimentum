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

Quickstart
----------
In order to create all needed files and folders *(including config and migrations)* the experimentum framework contains a quickstart command.
Just run ``experimentum-quickstart`` and answer the questions.

You can also add a different root path with the ``--root`` option, e.g.::

    experimentum-quickstart --root example