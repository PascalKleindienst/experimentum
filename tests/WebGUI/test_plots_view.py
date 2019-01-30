# -*- coding: utf-8 -*-
from flask import json
import os


class TestMigrationsView(object):
    def test_get_image(self, client, app):
        # setup
        folder = os.path.join(app.config['UPLOAD_FOLDER'], 'test')
        os.makedirs(folder)
        with open(os.path.join(folder, 'testing.svg'), 'w+') as fh:
            fh.write('')

        # assertion
        response = client.get('/plots/image/test/testing.svg')
        assert response.content_type == 'image/svg+xml'
        assert response.content_length == 0
        assert response.status_code == 200

    def test_get_image_fails(self, client, app):
        response = client.get('/plots/image/test/failing.svg')
        assert response.status_code == 404

    def test_export_plots(self, client, app):
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'foo'))
        response = client.get('/plots/export/foo')
        assert response.content_type == 'application/zip'
        assert response.status_code == 200

    def test_export_not_existing_plots(self, client, caplog):
        response = client.get('/plots/export/foo')
        assert 'No such file or directory:' in caplog.text
        assert response.content_type == 'text/html'
        assert response.status_code == 400

    def test_generate_plot(self, client, app, mocker):
        # Config
        config = {'plots': {'test_plot': {'experiment': 'test'}}}
        plot_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test', 'test_plot.svg')

        # Mocks
        plot_mock = mocker.patch('experimentum.Plots.Plot')
        app.config['container'].make = mocker.MagicMock(return_value=plot_mock)
        app.config['container'].config.get = mocker.MagicMock(
            side_effect=lambda key, default=None: config.get(key, default)
        )

        # assertions
        response = client.get('/plots/generate/test')
        plot_mock.plotting.assert_called_once_with()
        plot_mock.save.assert_called_once_with(plot_file)
        assert 'http://localhost/experiments/plots/test' == response.headers['Location']

    def test_generate_plot_ajax(self, client, app, mocker):
        # Config
        config = {'plots': {'test_plot': {'experiment': 'test'}}}
        plot_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test', 'test_plot.svg')

        # Mocks
        plot_mock = mocker.patch('experimentum.Plots.Plot')
        app.config['container'].make = mocker.MagicMock(return_value=plot_mock)
        app.config['container'].config.get = mocker.MagicMock(
            side_effect=lambda key, default=None: config.get(key, default)
        )

        # assertions
        response = client.get('/plots/generate_ajax/test')
        data = json.loads(response.get_data(as_text=True))

        plot_mock.plotting.assert_called_once_with()
        plot_mock.save.assert_called_once_with(plot_file)
        assert len(data) is 1
        assert data[0]['status'] == 'success'
        assert data[0]['file'] == '/plots/image/test/test_plot.svg'

    def test_generate_plot_ajax_fails(self, client, app, mocker):
        # Mocks
        config = {'plots': {'test_plot': {'experiment': 'test'}}}
        app.config['container'].make = mocker.MagicMock(
            side_effect=Exception
        )
        app.config['container'].config.get = mocker.MagicMock(
            side_effect=lambda key, default=None: config.get(key, default)
        )

        # assertions
        response = client.get('/plots/generate_ajax/test')
        data = json.loads(response.get_data(as_text=True))
        assert len(data) is 1
        assert data[0]['status'] == 'error'
        assert data[0]['file'] is None
