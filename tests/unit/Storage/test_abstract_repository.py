from experimentum.Storage import AbstractRepository
import pytest
import json


def err(self, foo):
    raise TypeError('something went wrong')


class TestAbstractRepository(object):
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

    def test_contains_item(self, mocker):
        repo = self.setup_repo(mocker)
        repo.foo = 'Bar'
        assert 'foo' in repo

    def test_to_json(self, mocker):
        repo = self.setup_repo(mocker)
        repo.foo = 'bar'
        repo.bar = ['foo', 'bar', 'baz']
        repo._private = 'private'

        output = {'foo': 'bar', 'bar': ['foo', 'bar', 'baz']}
        assert json.dumps(output, sort_keys=True, indent=4) == repo.to_json()

    def test_from_dict(self, mocker):
        mocker.patch.multiple(AbstractRepository, __abstractmethods__=set())
        repo = AbstractRepository.from_dict({
            'foo': 'bar',
            'foobars': ['foobar', 'foobaz']
        })
        assert repo.foo == 'bar'
        assert repo.foobars == ['foobar', 'foobaz']

    @pytest.mark.parametrize('init,output,code', [
        (err, "something went wrong", -1),
        (lambda self: None, 'got an unexpected keyword argument \'foo\'', 1),
        (lambda self, foo, bar: None, "The AbstractRepository class is missing the following parameters: {'bar'}", 2)
    ])
    def test_from_dict_error_init(self, mocker, capsys, init, output, code):
        mocker.patch.multiple(AbstractRepository, __init__=init, __abstractmethods__=set())

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AbstractRepository.from_dict({
                'foo': 'bar',
            })

        assert output in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == code

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
        assert isinstance(repo.foobar[0], AbstractRepository)
        assert repo.foobar[0].id == 'foobar'
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
        assert repo.before_insert() is repo

    def test_after_insert(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.after_insert() is repo

    def test_before_update(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.before_update() is repo

    def test_after_update(self, mocker):
        repo = self.setup_repo(mocker)
        assert repo.after_update() is repo
