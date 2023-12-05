import json
import os


class Settings:
    template = {
                "theme": "dark",
                "database": {
                    "system": "sqlite",
                    "location": "local",
                    "path": "data/database.db",
                    "name": "",
                    "address": "",
                    "port": "",
                    "username": "",
                    "password": "",
                },
            }

    def __init__(self, settings_path: str):
        self.settings_path = settings_path

        self.settings = self.load_settings()

    def __eq__(self, other):
        if isinstance(other, Settings):
            return self.settings == other.settings

        elif isinstance(other, dict):
            return self.settings == other

        else:
            return False

    def load_settings(self) -> dict:
        """
        Load the settings from the settings file.
        """
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as settings_file:
                settings = json.load(settings_file)

        else:
            # Create the directory relative to the top-level of this project
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)

            settings = self.save_settings(self.template)

        return settings

    def save_settings(self, settings: "dict | Settings | None" = None) -> dict:
        """
        Save the settings to the settings file.
        """
        if settings is None:
            settings = self.settings

        elif isinstance(settings, Settings):
            settings = settings.settings

        # Verify that all the required keys are in the settings to save.
        # If not, create them.
        for key, value in self.template.items():
            if key not in settings:
                settings[key] = value

            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in settings[key]:
                        settings[key][sub_key] = sub_value

        with open(self.settings_path, "w") as settings_file:
            json.dump(settings, settings_file, indent=4)

        return settings

    def copy(self) -> "Settings":
        """
        Return a copy of the settings.
        """
        return Settings(self.settings_path)

    @property
    def theme(self) -> str:
        """
        Get the current theme.
        """
        return self.settings["theme"]

    @theme.setter
    def theme(self, theme: str) -> None:
        """
        Set the current theme.
        """
        self.settings["theme"] = theme

    @property
    def database_system(self) -> str:
        """
        Get the current database system.
        """
        return self.settings["database"]["system"].lower()

    @database_system.setter
    def database_system(self, database_system: str) -> None:
        """
        Set the current database system.
        """
        self.settings["database"]["system"] = database_system

    @property
    def database_location(self) -> str:
        """
        Get the current database location.
        """
        return self.settings["database"]["location"]

    @database_location.setter
    def database_location(self, database_location: str) -> None:
        """
        Set the current database location.
        """
        self.settings["database"]["location"] = database_location

    @property
    def database_path(self) -> str:
        """
        Get the current database path.
        """
        return self.settings["database"]["path"]

    @database_path.setter
    def database_path(self, database_path: str) -> None:
        """
        Set the current database path.
        """
        self.settings["database"]["path"] = database_path

    @property
    def absolute_database_path(self) -> str:
        """
        Get the current absolute database path.
        """
        return os.path.abspath(self.database_path)

    @property
    def database_address(self) -> str:
        """
        Get the current database address.
        """
        return self.settings["database"]["address"]

    @database_address.setter
    def database_address(self, database_address: str) -> None:
        """
        Set the current database address.
        """
        self.settings["database"]["address"] = database_address

    @property
    def database_port(self) -> str:
        """
        Get the current database port.
        """
        return self.settings["database"]["port"]

    @database_port.setter
    def database_port(self, database_port: str) -> None:
        """
        Set the current database port.
        """
        self.settings["database"]["port"] = database_port

    @property
    def database_username(self) -> str:
        """
        Get the current database username.
        """
        return self.settings["database"]["username"]

    @database_username.setter
    def database_username(self, database_username: str) -> None:
        """
        Set the current database username.
        """
        self.settings["database"]["username"] = database_username

    @property
    def database_password(self) -> str:
        """
        Get the current database password.
        """
        return self.settings["database"]["password"]

    @database_password.setter
    def database_password(self, database_password: str) -> None:
        """
        Set the current database password.
        """
        self.settings["database"]["password"] = database_password

    @property
    def database_name(self) -> str:
        """
        Get the current database name.
        """
        return self.settings["database"]["name"]

    @database_name.setter
    def database_name(self, database_name: str) -> None:
        """
        Set the current database name.
        """
        self.settings["database"]["name"] = database_name

    @property
    def database_url(self) -> str:
        """
        Get the current database URL.
        """
        return self.settings["database"]["url"]

    @database_url.setter
    def database_url(self, database_url: str) -> None:
        """
        Set the current database URL.
        """
        self.settings["database"]["url"] = database_url

    @property
    def database_save_password(self) -> bool:
        """
        Get the current database save password setting.
        """
        return self.settings["database"]["save_password"]

    @database_save_password.setter
    def database_save_password(self, database_save_password: bool) -> None:
        """
        Set the current database save password setting.
        """
        self.settings["database"]["save_password"] = database_save_password

    @property
    def password(self) -> str:
        """
        Get the current password.
        """
        return self.settings["database"]["password"]

    @password.setter
    def password(self, password: str) -> None:
        """
        Set the current password.
        """
        self.settings["password"] = password
