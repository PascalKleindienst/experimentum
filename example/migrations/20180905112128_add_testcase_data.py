from experimentum.Storage.Migrations import Migration


class AddTestcaseData(Migration):

    """Create the add_testcase_data migration."""
    revision = '20180905112128'

    def up(self):
        """Run the migrations."""
        with self.schema.table('testcases') as table:
            table.integer('random_value')

    def down(self):
        """Revert the migrations."""
        with self.schema.table('testcases') as table:
            table.drop_column('random_value')
