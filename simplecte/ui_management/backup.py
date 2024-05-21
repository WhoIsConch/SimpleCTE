from layouts import get_backup_layout
import shutil
import os
from process.events.debug import handle_debug

import PySimpleGUI as sg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simplecte.process import App

__all__ = ("backup_handler",)


def backup_handler(app: "App"):
    window = sg.Window("Backup", get_backup_layout(), finalize=True, modal=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "-BACKUP_CANCEL-":
            window.close()
            break

        if event.find("CODE") != -1:
            handle_debug(event)

        match event:
            case "-BACKUP_BACKUP-":
                # Check if the backup name violates Windows' file naming rules
                if any(c in values["-BACKUP_NAME-"] for c in '\\/:*?"<>|'):
                    sg.popup(
                        "The backup name cannot contain any of the following characters: "
                        '\\/:*?"<>|'
                    )
                    continue

                if not values["-BACKUP_NAME-"] or not values["-BACKUP_PATH-"]:
                    sg.popup("The backup name and path are required.")
                    continue

                if not os.path.exists(values["-BACKUP_PATH-"]):
                    sg.popup("The backup path does not exist.")
                    continue

                window.close()
                # back up the file
                shutil.copy(
                    app.settings.database_path,
                    values["-BACKUP_PATH-"] + "/" + values["-BACKUP_NAME-"] + ".db",
                )
                break
