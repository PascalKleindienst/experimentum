# -*- coding: utf-8 -*-
from experimentum.Experiments import App
from commands.LoremIpsum import lorem


class ExampleApp(App):

    """Main Entry Point of the Framework.

    Args:
        config_path (str): Defaults to '.'. Path to config files
    """
    config_path = 'config'

    def register_commands(self):
        """Register Custom Commands.

        Returns:
            dict: { Name of command : Command Handler }
        """
        return {
            'lorem': lorem
        }


if __name__ == '__main__':
    app = ExampleApp('ExampleApp', __file__)
    app.run()
