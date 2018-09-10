from experimentum.Storage.AbstractRepository import AbstractRepository, RepositoryLoader
import pytest
import os


class TestRepositoryLoader(object):
    def test_setup(self):
        loader = RepositoryLoader('App', 'Implementation', 'Store')
        assert loader.app == 'App'
        assert loader.implementation == 'Implementation'
        assert loader.store == 'Store'
        assert AbstractRepository.implementation == 'Implementation'

    def test_load_fails(self, mocker):
        app = mocker.patch('experimentum.Experiments.App')
        app.root = os.path.dirname(__file__)
        app.config.get = mocker.MagicMock(return_value='.')

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            loader = RepositoryLoader(app, 'Implementation', app.store)
            loader.load()

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_get_repo(self):
        loader = RepositoryLoader('App', 'Implementation', 'Store')
        loader._repos = {'foo': AbstractRepository}

        assert issubclass(loader.get('foo'), AbstractRepository)

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            loader.get('foobar')
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
