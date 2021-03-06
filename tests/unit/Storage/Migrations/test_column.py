from experimentum.Storage.Migrations import Column


class TestColumn(object):
    def test_get_attributes(self):
        col = Column('some type', 'some name', {'foo': 'bar'})
        assert col.get('type') is 'some type'
        assert col.get('name') is 'some name'
        assert col.get('parameters') == {'foo': 'bar'}
        assert col.get('null') is False
        assert col.get('default', True) is None
        assert col.get('unsigned') is False

    def test_set_nullable(self):
        col = Column('some type', 'some name', {'foo': 'bar'})
        assert col.get('null') is False
        col.nullable()
        assert col.get('null') is True

    def test_set_default(self):
        col = Column('some type', 'some name', {'foo': 'bar'})
        assert col.get('default') is None
        col.default('val')
        assert col.get('default') is 'val'

    def test_set_unsigned(self):
        col = Column('some type', 'some name', {'foo': 'bar'})
        assert col.get('unsigned') is False
        col.unsigned()
        assert col.get('unsigned') is True

    def test_representation(self):
        col = Column('some type', 'some name', {'foo': 'bar'})
        assert "'type': 'some type'" in str(col)
        assert "'name': 'some name'" in str(col)
        assert "'parameters': {'foo': 'bar'}" in str(col)
        assert "'null': False" in str(col)
        assert "'default': None" in str(col)
        assert "'unsigned': False" in str(col)