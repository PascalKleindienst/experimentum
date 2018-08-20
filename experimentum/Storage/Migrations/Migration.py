"""Handles database migrations."""
import inflection


class Migration(object):

    """Base Migration Class."""
    revision = None

    def __init__(self, app):
        """Init the Migration and set up the schema class.

        Arguments:
            app (App): App class
        """
        self.schema = app.make('schema')

    def up(self):
        """Revert the migrations."""
        pass

    def down(self):
        """Revert the migrations."""
        pass

    def __repr__(self):
        """Return Migration name."""
        return '{}_{}'.format(
            self.revision,
            inflection.underscore(self.__class__.__name__)
        )
