# Experimentum [![Build Status][build-status-badge]][build-status-link] [![Codacy grade][codacy-quality-badge]][codacy-quality-link] [![Codacy coverage][codacy-coverage-badge]][codacy-coverage-link]

## Installation
Since experimentum is in its development stage you have to install it from its GitHub repository.

`pip install https://github.com/PascalKleindienst/experimentum/archive/master.tar.gz`

or 

`pip install git+ssh://git@github.com/PascalKleindienst/experimentum.git#egg=experimentum`

>The different ``dbapi`` packages are not part of the package dependencies, so you must install them in order to connect to corresponding databases:
>* PostgreSQL: ``psycopg2``
>* MySQL: ``PyMySQL`` or ``mysqlclient``
>* Oracle: ``cx_oracle``
>* Microsoft SQL Server: ``pyodbc`` or ``pymssql``
>* SQLite: The ``sqlite3`` module is bundled with Python by default

### Getting Started
In order to use the experimentum framework, you’ll have to take care of some initial setup. You’ll need to auto-generate some code that creates the config files, migrations, repositories and other application-specific settings.

From the command line, `cd` into a directory where you would like to store your code, and then run the following command:

`experimentum-quickstart`

After you answered the questions it will create the files and folders in this directory. If you want to create the project in a subdirectory you can add the `--root` option to the command, like so:

`experimentum-quickstart --root myproject`

This willl create a **myproject** directory in your current directoy. The quickstart command will have created the following:
```
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
```
These files are:

- **main.py**: The main entry point of the framework. It lets you interact with the experimentum framework via the command line.
- **config/**: Contains all configuration files. You can place you own configuration files here. All *.json files will be loaded by the framework and available via the Config class under the config attribute of the App class.
- **config/app.json** and **storage.json**: Framework related settings. For more information see Configuration
- **experiments/**: Here you can place your experiments and their configrations.
- **logs/**: Contains the log files.
- **migrations/**: Your migration files are placed here.
- **migrations/{TIMESTAMP}_create_experiments.py**: Migration for creating the experiments table.
- **migrations/{TIMESTAMP}_create_testcase.py**: Migration for creating the testcase table.
- **migrations/{TIMESTAMP}_create_performance.py**: Migration for creating the performance table.
- **repositories/ExperimentRepository.py**: Repository for experiment data.
- **repositories/TestcaseRepository.py**: Repository for testcase data.
- **repositories/PerformanceRepository.py**: Repository for performance data.

## Documentation
The documentation can be found under: https://pascalkleindienst.github.io/experimentum/index.html

## License
Copyright 2018 Pascal Kleindienst

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


[build-status-badge]: https://travis-ci.com/PascalKleindienst/experimentum.svg?token=Hv3aZrJaquTDR7zjNhps&branch=master
[build-status-link]:https://travis-ci.com/PascalKleindienst/experimentum

[codacy-quality-badge]: https://img.shields.io/codacy/grade/e85a2c346ef14265b3986ff7f58b3c7a.svg?style=flat-square
[codacy-quality-link]: https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=PascalKleindienst/experimentum&utm_campaign=Badge_Grade

[codacy-coverage-badge]: https://img.shields.io/codacy/coverage/e85a2c346ef14265b3986ff7f58b3c7a.svg?style=flat-square
[codacy-coverage-link]: https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=PascalKleindienst/experimentum&amp;utm_campaign=Badge_Coverage