import PySimpleGUI as sg

__all__ = (
    "get_login_layout",
)


def get_login_layout():
    return [
        [
            sg.Column(
                [
                    [sg.Text("Log In", font=("Arial", 20))],
                    [sg.Text("To access your database", font=("Arial", 10))],
                ],
                element_justification="center",
                expand_x=True,
            )
        ],
        [
            sg.Column(
                [
                    [
                        sg.Text("Server Address", font=("Arial", 10)),
                        sg.Input(
                            expand_x=True, k="-SERVER-"
                        ),
                    ],
                    [
                        sg.Text("Server Port", font=("Arial", 10)),
                        sg.Input(expand_x=True, k="-PORT-"),
                    ],
                    [
                        sg.Text("Database Name", font=("Arial", 10)),
                        sg.Input(expand_x=True, k="-DBNAME-"),
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text("Username", font=("Arial", 10)),
                        sg.Input(expand_x=True, k="-USERNAME-"),
                    ],
                    [
                        sg.Text("Password", font=("Arial", 10)),
                        sg.Input(expand_x=True, password_char="*", k="-PASSWORD-"),
                    ],
                ]
            )
        ],
        [sg.Button("Exit"), sg.Button("Connect & Open", k="-LOGIN-")],
    ]
