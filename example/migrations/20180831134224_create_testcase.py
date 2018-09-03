from experimentum.Storage.Migrations import Migration


class CreateTestcase(Migration):

    """Create the create_testcase migration."""
    revision = '20180831134224'

    def up(self):
        """Run the migrations."""
        with self.schema.create('testcases') as table:
            table.increments('id')
            table.primary('id')
            table.integer('iteration')
            table.integer('experiment_id')
            table.foreign('experiment_id')\
                .references('id').on('experiments')\
                .on_delete('cascade')\
                .on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('testcases')
