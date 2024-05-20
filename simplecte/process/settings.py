import json
import os
from utils.enums import BackupInterval
import subprocess
from filelock import FileLock
import pylnk3

__all__ = ("Settings",)


class Settings:
    template = {
        "theme": "dark",
        "database": {
            "path": str(os.path.abspath("simplecte/data/db.db")),
        },
        "backup": {
            "interval": 86400,  # Seconds between backups
            "path": str(os.path.abspath("simplecte/data/backups/")),
            "name": "{dbName}_{date}",
            "date": "%m-%d-%Y",
            "lastBackup": None,
            "enabled": False,
            "processId": None,
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
        # Use a lock here too
        lock = FileLock("settings.lock")
        with lock:
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

        # Use a lock because this file can also be accessed by the backup process
        lock = FileLock("settings.lock")
        with lock:
            with open(self.settings_path, "w") as settings_file:
                json.dump(settings, settings_file, indent=4)

        return settings

    def copy(self) -> "Settings":
        """
        Return a copy of the settings.
        """
        return Settings(self.settings_path)

    def spawn_backup_process(self) -> None:
        # We don't want to bother starting the process if the user doesn't have backups enabled
        # This should be handled *before* this method is called, but it's always nice to check twice
        if not self.backup_enabled:
            return

        def spawn_and_save():
            process = subprocess.Popen(
                ["python", "simplecte/utils/backup.py"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            self.settings["backup"]["processId"] = process.pid

        # Make sure the backup process is running so we are able to backup
        if self.backup_processId is None:
            spawn_and_save()
        else:
            try:
                os.kill(self.backup_processId, 0)
            except (OSError, SystemError):
                spawn_and_save()

        # Now our process must surely be running

    def backup_on_startup():
        startup_folder = os.path.expanduser(
            r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
        )
        shortcut_path = os.path.join(startup_folder, "simplecte-backup.lnk")

        lnk = pylnk3.LNK()
        lnk.target = os.path.abspath("simplcte/utils/backup.py")
        lnk.save(shortcut_path)

    def __getattr__(self, name: str) -> str | int | None:
        parts = name.split("_")

        try:
            if len(parts) == 1:
                return self.settings[name]

            else:
                return self.settings[parts[0]][parts[1]]
        except IndexError:
            return None

    @property
    def absolute_database_path(self) -> str:
        """
        Get the current absolute database path.
        """
        return os.path.abspath(self.database_path)

    @property
    def backup_interval(self) -> BackupInterval | int:
        try:
            return BackupInterval(self.backup_interval_)
        except ValueError:
            return self.backup_interval_

    @backup_interval.setter
    def set_backup_interval(self, value: BackupInterval | int):
        self.backup_interval_ = (
            value.value if isinstance(BackupInterval, value) else value
        )
