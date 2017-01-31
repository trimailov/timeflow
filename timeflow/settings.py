import os

from configparser import ConfigParser


class Settings():
    name = "Jon Doe"
    activity_email = "activity@example.com"
    email_address = "jondoe@example.com"
    email_user = "jondoe"
    email_password = "mypassword"
    smtp_server = "smtp.myserver.com"
    smtp_port = 25

    def config(self):
        config = ConfigParser()
        config["timeflow"] = {
            "name": self.name,
            "activity_email": self.activity_email,
            "email_address": self.email_address,
            "email_user": self.email_user,
            "email_password": self.email_password,
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
        }
        return config

    def get_config_file(self):
        return os.path.join(os.path.expanduser('~'), '.config', 'timeflow', 'settings.ini')

    def load(self):
        config_file = self.get_config_file()
        config = self.config()
        config.read(config_file)
        self.name = config['timeflow']['name']
        self.activity_email = config['timeflow']['activity_email']
        self.email_address = config['timeflow']['email_address']
        self.email_user = config['timeflow']['email_user']
        self.email_password = config['timeflow']['email_password']
        self.smtp_server = config['timeflow']['smtp_server']
        self.smtp_port = config['timeflow']['smtp_port']

    def save(self):
        config_file = self.get_config_file()
        config = self.config()
        with open(config_file, 'w') as f:
            config.write(f)
