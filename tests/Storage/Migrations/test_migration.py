from experimentum.Storage.Migrations import Migration

def test_up_down_methods_exists():
    assert 'up' in dir(Migration)
    assert 'down' in dir(Migration)

    m = Migration()
    m.up()
    m.down()

def test_representation():
    m = Migration()
    m.revision = 1234
    assert '1234_migration' == str(m)
