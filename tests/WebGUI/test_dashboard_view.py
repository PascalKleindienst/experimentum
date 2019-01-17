import pytest
from sqlalchemy.exc import InvalidRequestError


def test_dashboard(app, client, mocker):
    # Mocks
    rows_mock = mocker.MagicMock()
    rows_mock.name = 'Foo'
    rows_mock.config_file = 'foo.json'
    app.config['container'].repositories['ExperimentRepository'].all.return_value = [rows_mock]

    # Get dashboard
    response = client.get('/')

    # Experiments
    assert 'Experiments' in response.data
    assert 'Run: <em>0</em> times' in response.data
    assert 'href="/experiments/run/test"' in response.data
    assert 'Run: <em>1</em> time' in response.data
    assert 'href="/experiments/run/foo"' in response.data

    # Migrations
    assert 'data-status-url="/migrations/status"' in response.data
    assert 'href="/migrations/upgrade"' in response.data
    assert 'href="/migrations/downgrade"' in response.data
    assert 'href="#refresh-migration-modal"' in response.data
    assert '<i class="material-icons">error</i> 20190101000000_create_experiments' in response.data


def test_dashboard_error(app, client, mocker):
    app.config['container'].repositories['ExperimentRepository'].all.side_effect = InvalidRequestError()
    response = client.get('/')

    # Error
    assert 'href="/experiments/run/' not in response.data
    assert 'There seems to be an error with your database.' in response.data
    assert 'Please try to refresh your migrations and restart the webgui to resolve this problem.' in response.data
