import PySimpleGUI as sg
import typing
from enums import Screen
from pony.orm import db_session

if typing.TYPE_CHECKING:
    from main import App


def format_phone(phone_number: int) -> str:
    phone_number = str(phone_number)
    if len(phone_number) == 10:
        return f"({phone_number[:3]}) {phone_number[3:6]}-{phone_number[6:]}"
    elif len(phone_number) == 11:
        return f"+{phone_number[0]} ({phone_number[1:4]}) {phone_number[4:7]}-{phone_number[7:]}"
    else:
        return phone_number


def login_constructor(
    server_address: str = "",
    server_port: str = "",
    database_name: str = "",
    username: str = "",
):
    login = [
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
                            expand_x=True, k="-SERVER-", default_text=server_address
                        ),
                    ],
                    [
                        sg.Text("Server Port", font=("Arial", 10)),
                        sg.Input(expand_x=True, k="-PORT-", default_text=server_port),
                    ],
                    [
                        sg.Text("Database Name", font=("Arial", 10)),
                        sg.Input(
                            expand_x=True, k="-DBNAME-", default_text=database_name
                        ),
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text("Username", font=("Arial", 10)),
                        sg.Input(expand_x=True, k="-USERNAME-", default_text=username),
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
    return login


def get_contact_table(app: "App"):
    fields = [
        "Name",
        "Status",
        "Primary Phone",
        "Address",
        "Custom Field Name",
        "Custom Field Value",
    ]
    filters = ["Status", "Alphabetical", "Type", "Associated with resource..."]
    table_headings = ["Name", "Organization(s)", "Primary Phone"]

    contact_pages = app.db.get_contacts()

    table_values = []
    for contact in contact_pages:
        org_name = contact.organizations.filter(lambda c: c.id == 1).first()

        if org_name:
            org_name = org_name.name
        else:
            org_name = "No Organization"

        table_values.append(
            [
                contact.name,
                org_name,
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    return sg.Table(
        headings=table_headings,
        values=table_values,
        expand_x=True,
        font=("Arial", 15),
        right_click_menu=[
            "&Right",
            ["Right", "!&Click", "&Menu", "E&xit", "Properties"],
        ],
        right_click_selects=True,
        k="-CONTACT_TABLE-",
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        row_height=40,
        alternating_row_color=sg.theme_progress_bar_color()[1],
        justification="center",
        num_rows=5,
    ), filters, fields


def get_organization_table(app: "App"):
    filters = ["Status", "Alphabetical", "Type"]

    fields = [
        "Name",
        "Status",
        "Primary Phone",
        "Address",
        "Custom Field Name",
        "Custom Field Value",
    ]
    table_headings = ["Organization Name", "Type", "Primary Contact", "Status"]

    org_pages = app.db.get_organizations()

    table_values = []
    for org in org_pages:
        contact = org.contacts.filter(
            lambda c: c.org_titles[str(org.id)] == "Primary"
        ).first()
        contact_name = contact.name if contact else "No Primary Contact"
        table_values.append([org.name, org.type, contact_name, org.status])

    return sg.Table(
        headings=table_headings,
        values=table_values,
        expand_x=True,
        font=("Arial", 15),
        right_click_menu=[
            "&Right",
            ["Right", "!&Click", "&Menu", "E&xit", "Properties"],
        ],
        right_click_selects=True,
        k="-ORG_TABLE-",
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        row_height=40,
        alternating_row_color=sg.theme_progress_bar_color()[1],
        justification="center",
        num_rows=5,
    ), filters, fields


@db_session
def main_constructor(app: "App"):
    contact_table, contact_filters, contact_fields = get_contact_table(app)
    org_table, org_filters, org_fields = get_organization_table(app)

    if app.screen == Screen.CONTACT_SEARCH:
        fields = contact_fields
        filters = contact_filters

    elif app.screen == Screen.ORG_SEARCH:
        fields = org_fields
        filters = org_filters

    layout = [
        [
            sg.Column(
                expand_x=True,
                element_justification="center",
                background_color=sg.theme_progress_bar_color()[1],
                pad=((0, 0), (0, 10)),
                layout=[
                    [
                        sg.Column(
                            pad=5,
                            element_justification="center",
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Button("Export by Filter", k="-EXPORT_FILTER-"),
                                    sg.Button("Export All", k="-EXPORT_ALL-"),
                                    sg.Button("Settings", k="-SETTINGS-"),
                                    sg.Button("Backup", k="-BACKUP-"),
                                    sg.Button("Help", k="-HELP-"),
                                    sg.Button("Logout", k="-LOGOUT-"),
                                    sg.Button("Add Record", k="-ADD_RECORD-"),
                                ]
                            ],
                        )
                    ]
                ],
            )
        ],
        [
            sg.Column(
                expand_x=True,
                pad=((0, 0), (0, 10)),
                layout=[
                    [
                        sg.Button("Search", k="-SEARCH-"),
                        sg.Text("Search Query:"),
                        sg.Input(k="-SEARCH-"),
                        sg.Text("Search In:"),
                        sg.Combo(
                            ["Contacts", "Organizations"],
                            k="-SEARCHTYPE-",
                            default_value="Contacts"
                            if app.screen == Screen.CONTACT_SEARCH
                            else "Organizations",
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Search Fields:"),
                        sg.Combo(fields, k="-SEARCHFIELDS-", expand_x=True),
                        sg.Text("Search Filters:"),
                        sg.Combo(filters, k="-SORTTYPE-", expand_x=True),
                    ],
                ],
            )
        ],
        [
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                expand_y=True,
                element_justification="center",
                key="-ORG_SCREEN-",
                visible=app.screen == Screen.ORG_SEARCH,
                layout=[
                    [
                        sg.Text(
                            "Organization Search",
                            background_color=sg.theme_progress_bar_color()[1],
                            font=("Arial", 20),
                        )
                    ],
                    [
                        org_table,
                    ],
                ],
            ),
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                expand_y=True,
                element_justification="center",
                key="-CONTACT_SCREEN-",
                visible=app.screen == Screen.CONTACT_SEARCH,
                layout=[
                    [
                        sg.Text(
                            "Contact Search",
                            background_color=sg.theme_progress_bar_color()[1],
                            font=("Arial", 20),
                        ),
                    ],
                    [
                        contact_table,
                    ],
                ],
            ),
        ],
    ]
    return layout
