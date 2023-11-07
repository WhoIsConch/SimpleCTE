import PySimpleGUI as sg

def login_constructor(
        server_address: str = "",
        server_port: str = "",
        database_name: str = "",
        username: str = ""
):
    login = [
        [
            sg.Column(
                [   
                    [sg.Text("Log In", font=("Arial", 20))],
                    [sg.Text("To access your database", font=("Arial", 10))],
                ],
                element_justification="center",
                expand_x=True
            )
        ],
        [
            sg.Column(
                [
                    [sg.Text("Server Address", font=("Arial", 10)), sg.Input(expand_x=True, k="-SERVER-", default_text=server_address)],
                    [sg.Text("Server Port", font=("Arial", 10)), sg.Input(expand_x=True, k="-PORT-", default_text=server_port)],
                    [sg.Text("Database Name", font=("Arial", 10)), sg.Input(expand_x=True, k="-DBNAME-", default_text=database_name)],
                    [sg.HorizontalSeparator()],
                    [sg.Text("Username", font=("Arial", 10)), sg.Input(expand_x=True, k="-USERNAME-", default_text=username)],
                    [sg.Text("Password", font=("Arial", 10)), sg.Input(expand_x=True, password_char="*", k="-PASSWORD-")]
                ]
            )
        ],
        [sg.Button("Exit"), sg.Button("Connect & Open", k="-LOGIN-")]
    ]
    return login

def main_constructor():
    layout = [
        [sg.Frame(
            title="Action Menu",
            expand_x=True,
            element_justification="center",
            layout=[
                [
                    sg.Button("Export by Filter"),
                    sg.Button("Export All"),
                    sg.Button("Settings"),
                    sg.Button("Backup"),
                    sg.Button("Help"),
                    sg.Button("Logout"),
                    sg.Button("Add Record")
                ]
            ]
        )
        ],
        [sg.Button("Search"), sg.Input(k="-SEARCH-"), sg.Combo(["Contacts", "Organizations"], k="-SEARCHTYPE-", tooltip="gay"), sg.Combo(["Status", "Alphabetical", "Type"], k="-SORTTYPE-")]
    ]
    return layout