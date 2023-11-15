import PySimpleGUI as sg
import typing
from enums import Screen, AppStatus
from pony.orm import db_session
from threading import Thread
from database import Contact, Organization, Resource

if typing.TYPE_CHECKING:
    from main import App


def format_phone(phone_number: int) -> str:
    """
    Convert a ten-digit or eleven-digit phone number, such as
    1234567890 or 11234567890, into a formatted phone number, such as
    (123) 456-7890 or +1 (123) 456-7890.
    """
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
    """
    Build the login screen layout.
    """
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


def get_action_bar(screen: Screen) -> list[list[sg.Button]]:
    """
    Return the action bar for the given screen.
    """
    if screen == Screen.CONTACT_SEARCH or screen == Screen.ORG_SEARCH:
        layout = [
            [
                sg.Button("Export by Filter", k="-EXPORT_FILTER-"),
                sg.Button("Export All", k="-EXPORT_ALL-"),
                sg.Button("Settings", k="-SETTINGS-"),
                sg.Button("Backup", k="-BACKUP-"),
                sg.Button("Help", k="-HELP-"),
                sg.Button("Logout", k="-LOGOUT-"),
                sg.Button("Add Record", k="-ADD_RECORD-"),
            ]
        ]
    else:
        layout = [
            [
                sg.Button("Export", k="-EXPORT-"),
                sg.Button("Settings", k="-SETTINGS-"),
                sg.Button("Backup", k="-BACKUP-"),
                sg.Button("Help", k="-HELP-"),
                sg.Button("Logout", k="-LOGOUT-"),
                sg.Button("Add Record", k="-ADD_RECORD-"),
            ]
        ]

    return layout


@db_session
def get_contact_table(app: "App", values_only: bool = False, search_info: dict[str, str, str] | None = None) -> sg.Table | list[list[str]]:
    """
    Build the table that includes information of contacts.
    """
    fields = [
        "Name",
        "Status",
        "Primary Phone",
        "Address",
        "Custom Field Name",
        "Custom Field Value",
    ]
    table_headings = ["Name", "Organization(s)", "Primary Phone"]

    if search_info:
        contact_pages = app.db.get_contacts(**search_info)
    else:
        contact_pages = app.db.get_contacts()

    if not contact_pages:
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

    if values_only:
        return table_values

    return sg.Table(
        headings=table_headings,
        values=table_values,
        expand_x=True,
        font=("Arial", 15),
        right_click_menu=[
            "&Right",
            ["View", "Edit", "Delete"],
        ],
        right_click_selects=True,
        k="-CONTACT_TABLE-",
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        row_height=40,
        alternating_row_color=sg.theme_progress_bar_color()[1],
        justification="center",
        enable_click_events=True,
        num_rows=5,
    ), fields


