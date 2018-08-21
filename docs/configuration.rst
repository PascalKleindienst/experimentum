=============
Configuration
=============

All of the configuration files for the experimentum framework are stored in the ``config`` directory.

App Configuration
-----------------
The App configuration is stored in the ``app.json`` file and has to following options:

+--------------------------+----------------------------------------------+
| Option                   | Description                                  |
+==========================+==============================================+
| ``prog``                 | Name of the program file.                    |
+--------------------------+----------------------------------------------+
| ``description``          | Description of the program.                  |
+--------------------------+----------------------------------------------+
| ``logging.format``       | Log Format.                                  |
+--------------------------+----------------------------------------------+
| ``logging.level``        | Log Level.                                   |
+--------------------------+----------------------------------------------+
| ``logging.filename``     | Name of the Log file.                        |
+--------------------------+----------------------------------------------+
| ``logging.path``         | Path to the log file.                        |
+--------------------------+----------------------------------------------+
| ``logging.backup_count`` | Number of backups the log handler keeps.     |
+--------------------------+----------------------------------------------+
| ``logging.max_bytes``    | Maxium Bytes per log file. *(default 1MB)*   |
+--------------------------+----------------------------------------------+


Example Config:

.. code-block:: json

    {
        "prog": "main.py",
        "description": "Some Description",
        "logging": {
            "format": "[%(asctime)s] - [%(levelname)s] - [%(module)s] - %(message)s",
            "level": "info",
            "filename": "example_app.log",
            "path": "logs",
            "backup_count": 10,
            "max_bytes": 1048576
        }
    }


Storage Configuration
---------------------
The Database configuration is stored in the ``storage.json`` file and has to following options:

+--------------------------+---------------------------------------------------------------+
| Option                   | Description                                                   |
+==========================+===============================================================+
| ``datastore.drivername`` | Name of the database driver, e.g.                             |
|                          | ``postgresql``, ``mysql``, ``oracle``, ``mssql``, ``sqlite``. |
+--------------------------+---------------------------------------------------------------+
| ``datastore.database``   | Name of the database.                                         |
+--------------------------+---------------------------------------------------------------+
| ``datastore.username``   | Database Username.                                            |
+--------------------------+---------------------------------------------------------------+
| ``datastore.password``   | Database Password.                                            |
+--------------------------+---------------------------------------------------------------+
| ``datastore.host``       | Database host.                                                |
+--------------------------+---------------------------------------------------------------+
| ``datastore.port``       | Database port.                                                |
+--------------------------+---------------------------------------------------------------+
| ``migrations.path``      | Path to the migrations folder.                                |
+--------------------------+---------------------------------------------------------------+


Example Config:

.. code-block:: json

    {
        "datastore": {
            "drivername": "sqlite",
            "database": "experimentum.db",
            "username": null,
            "password": null,
            "host": null,
            "port": null
        },
        "migrations": {
            "path": "migrations"
        }
    }
