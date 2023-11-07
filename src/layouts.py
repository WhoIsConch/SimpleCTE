import PySimpleGUI as sg
import typing
from enums import Screen
from pony.orm import db_session
if typing.TYPE_CHECKING:
    from main import App

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

@db_session
def main_constructor(app: "App"):
    filters = ["Status", "Alphabetical", "Type"]
    # app.screen = Screen.CONTACT_SEARCH

    if app.screen == Screen.ORG_SEARCH:
        fields = ["Name", "Status", "Primary Phone", "Address", "Custom Field Name", "Custom Field Value"]
        table_headings = ["Organization Name", "Type", "Primary Contact", "Status"]

        org_pages = app.db.get_organizations()

        table_values = []
        for org in org_pages:
            contact = org.contacts.filter(lambda c: c.org_titles[str(org.id)] == "Primary").first()
            contact_name = contact.name if contact else "No Primary Contact"
            table_values.append([org.name, org.type, contact_name, org.status])

    elif app.screen == Screen.CONTACT_SEARCH:
        fields = ["Name", "Status", "Primary Phone", "Address", "Custom Field Name", "Custom Field Value"]
        filters.append("Associated with resource...")
        table_headings = ["Name", "Organization(s)"]

        contact_pages = app.db.get_contacts()

        table_values = []
        for contact in contact_pages:
            table_values.append([contact.name, contact.organizations])

    layout = [
        [sg.Column(
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
                        layout=[[sg.Button("Export by Filter"),
                        sg.Button("Export All"),
                        sg.Button("Settings"),
                        sg.Button("Backup"),
                        sg.Button("Help"),
                        sg.Button("Logout"),
                        sg.Button("Add Record")]]
                    )
                ]
            ]
        )
        ],
        [
            sg.Button("Search"), 
            sg.Text("Search Query:"),
            sg.Input(k="-SEARCH-"), 
            sg.Text("Search Fields:"),
            sg.Combo(fields, k="-SEARCHFIELDS-"),
            sg.Text("Search In:"), 
            sg.Combo(["Contacts", "Organizations"], k="-SEARCHTYPE-", default_value="Contacts" if app.screen == Screen.CONTACT_SEARCH else "Organizations"), 
            sg.Text("Search Filters:"), 
            sg.Combo(filters, k="-SORTTYPE-")
        ],
        [sg.Column(
            background_color=sg.theme_progress_bar_color()[1],
            expand_x=True,
            expand_y=True,
            element_justification="center",
            pad=((0, 0), (20, 0)),
            layout=[
                [sg.Text("Contact Search" if app.screen == Screen.CONTACT_SEARCH else "Organization Search", background_color=sg.theme_progress_bar_color()[1], font=("Arial", 20))],
                [sg.Table(
                    headings = table_headings,
                    values=table_values,
                    expand_x=True,
                    font=("Arial", 15),
                    right_click_menu= ['&Right', ['Right', '!&Click', '&Menu', 'E&xit', 'Properties']],
                    right_click_selects=True,
                    k="-TABLE-",
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    row_height=30,
                    alternating_row_color=sg.theme_progress_bar_color()[1],
                    justification="center"
                )]
            ]
        )]
    ]
    return layout