from experimentum.Storage.Migrations import Migration


class CreateExperiments(Migration):

    """Create the create_experiments migration."""
    revision = '20180831134223'

    def up(self):
        """Run the migrations."""
        with self.schema.create('experiments') as table:
            table.increments('id')
            table.primary('id')
            table.string('name', 75)
            table.datetime('start')
            table.datetime('finished').nullable()
            table.string('config_file').nullable()
            table.json('config_content').nullable()

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('experiments')
