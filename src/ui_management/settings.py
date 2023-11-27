from typing import TYPE_CHECKING
import PySimpleGUI as sg

from ..layouts import get_settings_layout

if TYPE_CHECKING:
    from ..process.app import App

__all__ = (
    "settings_handler",
)


def update_settings_window(window: sg.Window, app: "App"):
    """
    Updates the settings window with the current settings values, to decide
    what is disabled and what to display.
    """
    window["-SET_THEME-"].update(value=app.settings.theme)

    if app.settings.database_system == "sqlite":
        window["-SET_POSTGRESQL_TAB-"].update(disabled=True)
        window["-SET_DB_SYSTEM-"].update(value="SQLite")

        if app.settings.database_location == "local":
            window["-SET_DB_URL-"].update(disabled=True)
            window["-SET_SQLITE_LOCATION_TYPE-"].update(value="Local")

        else:
            window["-SET_DB_PATH-"].update(disabled=True)
            window["-SET_SQLITE_LOCATION_TYPE-"].update(value="Remote")

    else:
        window["-SET_SQLITE_TAB-"].update(disabled=True)
        window["-SET_DB_SYSTEM-"].update(value="PostgreSQL")

    if app.settings.database_location == "local":
        window["-DB_PATH-"].update(value=app.settings.database_path)

    else:
        window["-SET_DB_URL-"].update(value=app.settings.database_address)

    window["-SET_POSTGRESQL_DB_NAME-"].update(value=app.settings.database_name)
    window["-SET_POSTGRESQL_ADDRESS-"].update(value=app.settings.database_address)
    window["-SET_POSTGRESQL_PORT-"].update(value=app.settings.database_port)
    window["-SET_POSTGRESQL_USERNAME-"].update(value=app.settings.database_username)
    window["-SET_POSTGRESQL_PASSWORD-"].update(value=app.settings.password)


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

            case "-SET_SAVE_SETTINGS-":
                settings.theme = values["-SET_THEME-"]

                settings.database_system = values["-SET_DB_SYSTEM-"].lower()

                if settings.database_system == "sqlite":
                    if settings.database_location.lower() == "local":
                        settings.database_path = values["-SET_DB_PATH-"]

                        if settings.database_path == "":
                            settings.database_path = app.settings.database_path

                    else:
                        settings.database_address = values["-SET_DB_URL-"]

                else:
                    settings.database_name = values["-SET_POSTGRESQL_DB_NAME-"]
                    settings.database_address = values["-SET_POSTGRESQL_ADDRESS-"]
                    settings.database_port = values["-SET_POSTGRESQL_PORT-"]
                    settings.database_username = values["-SET_POSTGRESQL_USERNAME-"]
                    settings.database_system = "postgres"

                    if values["-SET_POSTGRESQL_SAVE_PASSWORD-"]:
                        settings.password = values["-SET_POSTGRESQL_PASSWORD-"]

                    else:
                        settings.password = ""

                if settings == app.settings:
                    window.close()
                    break

                restart_win = sg.popup_yes_no(
                    "You must restart the application for the changes to take effect. Would you like to restart now?"
                )

                if restart_win == "Yes":
                    app.settings.save_settings(settings)
                    app.restart()

                app.settings.save_settings(settings)

                window.close()
                break

            case "-SET_DB_SYSTEM-":
                settings.database_system = values["-SET_DB_SYSTEM-"].lower()
                if settings.database_system == "sqlite":
                    window["-SET_SQLITE_TAB-"].update(disabled=False)
                    window["-SET_POSTGRESQL_TAB-"].update(disabled=True)

                else:
                    window["-SET_SQLITE_TAB-"].update(disabled=True)
                    window["-SET_POSTGRESQL_TAB-"].update(disabled=False)

            case "-SET_SQLITE_LOCATION_TYPE-":
                settings.database_location = values["-SET_SQLITE_LOCATION_TYPE-"].lower()
                if settings.database_location == "local":
                    window["-SET_DB_PATH-"].update(disabled=False)
                    window["-SET_DB_URL-"].update(disabled=True)

                else:
                    window["-SET_DB_PATH-"].update(disabled=True)
                    window["-SET_DB_URL-"].update(disabled=False)

            case "-SET_POSTGRESQL_SHOW_PASSWORD-":
                if values["-SET_POSTGRESQL_SHOW_PASSWORD-"]:
                    window["-SET_POSTGRESQL_PASSWORD-"].update(password_char="")

                else:
                    window["-SET_POSTGRESQL_PASSWORD-"].update(password_char="*")
