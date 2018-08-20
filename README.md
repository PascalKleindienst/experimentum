# Experimentum [![Build Status][build-status-badge]][build-status-link] [![Codacy grade][codacy-quality-badge]][codacy-quality-link] [![Codacy coverage][codacy-coverage-badge]][codacy-coverage-link]

## Installation
`pip install https://github.com/PascalKleindienst/experimentum/archive/master.tar.gz`

`pip install git+ssh://git@github.com/PascalKleindienst/experimentum.git#egg=experimentum`

>The different ``dbapi`` packages are not part of the package dependencies, so you must install them in order to connect to corresponding databases:
>* PostgreSQL: ``psycopg2``
>* MySQL: ``PyMySQL`` or ``mysqlclient``
>* Oracle: ``cx_oracle``
>* Microsoft SQL Server: ``pyodbc`` or ``pymssql``
>* SQLite: The ``sqlite3`` module is bundled with Python by default

### Getting Started
All you need to get you started is an `app.json` config file and creating a new class derived from the `experimentum.Experiments.App` class where you set the path to the config folder.
To start the framework just call the `run`-method of the new `App` class.

All needed files and a derived `App` class can be generated with the `experimentum-quickstart` command *(see [Quickstart](#quickstart))*

Example `MyApp` class:

```python
from experimentum.Experiments import App

class MyApp(App):
    """Main Entry Point of the Framework.

    Args:
        config_path (str): Defaults to '.'. Path to config files.
    """
    config_path = 'config'

if __name__ == '__main__':
    app = MyApp('MyApp')  # Name of the app.
    app.run()
```

### Quickstart
In order to create all needed config files and folders the experimentum framework contains a quickstart command.
Just run `experimentum-quickstart` and answer the questions.

You can add a different root path with the `--root` option, e.g. `experimentum-quickstart --root example`

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