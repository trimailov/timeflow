import os

from timeflow import cli
from timeflow.settings import Settings


def main():
    settings = Settings()
    config_file = settings.get_config_file()

    # create config file directory if it does not exist
    if not os.path.exists(os.path.dirname(config_file)):
        os.makedirs(os.path.dirname(config_file))

    # create settings config file if it does not exists and save settings there
    if not os.path.exists(config_file):
        open(config_file, 'a').close()
        settings.save()
        print('Settings file at {} was created!'.format(config_file))
    cli.cli()
