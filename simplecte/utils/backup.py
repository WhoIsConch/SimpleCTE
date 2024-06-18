"""
SimpleCTE backup program. This will autonomously back up your database files to the specified location in settings.json.
This script is not meant to be imported by the program, and is meant to run as a separate process.
This script is invoked by simplecte/process/settings.py line 103 (spawn_backup_process) and is not meant to be run manually.
"""

import os
import json
import time
from datetime import timedelta, datetime as dt
import shutil
from dataclasses import dataclass
from filelock import FileLock

DATETIME_FORMAT = r"%m/%d/%Y %H:%M:%S"
# TODO: Make sure this can run on its own, from startup.


@dataclass
class Settings:
    raw: dict
    db_path: str
    backup_path: str
    name_format: str
    date_format: str
    backup_interval: int
    last_backup: str
    backup_enabled: bool

    @classmethod
    def load_settings(cls) -> "Settings":
        with FileLock("settings.lock"):
            with open("simplecte/data/settings.json", "r") as f:
                settings = json.load(f)

        written_pid = settings["backup"]["processId"]

        self = cls(
            raw=settings,
            db_path=settings["database"]["path"],
            backup_path=settings["backup"]["path"],
            name_format=settings["backup"]["name"],
            date_format=settings["backup"]["date"],
            last_backup=settings["backup"]["lastBackup"],
            backup_interval=settings["backup"]["interval"],
            backup_enabled=settings["backup"]["enabled"],
        )

        if written_pid is None or written_pid != os.getpid():
            settings["backup"]["processId"] = os.getpid()

            self.write_settings(mark_backup=False)

        return self

    def write_settings(self, mark_backup=True) -> None:
        if mark_backup:
            self.raw["backup"]["lastBackup"] = dt.now().strftime(DATETIME_FORMAT)

        with FileLock("settings.lock"):
            with open("simplecte/data/settings.json", "w") as f:
                json.dump(self.raw, f, indent=4)


def backup():
    while True:
        config = Settings.load_settings()

        if not config.backup_enabled:
            exit()

        if config.last_backup is not None:
            last_backup_time = dt.strptime(config.last_backup, DATETIME_FORMAT)
            next_backup_time = last_backup_time + timedelta(
                seconds=config.backup_interval
            )
            time_to_next_backup = (next_backup_time - dt.now()).total_seconds()

            if time_to_next_backup > 0:
                time.sleep(time_to_next_backup)
                continue

        db_name = config.db_path.split("\\")[-1][0:-3]
        date = dt.now().strftime(config.date_format)
        backup = (
            config.backup_path
            + "\\"
            + config.name_format.format(dbName=db_name, date=date)
            + ".db"
        )

        if not os.path.exists(config.backup_path):
            os.makedirs(config.backup_path)

        shutil.copy(config.db_path, backup)

        config.write_settings()

        time.sleep(config.backup_interval)


backup()
