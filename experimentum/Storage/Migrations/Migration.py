import inflection


class Migration(object):

    """Abstract Migration."""
    revision = None

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
