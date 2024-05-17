import os
import json
import time
from datetime import timedelta, datetime as dt
import shutil
from dataclasses import dataclass

DATETIME_FORMAT = r"%m/%d/%Y %H:%M:%S"


@dataclass
class Settings:
    raw: dict
    db_path: str
    backup_path: str
    name_format: str
    date_format: str
    backup_interval: int
    last_backup: str

    @classmethod
    def load_settings(cls) -> "Settings":
        with open("simplecte/data/settings.json", "r") as f:
            settings = json.load(f)

        return cls(
            raw=settings,
            db_path=settings["database"]["path"],
            backup_path=settings["backup"]["path"],
            name_format=settings["backup"]["name"],
            date_format=settings["backup"]["date"],
            last_backup=settings["backup"]["lastBackup"],
            backup_interval=settings["backup"]["interval"],
        )

    def mark_backup(self) -> None:
        self.raw["backup"]["last_backup"] = dt.now().strftime(DATETIME_FORMAT)

        with open("simplecte/data/settings.json", "w") as f:
            json.dump(self.raw, f, indent=4)


def backup():
    while True:
        config = Settings.load_settings()

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

        config.mark_backup()

        time.sleep(config.backup_interval)


backup()
