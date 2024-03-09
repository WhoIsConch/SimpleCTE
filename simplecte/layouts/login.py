import PySimpleGUI as sg

__all__ = ("get_login_layout",)


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
                        sg.Text(
                            "Server Address",
                            font=("Arial", 10),
                            tooltip=" The address of the server you are connecting to. ",
                        ),
                        sg.Input(
                            expand_x=True,
                            k="-SERVER-",
                            tooltip=" The address of the server you are connecting to. ",
                        ),
                    ],
                    [
                        sg.Text(
                            "Server Port",
                            font=("Arial", 10),
                            tooltip=" The port of the server you are connecting to. ",
                        ),
                        sg.Input(
                            expand_x=True,
                            k="-PORT-",
                            tooltip=" The port of the server you are connecting to. ",
                        ),
                    ],
                    [
                        sg.Text(
                            "Database Name",
                            font=("Arial", 10),
                            tooltip=" The name of the database you are connecting to. "
                            "Generally only useful for PostgreSQL.",
                        ),
                        sg.Input(
                            expand_x=True,
                            k="-DBNAME-",
                            tooltip=" The name of the database you are connecting to. "
                            "Generally only useful for PostgreSQL.",
                        ),
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text(
                            "Username",
                            font=("Arial", 10),
                            tooltip=" The username you are using to connect to the database. ",
                        ),
                        sg.Input(
                            expand_x=True,
                            k="-USERNAME-",
                            tooltip=" The username you are using to connect to the database. ",
                        ),
                    ],
                    [
                        sg.Text(
                            "Password",
                            font=("Arial", 10),
                            tooltip=" The password you are using to connect to the database. ",
                        ),
                        sg.Input(
                            expand_x=True,
                            password_char="*",
                            k="-PASSWORD-",
                            tooltip=" The password you are using to connect to the database. ",
                        ),
                    ],
                ]
            )
        ],
        [sg.Button("Exit"), sg.Button("Connect & Open", k="-LOGIN-")],
    ]
