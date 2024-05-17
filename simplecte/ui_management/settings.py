from typing import TYPE_CHECKING
import PySimpleGUI as sg

from layouts import get_settings_layout

if TYPE_CHECKING:
    from process.app import App

__all__ = ("settings_handler",)


def update_settings_window(window: sg.Window, app: "App"):
    """
    Updates the settings window with the current settings values, to decide
    what is disabled and what to display.
    """
    window["-SET_THEME-"].update(value=app.settings.theme)
    window["-SET_DB_PATH-"].update(value=app.settings.database_path)


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

                settings.database_path = values["-SET_DB_PATH-"]

                if settings.database_path == "":
                    settings.database_path = app.settings.database_path

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
