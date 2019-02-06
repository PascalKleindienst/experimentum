from experimentum.Storage.SQLAlchemy import Repository
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from sqlalchemy import or_


class mock_foo_relation(Repository):
    __relationships__ = {}


class TestAbstractStore(object):
    def setup_repo(self, mocker):
        store = mocker.patch('experimentum.Storage.SQLAlchemy.Store')
        store.session = UnifiedAlchemyMagicMock()
        Repository.__relationships__ = {}
        repo = Repository()
        Repository.store = store
        repo.store = store
        return repo

    def setup_mapper(self, mocker):
        store = mocker.patch('experimentum.Storage.SQLAlchemy.Store')
        table = mocker.MagicMock()
        store.meta.tables.get.return_value = table
        mapper_mock = mocker.patch('experimentum.Storage.SQLAlchemy.Repository.map_to_table')

        Repository.__table__ = 'foo'

        return mapper_mock, store, table

    def test_mapping(self, mocker):
        mapper_mock, store, table = self.setup_mapper(mocker)
        Repository.mapping(Repository, store)

        assert Repository.store == store
        mapper_mock.assert_called_once_with(Repository, Repository, table, properties={})

    def test_mapping_relationships(self, mocker):
        mapper_mock, store, table = self.setup_mapper(mocker)

        Repository.__relationships__ = {
            'foo': [mock_foo_relation, {'order_by': 'my_id'}],
            'bar': [mock_foo_relation]
        }
        Repository.mapping(Repository, store)

        assert Repository.store == store
        assert mapper_mock.call_count == 3
        mapper_mock.assert_any_call(
            Repository, Repository, table, properties={'foo': mocker.ANY, 'bar': mocker.ANY}
        )

    def test_mapping_fail(self, mocker, caplog):
        store = mocker.patch('experimentum.Storage.SQLAlchemy.Store')
        Repository.__relationships__ = {}
        Repository.mapping(Repository, store)

        assert 'Could not map table: foo' in caplog.text

    def test_create(self, mocker):
        repo = self.setup_repo(mocker)
        repo.create()
        repo.store.session.add.assert_called_once_with(repo)
        repo.store.session.commit.assert_called_once_with()

    def test_update(self, mocker):
        repo = self.setup_repo(mocker)
        repo.update()
        repo.store.session.commit.assert_called_once_with()

    def test_delete(self, mocker):
        repo = self.setup_repo(mocker)
        Repository.id = 42
        repo.delete()
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(repo.__class__.id == 42)
        ])
        repo.store.session.commit.assert_called_once_with()

    def test_get(self, mocker):
        repo = self.setup_repo(mocker)
        repo.get()
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(or_())
        ])

    def test_get_where_OR_id(self, mocker):
        repo = self.setup_repo(mocker)
        repo.get(where=['or', 'id', 2])
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(or_(Repository.id == 2))
        ])

    def test_get_where_id_eq_neq(self, mocker):
        repo = self.setup_repo(mocker)
        repo.get(where=[['id', '!=', 2], ['id', '==', 2]])
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(Repository.id != 2, Repository.id == 2, or_())
        ])

    def test_get_where_OR_id_eq_neq(self, mocker):
        repo = self.setup_repo(mocker)
        repo.get(where=[['or', 'id', '!=', 2], ['or', 'id', '==', 2]])
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(or_(Repository.id != 2, Repository.id == 2))
        ])

    def test_first(self, mocker):
        repo = self.setup_repo(mocker)
        repo.first()
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(or_())
        ])
        repo.store.session.first.assert_called_once_with()

    def test_all(self, mocker):
        repo = self.setup_repo(mocker)
        repo.all()
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.all.assert_called_once_with()

    def test_find(self, mocker):
        repo = self.setup_repo(mocker)
        repo.find(42)
        repo.store.session.query.assert_called_once_with(repo.__class__)
        repo.store.session.filter.assert_has_calls([
            mocker.call(Repository.id == 42, or_())
        ])
