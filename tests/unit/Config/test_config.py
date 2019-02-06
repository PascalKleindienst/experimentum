from experimentum.Config import Config


class TestConfig(object):
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cls.config = Config()
        cls.config.items = {
            'foo': {'bar': 'baz', 'foobar': [1, 2, 3]},
            'root': {'level1': {'level2': 'val'}}
        }

    def test_has_with_valid_key(self):
        assert self.config.has('foo.bar') is True

    def test_has_with_invalid_key(self):
        assert self.config.has('invalid.key') is False

    def test_get_with_valid_key(self):
        assert self.config.get('foo.bar') is 'baz'

    def test_get_with_valid_key_list(self):
        keys = [('foo.bar', 'a'), ('foo.baz', 'b')]
        assert self.config.get(keys) == {'foo.bar': 'baz', 'foo.baz': 'b'}

    def test_get_with_sublevels(self):
        assert self.config.get('root') == {'level1': {'level2': 'val'}}

    def test_get_all(self):
        assert self.config.all() == self.config.items

    def test_set_key(self):
        self.config.set('foo', {'foobar': 42})
        assert self.config.items['foo']['foobar'] is 42

    def test_set_dot(self):
        self.config.set('foo.bar.baz', 42)
        assert 'foo' in self.config.items
        assert 'bar' in self.config.items['foo']
        assert 'baz' in self.config.items['foo']['bar']
        assert self.config.items['foo']['bar']['baz'] is 42

    def test_set_multiple_key(self):
        self.config.set({'foo': {'bar': 42}, 'x': 'y'})
        assert self.config.items['foo']['bar'] is 42
        assert self.config.items['x'] == 'y'
