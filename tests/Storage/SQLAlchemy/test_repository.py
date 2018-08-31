from experimentum.Storage.SQLAlchemy import Repository
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from sqlalchemy import or_


class TestAbstractStore(object):
    def setup_repo(self, mocker):
        store = mocker.patch('experimentum.Storage.SQLAlchemy.Store')
        store.session = UnifiedAlchemyMagicMock()
        repo = Repository()
        Repository.store = store
        repo.store = store
        return repo

    def test_mapping(self, mocker):
        mapper = mocker.patch('sqlalchemy.orm.mapper')
        Repository.__table__ = 'foo'
        Repository.mapping(Repository, 'store')

        # TODO: Assertions
        assert Repository.store == 'store'

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
