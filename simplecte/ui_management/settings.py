from typing import TYPE_CHECKING
import PySimpleGUI as sg
from utils.enums import BackupInterval
import datetime as dt

from layouts import get_settings_layout

if TYPE_CHECKING:
    from process.app import App

__all__ = ("settings_handler",)


def parse_custom_interval(interval: str):
    """
    Parse a custom interval, like 1d2h3m4s, into seconds, like 93784.
    """
    time_units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    total_seconds = 0
    remaining_str = interval

    for unit, seconds_per_unit in time_units.items():
        if unit in remaining_str:
            value, remaining_str = remaining_str.split(unit)
            total_seconds += int(value) * seconds_per_unit

    return total_seconds


def format_custom_interval(interval: int):
    delta = dt.timedelta(seconds=interval)

    days = delta.days
    hours = delta.seconds // 3600 % 24
    minutes = delta.seconds // 60 % 60
    seconds = delta.seconds % 60

    # Format the time string with leading zeros for days, hours, minutes if needed
    return (
        (f"{days}d" if days else "")
        + (f"{hours}h" if hours else "")
        + (f"{minutes}m" if minutes else "")
        + (f"{seconds}s" if seconds else "")
    )


def update_settings_window(window: sg.Window, app: "App"):
    """
    Updates the settings window with the current settings values, to decide
    what is disabled and what to display.
    """
    window["-SET_THEME-"].update(value=app.settings.theme)
    window["-SET_DB_PATH-"].update(value=app.settings.absolute_database_path)

    interval_str = "Custom"

    if isinstance(app.settings.backup_interval, int):
        window["-BACKUP_INTERVAL_CUSTOM-"].update(
            visible=True, value=format_custom_interval(app.settings.backup_interval)
        )
    else:
        interval_str = app.settings.backup_interval.name.capitalize()

    window["-BACKUP_INTERVAL-"].update(value=interval_str)
    window["-BACKUP_PATH-"].update(value=app.settings.backup_path)
    window["-BACKUP_NAME-"].update(value=app.settings.backup_name)
    window["-BACKUP_DATE-"].update(value=app.settings.backup_date)


def settings_handler(app: "App"):
    window = sg.Window("Settings", get_settings_layout(), finalize=True, modal=True)
    settings = app.settings.copy()

    update_settings_window(window, app)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-SET_CANCEL_SETTINGS-":
                window.close()
                break

            # TODO: Fix this, it doesn't work
            case "-BACKUP_NAME_HELP-":
                sg.Window(
                    title="Backup Names and Dates",
                    layout=[
                        [
                            sg.Multiline(
                                "Backup names and dates are special fields that dynamically change the name and date on a backup. This helps keep them organized.\nBackup names are formatted with {dbName} and {date}, where dbName is the name of your database file and date is your date format. The date format is formatted with %M, %D, and %Y, which represent the month, day, and year respectively.",
                                size=(200, 200),
                            )
                        ]
                    ],
                    finalize=True,
                    modal=True,
                ).read()
                break

            case "-SET_SAVE_SETTINGS-":
                settings.theme = values["-SET_THEME-"]
                settings.database_path = values["-SET_DB_PATH-"]

                if settings.database_path == "":
                    settings.database_path = app.settings.database_path

                if values["-BACKUP_INTERVAL-"] == "Custom":
                    settings.settings["backup"]["interval"] = parse_custom_interval(
                        values["-BACKUP_INTERVAL_CUSTOM-"]
                    )
                else:
                    settings.settings["backup"]["interval"] = getattr(
                        BackupInterval, values["-BACKUP_INTERVAL-"].upper()
                    ).value

                for setting in settings.backup:
                    # Skip this because it cannot be edited by the user
                    if setting == "lastBackup" or setting == "interval":
                        continue

                    settings.settings["backup"][setting] = values[
                        f"-BACKUP_{setting.upper()}-"
                    ]

                if settings == app.settings:
                    window.close()
                    break

                restart_win = sg.popup_yes_no(
                    "You must restart the application for the changes to take effect. Would you like to restart now?"
                )

                app.settings.save_settings(settings)

                if restart_win == "Yes":
                    app.restart()

                window.close()
                break

            case "-BACKUP_INTERVAL-":
                if values["-BACKUP_INTERVAL-"] == "Custom":
                    window["-BACKUP_INTERVAL_CUSTOM-"].update(visible=True)
                else:
                    window["-BACKUP_INTERVAL_CUSTOM-"].update(visible=False)
