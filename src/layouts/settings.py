import PySimpleGUI as sg

__all__ = (
    "get_settings_layout",
)


def get_general_layout():
    return [
        [
            sg.Text("Current Theme: ", tooltip=" Change the app's theme! "),
            sg.Combo(sg.theme_list(), default_value=sg.theme(), key="-SET_THEME-", tooltip=" Change the app's theme! ")
        ],
    ]


def get_sqlite_layout():
    layout = [
        [sg.Text("SQLite Location Type:", tooltip=" Whether to store the database locally or remotely. "),
         sg.Combo(["Local", "Remote"], key="-SET_SQLITE_LOCATION_TYPE-", enable_events=True,
                  tooltip=" Whether to store the database locally or remotely. ")],
        [sg.Text("Database Path:", tooltip=" The path to the file. "),
         sg.InputText(key="-SET_DB_PATH-", tooltip=" The path to the file. "),
         sg.FileBrowse(tooltip=" Select the path to the file. ")],  # Disabled if remote
        [sg.Text("Database URL: ", tooltip=" The URL to the database server, if remote. "), sg.Input(key="-SET_DB_URL-", tooltip=" The URL to the database server, if remote. ")],  # Disabled if local
    ]

    return layout


def get_postgresql_layout():
    layout = [
        [sg.Text("Database Name: "), sg.Input(key="-SET_POSTGRESQL_DB_NAME-", tooltip=" The name of the database. ")],
        [sg.Text("Address: "), sg.Input(key="-SET_POSTGRESQL_ADDRESS-", tooltip=" The address of the database server. ")],
        [sg.Text("Port: "), sg.Input(key="-SET_POSTGRESQL_PORT-", tooltip=" The port of the database server. ")],
        [sg.Text("Username: "), sg.Input(key="-SET_POSTGRESQL_USERNAME-", tooltip=" The username to connect with. ")],
        [sg.Text("Password: "), sg.Input(key="-SET_POSTGRESQL_PASSWORD-", password_char="*", tooltip=" The password to connect with. ")],
        [sg.Checkbox("Show Password", key="-SET_POSTGRESQL_SHOW_PASSWORD-", enable_events=True, tooltip=" Show the password in plain text. "),
         sg.Checkbox("Save Password", key="-SET_POSTGRESQL_SAVE_PASSWORD-", tooltip=" Save the password to the settings file. ")],
    ]

    return layout


def get_database_layout():
    layout = [
        # Always enabled
        [sg.Text("Current Database System:"),
         sg.Combo(["PostgreSQL", "SQLite"], key="-SET_DB_SYSTEM-", enable_events=True, tooltip=" The database system to use. ")],
        [sg.HorizontalSeparator()],
        # Disabled if SQLite is not selected
        [sg.TabGroup(
            [
                [sg.Tab('SQLite', get_sqlite_layout(), key="-SET_SQLITE_TAB-")],
                [sg.Tab('PostgreSQL', get_postgresql_layout(), key="-SET_POSTGRESQL_TAB-")]
            ]
        )],
    ]

    return layout


def get_settings_layout():
    layout = [
        [sg.TabGroup(
            [
                [sg.Tab('General', get_general_layout())],
                [sg.Tab('Database', get_database_layout())]
            ]
        )],
        [sg.Button("Save", key="-SET_SAVE_SETTINGS-"), sg.Push(), sg.Button("Discard", key="-SET_CANCEL_SETTINGS-")],
    ]
    return layout
