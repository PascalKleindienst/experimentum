
class TestExperimentsView(object):
    def test_run_invalid_experiment(self, client):
        response = client.get('/experiments/run/invalid_one')
        assert response.status_code == 404
        assert 'Page Not Found' in response.data.decode('utf-8', errors='ignore')

    def test_run_experiment_configuration(self, client):
        response = client.get('/experiments/run/test')
        assert 'Run Experiment' in response.data.decode('utf-8', errors='ignore')
        assert 'name="iterations"' in response.data.decode('utf-8', errors='ignore')
        assert 'name="config"' in response.data.decode('utf-8', errors='ignore')

    def test_run_experiment_show_results(self, client, app, mocker):
        exp_mock = mocker.patch('experimentum.Experiments.Experiment')
        app.config['container'].make = mocker.MagicMock(return_value=exp_mock)
        response = client.post('/experiments/run/test', data={'iterations': 1, 'config': ''})

        assert '<time class="started_at">-</time>' in response.data.decode('utf-8', errors='ignore')
        assert '<time class="finished_at">-</time>' in response.data.decode('utf-8', errors='ignore')
        assert '<code class="config_file">-</code>' in response.data.decode('utf-8', errors='ignore')
        assert '<div id="result" class="col s12"></div>' in response.data.decode('utf-8', errors='ignore')
        assert 'Running Tests' in response.data.decode('utf-8', errors='ignore')
        assert 'Generating Plots' in response.data.decode('utf-8', errors='ignore')
        assert "log_stream('/experiments/run/test?config=&iterations=1', '/plots/generate_ajax/test');" in response.data.decode('utf-8', errors='ignore')

    def test_run_experiment_event_stream(self, client, app, mocker):
        import datetime
        exp_mock = mocker.patch('experimentum.Experiments.Experiment')
        exp_mock.repos['experiment'].start = datetime.datetime(1970, 1, 1)
        exp_mock.repos['experiment'].finished = datetime.datetime(1970, 1, 1)
        exp_mock.repos['experiment'].config_file = 'foo.json'
        exp_mock.repos['experiment'].config_content = '{"foo": "bar"}'
        exp_mock.performance.formatter.get_table = mocker.MagicMock(return_value='FOO TABLE')
        app.config['container'].make = mocker.MagicMock(return_value=exp_mock)
        response = client.get('/experiments/run/test?config=bar.json&iterations=2', headers={'accept': 'text/event-stream'})

        assert response.content_type == 'text/event-stream'
        assert exp_mock.config_file == 'bar.json'
        assert exp_mock.show_progress is True
        assert 'data: {"type": "started"}' in response.data.decode('utf-8', errors='ignore')
        assert '"table": "FOO TABLE"' in response.data.decode('utf-8', errors='ignore')
        assert '"type": "table"' in response.data.decode('utf-8', errors='ignore')
        assert '"type": "finished"' in response.data.decode('utf-8', errors='ignore')
        assert '"start": "1970-01-01T00:00:00"' in response.data.decode('utf-8', errors='ignore')
        assert '"finished": "1970-01-01T00:00:00"' in response.data.decode('utf-8', errors='ignore')
        assert '"config_file": "foo.json"' in response.data.decode('utf-8', errors='ignore')
        assert '"config_content": "{\\"foo\\": \\"bar\\"}' in response.data.decode('utf-8', errors='ignore')

    def test_run_experiment_event_stream_content(self, client, app, mocker):
        import datetime
        import sys
        from time import sleep
        def run_mock():
            sleep(.5) # do some work
            sys.stderr.write('error logging')
            sleep(.5) # do some work
            sys.stdout.write('logging')

        exp_mock = mocker.patch('experimentum.Experiments.Experiment')
        exp_mock.start = lambda iterations: run_mock()
        exp_mock.repos['experiment'].start = datetime.datetime(1970, 1, 1)
        exp_mock.repos['experiment'].finished = datetime.datetime(1970, 1, 1)
        exp_mock.repos['experiment'].config_file = 'foo.json'
        exp_mock.repos['experiment'].config_content = '{"foo": "bar"}'
        exp_mock.performance.formatter.get_table = mocker.MagicMock(return_value='FOO TABLE')
        app.config['container'].make = mocker.MagicMock(return_value=exp_mock)
        response = client.get('/experiments/run/test', headers={'accept': 'text/event-stream'})

        assert response.content_type == 'text/event-stream'
        assert '"type": "log"' in response.data.decode('utf-8', errors='ignore')
        assert '"data": "error logging"' in response.data.decode('utf-8', errors='ignore')
        assert '"error": true' in response.data.decode('utf-8', errors='ignore')
        assert '"data": "logging"' in response.data.decode('utf-8', errors='ignore')
        assert '"error": false' in response.data.decode('utf-8', errors='ignore')

    def test_plots_empty(self, client, app, mocker):
        exp_mock = mocker.patch('experimentum.Experiments.Experiment')
        app.config['container'].make = mocker.MagicMock(return_value=exp_mock)
        response = client.get('/experiments/plots/test')

        assert 'No Plots available'

    def test_plots(self, client, app, mocker):
        import os
        exp_mock = mocker.patch('experimentum.Experiments.Experiment')
        app.config['container'].make = mocker.MagicMock(return_value=exp_mock)

        plot = os.path.join(app.config['UPLOAD_FOLDER'], 'test', 'foo.png')
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'test'))
        with open(plot, 'w+') as fh:
            fh.write('')

        response = client.get('/experiments/plots/test')
        assert 'src="/plots/image/test/foo.png"' in response.data.decode('utf-8', errors='ignore')

        os.unlink(plot)
