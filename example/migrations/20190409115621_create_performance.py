from experimentum.Storage.Migrations import Migration


class CreatePerformance(Migration):

    """Create the create_performance migration."""
    revision = '20190409115621'

    def up(self):
        """Run the migrations."""
        with self.schema.create('performance') as table:
            table.big_increments('id')
            table.primary('id')
            table.string('label', 75)
            table.small_integer('level')
            table.string('type', 25)
            table.float('time')
            table.float('memory')
            table.float('peak_memory')
            table.integer('test_id')
            table.foreign('test_id')\
                .references('id').on('testcases')\
                .on_delete('cascade')\
                .on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('performance')
