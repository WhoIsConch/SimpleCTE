import PySimpleGUI as sg

__all__ = ("get_backup_layout",)


def get_backup_layout():
    path_tooltip = " The folder location to back up the database to "
    name_tooltip = " The name of the backup file "
    layout = [
        [
            sg.Text(
                "Back up your data! Data is backed up by copying the database file to a new\n"
                "directory. To restore a backup, you can simply copy the file and paste it where\n"
                "the old file was, or open the database directly via settings.",
                auto_size_text=True,
                right_click_menu=[
                    "",
                    [
                        "Code LYT::CODE(simplecte/layouts/backup.py,6)",
                        "Code BTS::CODE(simplecte/ui_management/backup.py,15)",
                    ],
                ],
            ),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Backup Location:", size=(15, 1), tooltip=path_tooltip),
            sg.InputText(key="-BACKUP_PATH-", size=(30, 1), tooltip=path_tooltip),
            sg.FolderBrowse(key="-BACKUP_BROWSE-", size=(10, 1), tooltip=path_tooltip),
        ],
        [
            sg.Text("Backup Name:", size=(15, 1), tooltip=name_tooltip),
            sg.InputText(key="-BACKUP_NAME-", size=(30, 1), tooltip=name_tooltip),
        ],
        [
            sg.Button("Backup", key="-BACKUP_BACKUP-", size=(10, 1)),
            sg.Button("Cancel", key="-BACKUP_CANCEL-", size=(10, 1)),
        ],
    ]

    return layout
