from experimentum.Storage.Migrations import Migration


class AddTestcaseData(Migration):

    """Create the add_testcase_data migration."""
    revision = '20190411131223'

    def up(self):
        """Run the migrations."""
        with self.schema.table('testcases') as table:
            table.integer('value')

    def down(self):
        """Revert the migrations."""
        if self.schema.has_column('testcases', 'value'):
            with self.schema.table('testcases') as table:
                table.drop_column('value')
