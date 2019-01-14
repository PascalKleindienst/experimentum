from experimentum.Plots import Factory
import pytest


class TestFactory(object):
    def setup_factory(self, mocker, cfg={}):
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.config = mocker.MagicMock()
        factory = Factory(app_mock)
        factory.app.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        return factory

    def setup_create(self, mocker, tmpdir):
        cfg = {'app.plots.path': tmpdir.strpath}
        factory = self.setup_factory(mocker, cfg)
        factory.parse = mocker.MagicMock(return_value={'foo': 'bar'})
        factory.validate = mocker.MagicMock(return_value={'foo': 'bar'})

        return factory

    def test_create(self, mocker, tmpdir):
        with tmpdir.join('FooPlot.py').open('w+') as fh:
            fh.write(
                'from experimentum.Plots.Plot import Plot\n'
                'class FooPlot(Plot): pass'
            )

        factory = self.setup_create(mocker, tmpdir)
        plot = factory.create('foo')

        assert plot.config == {'foo': 'bar'}
        assert plot.type == 'plot'
        factory.parse.assert_called_once_with('foo')
        factory.validate.assert_called_once_with({'foo': 'bar'})

    def test_create_not_found(self, mocker, tmpdir, capsys):
        factory = self.setup_create(mocker, tmpdir)

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            factory.create('foo')

        assert 'Could not find plot named "{}" under path "{}"'.format('foo', tmpdir.strpath) in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_create_not_loadable(self, mocker, tmpdir, capsys):
        with tmpdir.join('FooPlot.py').open('w+') as fh:
            fh.write('')

        factory = self.setup_create(mocker, tmpdir)
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            factory.create('foo')

        assert 'Could not load file:' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    def test_parse(self, mocker):
        factory = self.setup_factory(mocker, {'plots.foo': 'bar'})
        assert factory.parse('foo') == 'bar'

    def test_parse_invalid_config(self, mocker, capsys):
        factory = self.setup_factory(mocker, {'plots.baz': 'bar'})

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            factory.parse('foo')

        assert 'Could not parse config for plot "foo".' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_validate(self, mocker):
        data = {'foo': 'bar'}
        factory = self.setup_factory(mocker)
        cfg_mock = mocker.patch('experimentum.Config')
        factory.app.make = mocker.MagicMock(return_value=cfg_mock)

        factory.validate(data)
        cfg_mock.set.assert_called_once_with(data)
