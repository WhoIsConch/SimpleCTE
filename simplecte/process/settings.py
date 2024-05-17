import json
import os


__all__ = ("Settings",)


class Settings:
    template = {
        "theme": "dark",
        "database": {
            "system": "sqlite",
            "path": str(os.path.abspath("simplecte/data/db.db")),
            "saved_dbs": [str(os.path.abspath("simplecte/data/db.db"))]
        },
        "backup": {
            "interval": 86400,  # Seconds between backups
            "path": str(os.path.abspath("simplecte/data/backups/")),
            "name": "{dbName}_{date}",
            "date": "%m-%d-%Y",
            "last_backup": None,
        },
    }

    def __init__(self, settings_path: str):
        self.settings_path = settings_path
        self.first_time = False

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
            try:
                with open(self.settings_path, "r") as settings_file:
                    settings = json.load(settings_file)

                return settings
            except:
                pass

        # Create the directory relative to the top-level of this project
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)

        settings = self.save_settings(self.template)
        self.first_time = True

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
        return "local"

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
