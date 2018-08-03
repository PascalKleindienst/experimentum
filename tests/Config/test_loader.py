from experimentum.Config import Loader, Config
import json
import pytest


class TestLoader(object):
    def _setup_loader(self, dir, fname='app.json'):
        data = {'foo': 'bar'}
        path = ''
        with dir.join(fname).open('w+') as fh:
            path = fh.name.replace('/' + fname, '')
            json.dump(data, fh)

        self.loader = Loader(path, Config())
        return path

    def test_get_config_files(self, tmpdir):
        path = self._setup_loader(tmpdir)
        assert self.loader.get_config_files() == {'app': path + '/app.json'}

    def test_load_config_files_with_missing_app_conf(self, tmpdir):
        with pytest.raises(Exception):
            self._setup_loader(tmpdir, 'foo.json')
            self.loader.load_config_files()

    def test_load_config_files(self, tmpdir):
        self._setup_loader(tmpdir)
        self.loader.load_config_files()
        assert self.loader.config.all() == {'app': {'foo': 'bar'}}
