from experimentum.Storage.Migrations import Migration

def test_up_down_methods_exists(mocker):
    assert 'up' in dir(Migration)
    assert 'down' in dir(Migration)

    m = Migration(mocker.patch('experimentum.Experiments.App'))
    m.up()
    m.down()

def test_representation(mocker):
    m = Migration(mocker.patch('experimentum.Experiments.App'))
    m.revision = 1234
    assert '1234_migration' == str(m)
