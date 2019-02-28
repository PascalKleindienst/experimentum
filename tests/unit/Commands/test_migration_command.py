from experimentum.Commands.MigrationCommand import down, make, up, status, refresh


class TestMigrationCommand(object):
    def test_status(self, mocker):
        mock_migrator = mocker.patch('experimentum.Storage.Migrator')
        mock_migrator.status = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=mock_migrator)

        status(app_mock).handle(app_mock)
        mock_migrator.status.assert_called_once_with()

    def test_refresh(self, mocker):
        mock_migrator = mocker.patch('experimentum.Storage.Migrator')
        mock_migrator.refresh = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=mock_migrator)

        refresh(app_mock).handle(app_mock)
        mock_migrator.refresh.assert_called_once_with()

    def test_up(self, mocker):
        mock_migrator = mocker.patch('experimentum.Storage.Migrator')
        mock_migrator.up = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=mock_migrator)

        up(app_mock).handle(app_mock)
        mock_migrator.up.assert_called_once_with()

    def test_down(self, mocker):
        mock_migrator = mocker.patch('experimentum.Storage.Migrator')
        mock_migrator.down = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=mock_migrator)

        down(app_mock).handle(app_mock)
        mock_migrator.down.assert_called_once_with()

    def test_make(self, mocker):
        mock_migrator = mocker.patch('experimentum.Storage.Migrator')
        mock_migrator.make = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=mock_migrator)

        class args:
            name = 'Foo'

        make(app_mock).handle(app_mock, args)
        mock_migrator.make.assert_called_once_with('foo')
