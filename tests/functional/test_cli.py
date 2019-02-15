from __future__ import print_function
import sys
import tempfile
from experimentum.Experiments import App
from experimentum.Commands import command

# Lorem Ipsum Text
lorem_ipsum = [
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
    "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
    "At vero eos et accusam et justo duo dolores et ea rebum.",
    "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
    "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
    "At vero eos et accusam et justo duo dolores et ea rebum.",
    "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
    "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
    "At vero eos et accusam et justo duo dolores et ea rebum.",
    "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
    "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua."
]


# Lorem Ipsum Command
@command(
    'Displays between one and ten lorem ipsum sentences.',
    arguments={'sentences': {'type': int, 'action': 'store'}},
    help='Display lorem ipsum text'
)
def lorem(app, args):
    """Display lorem ipsum text."""
    # Clamp sentences between 1 and 10
    sentences = args.sentences
    sentences = 1 if sentences < 1 else sentences
    sentences = 10 if sentences > 10 else sentences

    print(' '.join(lorem_ipsum[:sentences]))


class TestCLI(object):
    def test_custom_commands(self, app_files, capsys):
        """
        GIVEN the framework is installed
        WHEN a user wants add and use a custom CLI command
        THEN the command is executed
        """
        # Register Lorem Command in app
        class TestApp(App):
            config_path = tempfile.mkdtemp()

            def register_commands(self):
                return {'lorem': lorem}

        # User initialises the application
        app_files.create_directories_and_files(TestApp.config_path)
        app = TestApp('testing', TestApp.config_path + '/.')

        # User runs the lorem command
        sys.argv = ['main.py', 'lorem', '3']
        app.run()

        # Check output
        output = capsys.readouterr().out.strip().split('.')
        assert len(output) == 4
        assert output[0].strip() == lorem_ipsum[0][:-1]  # missing '.' due to split
        assert output[1].strip() == lorem_ipsum[1][:-1]  # missing '.' due to split
        assert output[2].strip() == lorem_ipsum[2][:-1]  # missing '.' due to split
        assert output[3].strip() == ''
