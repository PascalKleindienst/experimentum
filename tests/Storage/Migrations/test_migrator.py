from experimentum.Storage.Migrations import Migrator, Migration
from datetime import datetime
import pytest

_STUB_ = """
from experimentum.Storage.Migrations import Migration


class {migration}(Migration):

    \"\"\"Create the {name} migration.\"\"\"
    revision = '{revision}'

    def up(self):
        \"\"\"Revert the migrations.\"\"\"
        pass

    def down(self):
        \"\"\"Revert the migrations.\"\"\"
        pass
"""

class TestMigrator(object):
    def _create_migration_file(self, ts, tmpdir):
        time = datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        fname = "{}_test_migration_{}.py".format(time, ts)
        fh = tmpdir.join(fname)
        fh.write(_STUB_.format(
            migration='TestMigration' + str(ts),
            name="Test Migration " + str(ts),
            revision=time
        ))

        return fname

    def _create_migrator(self, tmpdir, mocker):
        app = mocker.patch('experimentum.Experiments.App')
        return Migrator(tmpdir, app)

    def test_init_creates_version_file(self, tmpdir, mocker):
        assert tmpdir.join('.version').check() is False
        self._create_migrator(tmpdir.strpath, mocker)
        assert tmpdir.join('.version').check() is True

    def test_init_loads_migrations(self, tmpdir, mocker):
        self._create_migration_file(0, tmpdir)
        self._create_migration_file(1, tmpdir)
        migrator = self._create_migrator(tmpdir.strpath, mocker)

        for name, migration in migrator.migrations.items():
            assert isinstance(migration, Migration)

    def test_status_not_migrated(self, tmpdir, mocker, capsys):
        fname = self._create_migration_file(0, tmpdir)
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.status()
        captured = capsys.readouterr()
        assert fname[:-3] in captured.out
        assert 'No' in captured.out

    def test_status_migrated(self, tmpdir, mocker, capsys):
        fname = self._create_migration_file(0, tmpdir)
        tmpdir.join('.version').write(fname[:14])
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.status()
        captured = capsys.readouterr()
        assert fname[:-3] in captured.out
        assert 'Yes' in captured.out

    def test_make_migration(self, tmpdir, mocker):
        import glob
        assert len(glob.glob(tmpdir.strpath + '/*_test.py')) is 0
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.make('test')
        assert len(glob.glob(tmpdir.strpath + '/*_test.py')) is 1

    def test_upgrade_migration(self, tmpdir, mocker):
        self._create_migration_file(0, tmpdir)
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.up()
        assert tmpdir.join('.version').read() ==  '|' + datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S')

    def test_upgraded_all_migrations(self, tmpdir, mocker, capsys):
        self._create_migration_file(0, tmpdir)
        tmpdir.join('.version').write('|' + datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S'))
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.up()
        assert 'Migrations are all up to date' in capsys.readouterr().out

    def test_uprage_with_valid_migration(self, tmpdir, mocker):
        mock_migration = mocker.patch('experimentum.Storage.Migrations.Migration', revision=datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S'))
        mock_migration.up = mocker.MagicMock()

        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.up(mock_migration)
        mock_migration.up.assert_called_once()

    def test_upgrade_with_invalid_migration(self, tmpdir, mocker):
        migrator = self._create_migrator(tmpdir.strpath, mocker)

        with pytest.raises(TypeError):
            migrator.up('mock_migration')

    def test_downgrade_latest_migration(self, tmpdir, mocker):
        self._create_migration_file(0, tmpdir)
        self._create_migration_file(100, tmpdir)
        tmpdir.join('.version').write('|{}|{}'.format(
            datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S'),
            datetime.fromtimestamp(100).strftime('%Y%m%d%H%M%S')
        ))

        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.down()
        assert tmpdir.join('.version').read() ==  '|' + datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S')

    def test_downgraded_all_migrations(self, tmpdir, mocker, capsys):
        self._create_migration_file(0, tmpdir)
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.down()
        assert 'There are no migrations to downgrade' in capsys.readouterr().out

    def test_downgrade_with_valid_migration(self, tmpdir, mocker):
        mock_migration = mocker.patch('experimentum.Storage.Migrations.Migration', revision=datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S'))
        mock_migration.down = mocker.MagicMock()
        tmpdir.join('.version').write('|' + datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S'))

        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.down(mock_migration)
        mock_migration.down.assert_called_once()

    def test_downgrade_with_invalid_migration(self, tmpdir, mocker):
        migrator = self._create_migrator(tmpdir.strpath, mocker)

        with pytest.raises(TypeError):
            migrator.down('mock_migration')

    def test_refresh(self, tmpdir, mocker):
        self._create_migration_file(0, tmpdir)
        tmpdir.join('.version').write('|' + datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S'))
        migrator = self._create_migrator(tmpdir.strpath, mocker)
        migrator.up = mocker.MagicMock()
        migrator.down = mocker.MagicMock()

        migrator.refresh()

        migrator.down.assert_called()
        migrator.up.assert_called()