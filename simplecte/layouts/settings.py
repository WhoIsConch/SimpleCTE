import PySimpleGUI as sg

__all__ = ("get_settings_layout", "gen_saved_db_layout")


def gen_saved_db_layout(db_path: str, is_current: bool = False):
    db_title = " " + db_path.split("\\")[-1][0:-3] + " "

    if is_current:
        db_title += "(Current) "

    return sg.Frame(
        title=db_title,
        layout=[
            [
                sg.Text("Path: "),
                sg.Input(
                    db_path,
                    size=(None, 20),
                    key=f"-SAVED_DB::{db_path}",
                    readonly=True,
                    disabled_readonly_background_color=sg.theme_background_color(),
                ),
            ],
            [
                sg.Button("Open", key=f"-LOAD_SAVED_DB::{db_path}-"),
                sg.Button("Delete", key=f"-DELETE_SAVED_DB::{db_path}-"),
            ],
        ],
    )


def get_general_layout():
    return [
        [
            sg.Text("Current Theme: ", tooltip=" Change the app's theme! "),
            sg.Combo(
                sg.theme_list(),
                default_value=sg.theme(),
                readonly=True,
                key="-SET_THEME-",
                tooltip=" Change the app's theme! ",
            ),
        ],
    ]


def get_sqlite_layout():
    layout = [
        [
            sg.Text("Database Path:", tooltip=" The path to the file. "),
            sg.InputText(
                key="-SET_DB_PATH-",
                tooltip=" The path to the file. ",
                readonly=True,
                disabled_readonly_background_color=sg.theme_background_color(),
            ),
            sg.FileBrowse(tooltip=" Select the path to the file. "),
        ],
    ]

    return layout


def get_backup_layout():
    return [
        [
            sg.Checkbox("Perform Automated Backups", key="-BACKUP_ENABLED-"),
            sg.Checkbox("Run at System Startup", key="-BACKUP_STARTUP-"),
        ],
        [
            sg.Text("Backup Interval:"),
            sg.Combo(
                ["Hourly", "Daily", "Weekly", "Monthly", "Custom"],
                default_value="Daily",
                readonly=True,
                key="-BACKUP_INTERVAL-",
                enable_events=True,
            ),
            sg.Input(
                key="-BACKUP_INTERVAL_CUSTOM-",
                visible=False,
                default_text="1d2h3m4s",
                tooltip="Use d, h, m to mark the number before it as a day, hour, or minute. Unmarked numbers are seconds.",
            ),
        ],
        [
            sg.Text("Backup Path:"),
            sg.Input(
                key="-BACKUP_PATH-",
                disabled=True,
                disabled_readonly_background_color=sg.theme_background_color(),
            ),
            sg.FolderBrowse(),
        ],
        [
            sg.Button(button_text=" ? ", key="-BACKUP_NAME_HELP-"),
            sg.Text("Backup Name Format"),
            # sg.Text("This is the format you want the file names of your backups. Use {dbName} for the database's name and {date} for your set date format.", size=(10, 10)),
            sg.Input(default_text="{dbName}_{date}", key="-BACKUP_NAME-"),
        ],
        [
            sg.Button(button_text=" ? ", key="-BACKUP_NAME_HELP_2-"),
            sg.Text("Name Date Format"),
            sg.Input(default_text="%M-%D-%Y", key="-BACKUP_DATE-"),
        ],
    ]


def get_settings_layout():
    layout = [
        [
            sg.TabGroup(
                [
                    [sg.Tab("General", get_general_layout())],
                    [sg.Tab("Database", get_sqlite_layout())],
                    [
                        sg.Tab(
                            "Backup",
                            get_backup_layout(),
                            right_click_menu=[
                                "",
                                ["Code BTS::CODE(simplecte/utils/backup.py,65)"],
                            ],
                        )
                    ],
                ]
            )
        ],
        [
            sg.Button("Save", key="-SET_SAVE_SETTINGS-"),
            sg.Push(),
            sg.Button("Discard", key="-SET_CANCEL_SETTINGS-"),
        ],
    ]
    return layout
