from experimentum.Experiments import DataBag


class TestDataBag(object):
    def setup_method(self):
        """ Clear DataBag before each test. """
        DataBag._data = {}

    def test_add_item(self):
        DataBag.add('foo.bar.baz', 42)
        assert 'foo' in DataBag._data
        assert 'bar' in DataBag._data['foo']
        assert 'baz' in DataBag._data['foo']['bar']
        assert DataBag._data['foo']['bar']['baz'] is 42

    def test_append_item(self):
        DataBag.add('foo.bar.baz', 42)
        DataBag.add('foo.bar.baz', True)  # append
        assert DataBag._data['foo']['bar']['baz'] == [42, True]

    def test_get_item(self):
        DataBag._data = {'foo': {'bar': {'baz': 42 }}}
        assert DataBag.get('foo.bar.baz') is 42

    def test_get_invalid_item(self):
        assert DataBag.get('foo.bar.baz') is None

    def test_get_invalid_item_default(self):
        assert DataBag.get('foo.bar.baz', 'default') == 'default'

    def test_merge_dicts(self):
        DataBag._data = {'foo': {'bar': {'a': 1, 'b': 2}}}
        DataBag.merge('foo.bar', {'a': 42, 'c': 3})
        assert DataBag._data['foo']['bar']['a'] is 42
        assert DataBag._data['foo']['bar']['b'] is 2
        assert DataBag._data['foo']['bar']['c'] is 3

    def test_merge_lists(self):
        DataBag._data = {'foo': {'bar':  ['a', 'b', 'c']}}
        DataBag.merge('foo.bar', ['a', 'd', 'e'])
        assert DataBag._data['foo']['bar'] == ['a', 'b', 'c', 'a', 'd', 'e']

    def test_get_all(self):
        DataBag._data = {'foo': {'a': 1, 'b': 2}}
        assert DataBag.all() == {'foo': {'a': 1, 'b': 2}}

    def test_clear(self):
        DataBag._data = {'foo': {'a': 1, 'b': 2}}
        DataBag.clear()
        assert DataBag._data == {}

    def test_flush_all(self):
        DataBag._data = {'foo': {'a': 1, 'b': 2}}
        data = DataBag.flush()
        assert data == {'foo': {'a': 1, 'b': 2}}
        assert DataBag._data == {}

    def test_flush_key(self):
        DataBag._data = {'foo': {'a': 1, 'b': 2}}
        data = DataBag.flush('foo.a')
        assert data is 1
        assert DataBag._data == {'foo': {'b': 2}}

    def test_flush_invalid_key(self):
        DataBag._data = {'foo': 42}
        data = DataBag.flush('foo.a', 'invalid')
        assert data == 'invalid'
        assert DataBag._data == {'foo': 42}

    def test_delete_key(self):
        DataBag._data = {'foo': {'a': 42, 'b': 2}}
        assert DataBag.delete('foo.a') is 1
        assert DataBag._data == {'foo': {'b': 2}}

    def test_delete_invalid_key(self, capsys):
        DataBag._data = {'foo': {'a': {}}}
        assert DataBag.delete('foo.a.baz') is -1
