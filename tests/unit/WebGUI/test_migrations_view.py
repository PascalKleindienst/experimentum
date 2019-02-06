# -*- coding: utf-8 -*-
from flask import json
import sys


class TestMigrationsView(object):
    def test_upgrade_success(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.up.side_effect = lambda: sys.stdout.write('Some Message')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.get('/migrations/upgrade')
        data = json.loads(response.get_data(as_text=True))

        mock.up.assert_called_once_with()
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['message'] == 'Some Message'

    def test_upgrade_error(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.up.side_effect = SystemExit('error')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.get('/migrations/upgrade')
        data = json.loads(response.get_data(as_text=True))

        mock.up.assert_called_once_with()
        assert response.status_code == 200
        assert data['status'] == 'error'
        assert data['message'] == ''

    def test_downgrade_success(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.down.side_effect = lambda: sys.stdout.write('Some Message')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.get('/migrations/downgrade')
        data = json.loads(response.get_data(as_text=True))

        mock.down.assert_called_once_with()
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['message'] == 'Some Message'

    def test_downgrade_error(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.down.side_effect = SystemExit('error')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.get('/migrations/downgrade')
        data = json.loads(response.get_data(as_text=True))

        mock.down.assert_called_once_with()
        assert response.status_code == 200
        assert data['status'] == 'error'
        assert data['message'] == ''

    def test_downgrade_error_response(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.down.side_effect = lambda: sys.stdout.write('× Some Error Message')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.get('/migrations/downgrade')
        data = json.loads(response.get_data(as_text=True))

        mock.down.assert_called_once_with()
        assert response.status_code == 200
        assert data['status'] == 'error'
        assert data['message'] == u'× Some Error Message'

    def test_refresh(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.get('/migrations/refresh')
        data = json.loads(response.get_data(as_text=True))

        mock.refresh.assert_called_once_with()
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['message'] == u'› Refreshed all migrations'

    def test_make(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.make.side_effect = lambda _: sys.stdout.write('Some Message')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.post('/migrations/make', data={'name': 'foo'})
        data = json.loads(response.get_data(as_text=True))

        mock.make.assert_called_once_with('foo')
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['message'] == 'Some Message'

    def test_make_error(self, client, app, mocker):
        mock = mocker.patch('experimentum.Storage.Migrations.Migrator')
        mock.make.side_effect = SystemExit('Some Error')
        app.config['container'].make = mocker.MagicMock(return_value=mock)

        response = client.post('/migrations/make', data={'name': 'foo'})
        data = json.loads(response.get_data(as_text=True))

        mock.make.assert_called_once_with('foo')
        assert response.status_code == 200
        assert data['status'] == 'error'
        assert data['message'] == ''

    def test_status(self, client, app, mocker):
        response = client.get('/migrations/status')
        assert response.status_code == 200
        assert '20190101000000_create_experiments' in response.data.decode('utf-8', errors='ignore')
