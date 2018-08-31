from experimentum.Storage import AbstractRepository
import pytest



class TestAbstractStore(object):
    def setup_repo(self, mocker):
        mocker.patch.multiple(AbstractRepository, __abstractmethods__=set())
        return AbstractRepository()

    def test_representation(self, mocker):
        repo = self.setup_repo(mocker)
        repo.foo = 'bar'
        assert str(repo) == '<AbstractRepository foo="bar" />'

    def test_get_item(self, mocker):
        repo = self.setup_repo(mocker)
        repo.foo = 'bar'
        assert repo['foo'] == 'bar'

    def test_set_item(self, mocker):
        repo = self.setup_repo(mocker)
        repo['foo'] = 'Bar'
        assert repo.foo == 'Bar'

    def test_from_dict(self, mocker):
        mocker.patch.multiple(AbstractRepository, __abstractmethods__=set())
        repo = AbstractRepository.from_dict({
            'foo': 'bar',
            'foobars': ['foobar', 'foobaz']
        })
        assert repo.foo == 'bar'
        assert repo.foobars == ['foobar', 'foobaz']

    def test_from_dict_with_relationships(self, mocker):
        mocker.patch.multiple(AbstractRepository, __abstractmethods__=set())
        AbstractRepository.__relationships__ = {
            'foobars': [AbstractRepository]
        }
        repo = AbstractRepository.from_dict({
            'foo': 'bar',
            'foobars': [{'id': 'foobar'}, {'id': 'foobaz'}]
        })
        assert repo.foo == 'bar'
        assert isinstance(repo.foobars[0], AbstractRepository)
        assert isinstance(repo.foobars[1], AbstractRepository)
        assert repo.foobars[0].id == 'foobar'
        assert repo.foobars[1].id == 'foobaz'
        AbstractRepository.__relationships__ = {}

    def test_from_dict_with_one_to_one_relation(self, mocker):
        mocker.patch.multiple(AbstractRepository, __abstractmethods__=set())
        AbstractRepository.__relationships__ = {
            'foobar': [AbstractRepository]
        }
        repo = AbstractRepository.from_dict({
            'foo': 'bar',
            'foobar': {'id': 'foobar'},
        })
        assert repo.foo == 'bar'
        assert isinstance(repo.foobar, AbstractRepository)
        assert repo.foobar.id == 'foobar'
        AbstractRepository.__relationships__ = {}

    def test_abstract_mapping(self):
        with pytest.raises(NotImplementedError):
            AbstractRepository.mapping('foo', 'bar')

    def test_abstract_create(self, mocker):
        repo = self.setup_repo(mocker)

        with pytest.raises(NotImplementedError):
            repo.create()

    def test_abstract_update(self, mocker):
        repo = self.setup_repo(mocker)

        with pytest.raises(NotImplementedError):
            repo.update()

    def test_abstract_delete(self, mocker):
        repo = self.setup_repo(mocker)

        with pytest.raises(NotImplementedError):
            repo.delete()

    def test_abstract_get(self):
        with pytest.raises(NotImplementedError):
            AbstractRepository.get(where=[])

    def test_abstract_first(self):
        with pytest.raises(NotImplementedError):
            AbstractRepository.first(where=[])

    def test_abstract_all(self):
        with pytest.raises(NotImplementedError):
            AbstractRepository.all()

    def test_abstract_find(self):
        with pytest.raises(NotImplementedError):
            AbstractRepository.find(1)

    def test_before_insert(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.before_insert() is None

    def test_after_insert(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.after_insert() is None

    def test_before_update(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.before_update() is None

    def test_after_update(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.after_update() is None