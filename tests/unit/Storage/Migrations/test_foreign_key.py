from experimentum.Storage.Migrations import ForeignKey


class TestForeignKey(object):
    def test_get_attributes(self):
        fkey = ForeignKey('some_column', 'some_name')
        assert fkey.get('column') is 'some_column'
        assert fkey.get('name') is 'some_name'
        assert fkey.get('ref_table') is None
        assert fkey.get('ref_column') is None
        assert fkey.get('on_delete') is None
        assert fkey.get('on_update') is None

    def test_references(self):
        fkey = ForeignKey('some_column', 'some_name')
        assert fkey.get('ref_column') is None
        fkey.references('id')
        assert fkey.get('ref_column') is 'id'

    def test_on(self):
        fkey = ForeignKey('some_column', 'some_name')
        assert fkey.get('ref_table') is None
        fkey.on('users')
        assert fkey.get('ref_table') is 'users'

    def test_on_delete(self):
        fkey = ForeignKey('some_column', 'some_name')
        assert fkey.get('on_delete') is None
        fkey.on_delete('cascade')
        assert fkey.get('on_delete') is 'cascade'

    def test_on_update(self):
        fkey = ForeignKey('some_column', 'some_name')
        assert fkey.get('on_update') is None
        fkey.on_update('cascade')
        assert fkey.get('on_update') is 'cascade'
