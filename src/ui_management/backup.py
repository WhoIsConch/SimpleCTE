from src.layouts import get_backup_layout
import shutil

import PySimpleGUI as sg

__all__ = (
    "backup_handler",
)


def backup_handler(app: "App"):
    window = sg.Window("Backup", get_backup_layout(), finalize=True, modal=True)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-BACKUP_CANCEL-":
                window.close()
                break

            case "-BACKUP_BACKUP-":
                window.close()
                # back up the file
                shutil.copy(app.settings.database_path, values["-BACKUP_PATH-"] + "/" + values["-BACKUP_NAME-"] + ".db")
                break
