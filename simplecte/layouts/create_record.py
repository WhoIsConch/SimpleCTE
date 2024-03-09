import PySimpleGUI as sg

__all__ = (
    "get_create_contact_layout",
    "get_create_org_layout",
)


def get_create_contact_layout():
    return [
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Text(
                            "Create a new contact!\nFields marked with an asterisk (*) are required.",
                            font=("Arial", 15),
                            justification="center",
                        ),
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text("*First Name: "),
                        sg.Input(k="-FIRST_NAME-", tooltip="The contact's first name."),
                    ],
                    [
                        sg.Text("*Last Name: "),
                        sg.Input(k="-LAST_NAME-", tooltip="The contact's last name."),
                    ],
                    [
                        sg.Text("Status: "),
                        sg.Input(
                            k="-STATUS-",
                            tooltip="The contact's status, e.g. 'Active' or 'Former'",
                        ),
                    ],
                    [
                        sg.Text("Primary Phone: "),
                        sg.Input(
                            k="-PHONE_NUMBER-",
                            tooltip="The contact's primary phone number. You can add more later.",
                        ),
                    ],
                    [
                        sg.Text("Address: "),
                        sg.Input(
                            k="-ADDRESS-",
                            tooltip="The contact's primary address. You can add more later.",
                        ),
                    ],
                    [
                        sg.Text("Availability: "),
                        sg.Input(
                            k="-AVAILABILITY-",
                            tooltip="The contact's availability, e.g. weekends or 9am-5pm",
                        ),
                    ],
                ],
            )
        ],
        [
            sg.Button("Add Contact", k="-CONFIRM_ADD_CONTACT-"),
            sg.Button("Cancel", k="-CANCEL-"),
        ],
    ]


def get_create_org_layout():
    return [
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Text(
                            "Create a new organization!\nFields marked with an asterisk (*) are required.",
                            font=("Arial", 15),
                            justification="center",
                        ),
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text("*Name: "),
                        sg.Input(k="-NAME-", tooltip="The organization's name."),
                    ],
                    [
                        sg.Text("*Type: "),
                        sg.Input(
                            k="-TYPE-",
                            tooltip="The organization's type, e.g. 'Food Bank' or 'Shelter'.",
                        ),
                    ],
                    [
                        sg.Text("Status: "),
                        sg.Input(
                            k="-STATUS-",
                            tooltip="The organization's status, e.g. 'Active' or 'Former'",
                        ),
                    ],
                    [
                        sg.Text("Primary Phone: "),
                        sg.Input(
                            k="-PHONE_NUMBER-",
                            tooltip="The organization's primary phone number. You can add "
                            "more later.",
                        ),
                    ],
                    [
                        sg.Text("Address: "),
                        sg.Input(
                            k="-ADDRESS-",
                            tooltip="The organization's primary address. You can add more later.",
                        ),
                    ],
                ],
            )
        ],
        [
            sg.Button("Add Organization", k="-CONFIRM_ADD_ORGANIZATION-"),
            sg.Button("Cancel", k="-CANCEL-"),
        ],
    ]
