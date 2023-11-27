from typing import TYPE_CHECKING
import PySimpleGUI as sg

from ..layouts import get_settings_layout

if TYPE_CHECKING:
    from ..process.app import App

__all__ = (
    "settings_handler",
)


def settings_handler(app: "App"):
    window = sg.Window("Settings", get_settings_layout(), finalize=True, modal=True)

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

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-SET_CANCEL_SETTINGS-":
                window.close()
                break

            case "-SET_SAVE_SETTINGS-":
                app.settings.theme = values["-SET_THEME-"]

                app.settings.database_system = values["-SET_DB_SYSTEM-"]

                if app.settings.database_system == "sqlite":
                    if app.settings.database_location == "local":
                        app.settings.database_path = values["-SET_DB_PATH-"]

                    else:
                        app.settings.database_address = values["-SET_DB_URL-"]

                else:
                    app.settings.database_name = values["-SET_POSTGRESQL_DB_NAME-"]
                    app.settings.database_address = values["-SET_POSTGRESQL_ADDRESS-"]
                    app.settings.database_port = values["-SET_POSTGRESQL_PORT-"]
                    app.settings.database_username = values["-SET_POSTGRESQL_USERNAME-"]

                    if values["-SET_POSTGRESQL_SAVE_PASSWORD-"]:
                        app.settings.password = values["-SET_POSTGRESQL_PASSWORD-"]

                    else:
                        app.settings.password = ""

                app.settings.save_settings()

                window.close()
                break

            case "-SET_DB_SYSTEM-":
                if values["-SET_DB_SYSTEM-"] == "SQLite":
                    window["-SET_SQLITE_TAB-"].update(disabled=False)
                    window["-SET_POSTGRESQL_TAB-"].update(disabled=True)

                else:
                    window["-SET_SQLITE_TAB-"].update(disabled=True)
                    window["-SET_POSTGRESQL_TAB-"].update(disabled=False)

            case "-SET_SQLITE_LOCATION_TYPE-":
                if values["-SET_SQLITE_LOCATION_TYPE-"] == "local":
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
