from experimentum.Storage import AbstractStore
import pytest



class TestAbstractStore(object):

    def test_abstract_has_table(self, mocker):
        mocker.patch.multiple(AbstractStore, __abstractmethods__=set())
        store = AbstractStore()

        with pytest.raises(NotImplementedError):
            store.has_table('foo')

    def test_abstract_has_column(self, mocker):
        mocker.patch.multiple(AbstractStore, __abstractmethods__=set())
        store = AbstractStore()

        with pytest.raises(NotImplementedError):
            store.has_column('foo', 'bar')

    def test_abstract_create(self, mocker):
        mocker.patch.multiple(AbstractStore, __abstractmethods__=set())
        store = AbstractStore()

        with pytest.raises(NotImplementedError):
            store.create('blueprint')

    def test_abstract_rename(self, mocker):
        mocker.patch.multiple(AbstractStore, __abstractmethods__=set())
        store = AbstractStore()

        with pytest.raises(NotImplementedError):
            store.rename('old', 'new')

    def test_abstract_drop(self, mocker):
        mocker.patch.multiple(AbstractStore, __abstractmethods__=set())
        store = AbstractStore()

        with pytest.raises(NotImplementedError):
            store.drop('blueprint')

    def test_abstract_alter(self, mocker):
        mocker.patch.multiple(AbstractStore, __abstractmethods__=set())
        store = AbstractStore()

        with pytest.raises(NotImplementedError):
            store.alter('blueprint')