@db_session
def lazy_load_contact_values(app: "App"):
    """
    Lazy load contact values.

    This method is meant to be called in a separate thread,
    and will get all the values from the database and update the table
    to include them.
    """
    values = []

    for contact in app.db.get_contacts():
        org_name = contact.organizations.filter(lambda c: c.id == 1).first()

        if org_name:
            org_name = org_name.name
        else:
            org_name = "No Organization"

        values.append(
            [
                contact.name,
                org_name,
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    while app.status == AppStatus.READY:
        app.window["-CONTACT_TABLE-"].update(values=values)
        break


@db_session
def get_organization_table(app: "App", values_only: bool = False, search_info: dict[str, str, str] | None = None):
    """
    Build the table that includes information of organizations.
    """
    fields = [
        "Name",
        "Status",
        "Primary Phone",
        "Address",
        "Custom Field Name",
        "Custom Field Value",
    ]
    table_headings = ["Organization Name", "Type", "Primary Contact", "Status"]

    if search_info:
        org_pages = app.db.get_organizations(**search_info)
    else:
        org_pages = app.db.get_organizations()

    table_values = []
    for org in org_pages:
        contact = org.primary_contact
        contact_name = contact.name if contact else "No Primary Contact"
        table_values.append([org.name, org.type, contact_name, org.status])

    if values_only:
        return table_values

    return sg.Table(
        headings=table_headings,
        values=table_values,
        expand_x=True,
        font=("Arial", 15),
        right_click_menu=[
            "&Right",
            ["View", "Edit", "Delete"],
        ],
        right_click_selects=True,
        enable_click_events=True,
        k="-ORG_TABLE-",
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        row_height=40,
        alternating_row_color=sg.theme_progress_bar_color()[1],
        justification="center",
        num_rows=5,
    ), fields


@db_session
def lazy_load_org_values(app: "App", search_info: dict[str, str, str] | None = None):
    """
    Lazy load organization values.

    This method is meant to be called in a separate thread,
    and will get all the values from the database and update the table
    to include them.
    """
    values = []

    if search_info:
        orgs = app.db.get_organizations(**search_info, paginated=False)
    else:
        orgs = app.db.get_organizations(paginated=False)

    for org in orgs:
        contact = org.primary_contact
        contact_name = contact.name if contact else "No Primary Contact"
        values.append([org.name, org.type, contact_name, org.status])

    while app.status == AppStatus.READY:
        app.window["-ORG_TABLE-"].update(values=values)
        break


def search_constructor(app: "App"):
    """
    Build the main screen layout and decide which
    table to show.
    """
    filters = ["Status", "Alphabetical", "Type", "Associated with resource..."]

    print("Search Constructor")

    contact_table, contact_fields = get_contact_table(app)
    org_table, org_fields = get_organization_table(app)

    Thread(target=lazy_load_contact_values, args=(app,)).start()
    Thread(target=lazy_load_org_values, args=(app,)).start()

    if app.current_screen == Screen.CONTACT_SEARCH:
        fields = contact_fields

    elif app.current_screen == Screen.ORG_SEARCH:
        fields = org_fields

    layout = [
        [
            sg.Column(
                expand_x=True,
                element_justification="left",
                background_color=sg.theme_progress_bar_color()[1],
                pad=((0, 0), (0, 10)),
                layout=[
                    [
                        sg.Column(
                            pad=5,
                            element_justification="left",
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=get_action_bar(app.current_screen),
                        ),
                        sg.Push(background_color=sg.theme_progress_bar_color()[1]),
                        sg.Column(
                            element_justification="right",
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "View: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                        pad=((0, 0), (0, 0)),
                                    ),
                                    sg.Combo(
                                        ["Contacts", "Organizations"],
                                        k="-SEARCHTYPE-",
                                        default_value="Contacts"
                                        if app.current_screen == Screen.CONTACT_SEARCH
                                        else "Organizations",
                                        enable_events=True,
                                        pad=((0, 5), (0, 0)),
                                    ),
                                ]
                            ],
                        ),
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
                        sg.Button("Search", k="-SEARCH_BUTTON-"),
                        sg.Text("Search Query:"),
                        sg.Input(k="-SEARCH_QUERY-", expand_x=True),
                    ],
                    [
                        sg.Text("Search Fields:"),
                        sg.Combo(fields, k="-SEARCH_FIELDS-", expand_x=True),
                        sg.Text("Search Filters:"),
                        sg.Combo(filters, k="-SORT_TYPE-", expand_x=True),
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
                visible=app.current_screen == Screen.ORG_SEARCH,
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
                visible=app.current_screen == Screen.CONTACT_SEARCH,
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


def empty_viewer_head_constructor(contact: bool = False):
    print("Empty Viewer Head Constructor")

    layout = [
        [
            sg.Column(
                layout=get_action_bar(Screen.ORG_VIEW),
                background_color=sg.theme_progress_bar_color()[1],
                element_justification="left",
            ),
            sg.Push(),
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                element_justification="right",
                layout=[
                    [
                        sg.Button("Edit", k="-EDIT-" if not contact else "-CONTACT_EDIT-"),
                        sg.Button("Delete", k="-DELETE-" if not contact else "-CONTACT_DELETE-"),
                        sg.Button("Exit", k="-EXIT-" if not contact else "-CONTACT_EXIT-"),
                    ]
                ],
            ),
        ],
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Button("Exit", k="-EXIT_1-" if not contact else "-CONTACT_EXIT_1-", expand_y=True, expand_x=True),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "Name: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-NAME-" if not contact else "-CONTACT_NAME-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "Status: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-STATUS-" if not contact else "-CONTACT_STATUS-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "Primary Phone: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-PHONE-" if not contact else "-CONTACT_PHONE-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "Address: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-ADDRESS-" if not contact else "-CONTACT_ADDRESS-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                    ]
                ],
            )
        ],
        [sg.Sizer(800, 0)]
    ]

    return layout


