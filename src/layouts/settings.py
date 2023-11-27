import PySimpleGUI as sg

__all__ = (
    "get_settings_layout",
)


def get_general_layout():
    return [
        [sg.Text("Current Theme: "), sg.Combo(sg.theme_list(), default_value=sg.theme(), key="-SET_THEME-")],
    ]


def get_sqlite_layout():
    layout = [
        [sg.Text("SQLite Location Type:"), sg.Combo(["Local", "Remote"], key="-SET_SQLITE_LOCATION_TYPE-", enable_events=True)],
        [sg.Text("Database Path:"), sg.InputText(key="-SET_DB_PATH-"), sg.FileBrowse()],  # Disabled if remote
        [sg.Text("Database URL: "), sg.Input(key="-SET_DB_URL-")],
    ]

    return layout


def get_postgresql_layout():
    layout = [
        [sg.Text("Database Name: "), sg.Input(key="-SET_POSTGRESQL_DB_NAME-")],
        [sg.Text("Address: "), sg.Input(key="-SET_POSTGRESQL_ADDRESS-")],
        [sg.Text("Port: "), sg.Input(key="-SET_POSTGRESQL_PORT-")],
        [sg.Text("Username: "), sg.Input(key="-SET_POSTGRESQL_USERNAME-")],
        [sg.Text("Password: "), sg.Input(key="-SET_POSTGRESQL_PASSWORD-", password_char="*")],
        [sg.Checkbox("Show Password", key="-SET_POSTGRESQL_SHOW_PASSWORD-", enable_events=True),
         sg.Checkbox("Save Password", key="-SET_POSTGRESQL_SAVE_PASSWORD-")],
    ]

    return layout


def get_database_layout():
    layout = [
        # Always enabled
        [sg.Text("Current Database System:"), sg.Combo(["PostgreSQL", "SQLite"], key="-SET_DB_SYSTEM-", enable_events=True)],
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
