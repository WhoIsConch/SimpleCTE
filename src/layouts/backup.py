import PySimpleGUI as sg

__all__ = (
    "get_backup_layout",
)


def get_backup_layout():
    layout = [
        [
            sg.Text("Backup Location:", size=(15, 1)),
            sg.InputText(key="-BACKUP_PATH-", size=(30, 1)),
            sg.FolderBrowse(key="-BACKUP_BROWSE-", size=(10, 1)),
        ],
        [
            sg.Text("Backup Name:", size=(15, 1)),
            sg.InputText(key="-BACKUP_NAME-", size=(30, 1)),
        ],
        [
            sg.Button("Backup", key="-BACKUP_BACKUP-", size=(10, 1)),
            sg.Button("Cancel", key="-BACKUP_CANCEL-", size=(10, 1)),
        ],
    ]

    return layout