def empty_contact_view_constructor():
    """
    Returns the layout used to view the details of an organization.
    This returns empty, as we cannot predict the organization that the
    user is going to look at. Later, the program will fill in the blanks.
    """
    print("Empty Contact View Constructor")
    layout = [
        [
            sg.Column(
                expand_x=True,
                layout=empty_viewer_head_constructor(True),
            )
        ],
        [
            sg.Column(
                expand_x=True,
                background_color=sg.theme_progress_bar_color()[1],
                layout=[
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Contact Info", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_INFO_TABLE-",
                                        headings=["Name", "Value"],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows = 5,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Organizatons", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_ORGANIZATIONS_TABLE-",
                                        headings=["Name", "Status"],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows = 5,
                                        enable_click_events=True,
                                        right_click_menu=[
                                            "&Right",
                                            ["View", "Edit", "Delete"],
                                        ],
                                        right_click_selects=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ],
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Associated Resources", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_RESOURCES_TABLE-",
                                        headings=["Name", "Status"],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows = 5,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Custom Fields", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_CUSTOM_FIELDS_TABLE-",
                                        headings=["Name", "Value"],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows = 5,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ]
                ],
            )
        ],
    ]

    return layout


def empty_org_view_constructor():
    print("Empty Org View Constructor")
    layout = [
        [
            sg.Column(
                expand_x=True,
                layout=empty_viewer_head_constructor(),
            )
        ],
        [
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                layout=[
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Organization Contacts")],
                                [
                                    sg.Table(
                                        key="-ORG_CONTACT_INFO_TABLE-",
                                        headings=["Name", "Title", "Email", "Phone"],
                                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                        row_height=40,
                                        alternating_row_color=sg.theme_progress_bar_color()[1],
                                        justification="center",
                                        num_rows=5,
                                        auto_size_columns=True,
                                        expand_x=True,
                                        enable_click_events=True,
                                        right_click_menu=[
                                            "&Right",
                                            ["View", "Edit", "Delete"],
                                        ],
                                        right_click_selects=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Associated Resources")],
                                [
                                    sg.Table(
                                        key="-ORG_RESOURCES_TABLE-",
                                        headings=["Name", "Value"],
                                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                        row_height=40,
                                        alternating_row_color=sg.theme_progress_bar_color()[1],
                                        justification="center",
                                        num_rows=5,
                                        auto_size_columns=True,
                                        expand_x=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Custom Fields")],
                                [
                                    sg.Table(
                                        key="-ORG_CUSTOM_FIELDS_TABLE-",
                                        headings=["Name", "Value"],
                                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                        row_height=40,
                                        alternating_row_color=sg.theme_progress_bar_color()[1],
                                        justification="center",
                                        num_rows=5,
                                        auto_size_columns=True,
                                        expand_x=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ]
                ],
            )
        ],
    ]

    return layout


@db_session
def swap_to_org_viewer(
    app: "App", 
    location: tuple[int, int] | None = None, 
    org_name: str | None = None
    ) -> None:
    screen = app.current_screen

    if org_name:
        app.switch_screen(Screen.ORG_VIEW, org_name, push=False)

    else:
        if screen == Screen.ORG_SEARCH:
            org_name = app.window["-ORG_TABLE-"].get()[location[0]][0]
        
        elif screen == Screen.CONTACT_VIEW:
            org_name = app.window["-CONTACT_ORGANIZATIONS_TABLE-"].get()[location[0]][0]

        app.switch_screen(Screen.ORG_VIEW, org_name)


    contact_table_values = []
    resource_table_values = []
    custom_field_table_values = []

    org = Organization.get(name=org_name)

    for contact in org.contacts:
        contact_table_values.append(
            [
                contact.name,
                contact.org_titles[str(org.id)] if contact.org_titles else "No Title",
                contact.emails[0] if contact.emails else "No Email",
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    for resource in org.resources:
        resource_table_values.append([resource.name, resource.value])

    for key, value in org.custom_fields.items():
        custom_field_table_values.append([key, value])

    app.window["-ORG_CONTACT_INFO_TABLE-"].update(values=contact_table_values)
    app.window["-ORG_RESOURCES_TABLE-"].update(values=resource_table_values)
    app.window["-ORG_CUSTOM_FIELDS_TABLE-"].update(values=custom_field_table_values)

    app.window["-NAME-"].update(org.name)
    app.window["-STATUS-"].update(org.status)
    app.window["-PHONE-"].update(format_phone(org.phones[0]) if org.phones else "No phone number")
    app.window["-ADDRESS-"].update(org.addresses[0] if org.addresses else "No address")


@db_session
def swap_to_contact_viewer(
    app: "App", 
    location: tuple[int, int] | None = None, 
    contact_name: str | None = None
    ) -> None:
    screen = app.current_screen

    if contact_name:
        app.switch_screen(Screen.CONTACT_VIEW, contact_name, push=False)
    
    else:
        if screen == Screen.CONTACT_SEARCH: 
            contact_name = app.window["-CONTACT_TABLE-"].get()[location[0]][0]
        elif screen == Screen.ORG_VIEW:
            contact_name = app.window["-ORG_CONTACT_INFO_TABLE-"].get()[location[0]][0]

        app.switch_screen(Screen.CONTACT_VIEW, contact_name)

    contact_info_table_values = []
    organization_table_values = []
    resource_table_values = []
    custom_field_table_values = []

    contact = Contact.get_by_name(name=contact_name)

    for number in contact.phone_numbers:
        contact_info_table_values.append(["Phone", format_phone(number)])
    
    for addresses in contact.addresses:
        contact_info_table_values.append(["Address", addresses])

    for email in contact.emails:
        contact_info_table_values.append(["Email", email])

    contact_info_table_values.append(["Availability", contact.availability if contact.availability else "No Recorded Availability"])

    for key, value in contact.contact_info.items():
        contact_info_table_values.append([key, value])

    for org in contact.organizations:
        organization_table_values.append([org.name, org.status])

    for resource in contact.resources:
        resource_table_values.append([resource.name, resource.value])

    for key, value in contact.custom_fields.items():
        custom_field_table_values.append([key, value])

    app.window["-CONTACT_INFO_TABLE-"].update(values=contact_info_table_values)
    app.window["-CONTACT_ORGANIZATIONS_TABLE-"].update(values=organization_table_values)
    app.window["-CONTACT_RESOURCES_TABLE-"].update(values=resource_table_values)
    app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].update(values=custom_field_table_values)

    app.window["-CONTACT_NAME-"].update(contact.name)
    app.window["-CONTACT_STATUS-"].update(contact.status)
    app.window["-CONTACT_PHONE-"].update(format_phone(contact.phone_numbers[0]) if contact.phone_numbers else "No phone number")
    app.window["-CONTACT_ADDRESS-"].update(contact.addresses[0] if contact.addresses else "No address")
