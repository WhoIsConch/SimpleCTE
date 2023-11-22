from typing import List, Any, Tuple

import PySimpleGUI as sg
import typing

from PySimpleGUI import Table

from enums import Screen, AppStatus
from pony.orm import db_session
from threading import Thread
from database import Contact, Organization, Resource

import time

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
        return str(phone_number)


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
def get_contact_table(app: "App", values_only: bool = False, search_info: dict[str, str, str] | None = None,
                      lazy=False, table_values: list | None = None) -> sg.Table | tuple[sg.Table, list[str]]:
    """
    Build the table that includes information of contacts.
    """
    if table_values is None:
        table_values = []

    fields = [
        "Name",
        "Status",
        "Primary Phone",
        "Address",
        "Custom Field Name",
        "Custom Field Value",
    ]
    table_headings = ["ID", "Name", "Primary Organization", "Primary Phone"]

    if search_info:
        contact_pages = app.db.get_contacts(**search_info, paginated=(not lazy))
    else:
        contact_pages = app.db.get_contacts(paginated=(not lazy))

    if not contact_pages:
        contact_pages = app.db.get_contacts()


    for contact in contact_pages:
        org = None
        for org in contact.organizations:
            if org.primary_contact == contact:
                break

        if org:
            org_name = org.name
        else:
            org_name = "No Organization"

        table_values.append(
            [
                contact.id,
                contact.name,
                org_name,
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    if values_only or (values_only and lazy):
        return table_values

    return sg.Table(
        headings=table_headings,
        values=table_values,
        visible_column_map=[False, True, True, True],
        expand_x=True,
        font=("Arial", 15),
        right_click_menu=[
            "&Right",
            ["View", "Copy ID", "Delete"],
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
def get_organization_table(app: "App", values_only: bool = False, search_info: dict[str, str, str] | None = None,
                           lazy=False, table_values: list | None = None) -> None | list[list[str | Any]] | tuple[Table, list[str]]:
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
    table_headings = ["ID", "Organization Name", "Type", "Primary Contact", "Status"]

    if table_values is None:
        table_values = []

    if search_info:
        org_pages = app.db.get_organizations(**search_info, paginated=(not lazy))
    else:
        org_pages = app.db.get_organizations(paginated=(not lazy))

    for org in org_pages:
        contact = org.primary_contact
        contact_name = contact.name if contact else "No Primary Contact"
        table_values.append([org.id, org.name, org.type, contact_name, org.status])

    if lazy and values_only:
        while app.status == AppStatus.READY:
            app.window["-ORG_TABLE-"].update(values=table_values)
            app.window.refresh()
            break
        return

    elif values_only:
        return table_values

    return sg.Table(
        headings=table_headings,
        values=table_values,
        visible_column_map=[False, True, True, True, True],
        expand_x=True,
        font=("Arial", 15),
        right_click_menu=[
            "&Right",
            ["View", "Copy ID", "Delete"],
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


def search_constructor(app: "App"):
    """
    Build the main screen layout and decide which
    table to show.
    """
    filters = ["Status", "Alphabetical", "Type", "Associated with resource..."]

    print("Search Constructor")

    contact_table, contact_fields = get_contact_table(app)
    org_table, org_fields = get_organization_table(app)

    Thread(target=get_contact_table, args=(app,), kwargs={"values_only": True, "lazy": True}).start()
    Thread(target=get_organization_table, args=(app,), kwargs={"values_only": True, "lazy": True}).start()

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
                        sg.Button("Exit", k="-EXIT_1-" if not contact else "-CONTACT_EXIT_1-", expand_y=True,
                                  expand_x=True),
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
                                        num_rows=5,
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
                                [sg.Text("Organizations", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_ORGANIZATIONS_TABLE-",
                                        headings=["ID", "Name", "Status"],
                                        visible_column_map=[False, True, True],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        enable_click_events=True,
                                        right_click_menu=[
                                            "&Right",
                                            ["View", "Copy ID", "Add Organization", "Remove Organization"],
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
                                        num_rows=5,
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
                                        num_rows=5,
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
                                        headings=["ID", "Name", "Title", "Email", "Phone"],
                                        visible_column_map=[False, True, True, True, True],
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
                                            ["View", "Copy ID", "Change Title", "Add Contact", "Remove Contact"],
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
                                        headings=["ID", "Name", "Value"],
                                        visible_column_map=[False, True, True],
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
                                        headings=["ID", "Name", "Value"],
                                        visible_column_map=[False, True, True],
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
        org_id: int | None = None,
        org: Organization | None = None,
        push: bool = True,
) -> None:
    if org_id:
        org = Organization.get(id=org_id)

    if not org:
        raise ValueError("Must provide either ID or Organization.")

    app.switch_screen(Screen.ORG_VIEW, data=org.id, push=push)

    contact_table_values = []
    resource_table_values = []
    custom_field_table_values = []

    for contact in org.contacts:
        contact_table_values.append(
            [
                contact.id,
                contact.name,
                contact.org_titles.get(str(org.id), "No Title") if contact.org_titles else "No Title",
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

    app.window["-ORG_VIEW-"].metadata = org.id
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
        contact_id: int | None = None,
        contact: Contact | None = None,
        push: bool = True,
) -> None:
    if contact_id:
        contact = Contact.get(id=contact_id)

    if not contact:
        raise ValueError("Must provide either ID or Contact.")

    app.switch_screen(Screen.CONTACT_VIEW, data=contact.id, push=push)

    contact_info_table_values = []
    organization_table_values = []
    resource_table_values = []
    custom_field_table_values = []

    for number in contact.phone_numbers:
        contact_info_table_values.append(["Phone", format_phone(number)])

    for addresses in contact.addresses:
        contact_info_table_values.append(["Address", addresses])

    for email in contact.emails:
        contact_info_table_values.append(["Email", email])

    contact_info_table_values.append(
        ["Availability", contact.availability if contact.availability else "No Recorded Availability"])

    for key, value in contact.contact_info.items():
        contact_info_table_values.append([key, value])

    for org in contact.organizations:
        organization_table_values.append([org.id, org.name, org.status])

    for resource in contact.resources:
        resource_table_values.append([resource.name, resource.value])

    for key, value in contact.custom_fields.items():
        custom_field_table_values.append([key, value])

    app.window["-CONTACT_VIEW-"].metadata = contact.id
    app.window["-CONTACT_INFO_TABLE-"].update(values=contact_info_table_values)
    app.window["-CONTACT_ORGANIZATIONS_TABLE-"].update(values=organization_table_values)
    app.window["-CONTACT_RESOURCES_TABLE-"].update(values=resource_table_values)
    app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].update(values=custom_field_table_values)

    app.window["-CONTACT_NAME-"].update(contact.name)
    app.window["-CONTACT_STATUS-"].update(contact.status)
    app.window["-CONTACT_PHONE-"].update(
        format_phone(contact.phone_numbers[0]) if contact.phone_numbers else "No phone number")
    app.window["-CONTACT_ADDRESS-"].update(contact.addresses[0] if contact.addresses else "No address")


def create_contact():
    layout = [
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Text("First Name: "),
                        sg.Input(k="-FIRST_NAME-", tooltip="The contact's first name."),
                    ],
                    [
                        sg.Text("Last Name: "),
                        sg.Input(k="-LAST_NAME-", tooltip="The contact's last name."),
                    ],
                    [
                        sg.Text("Status: "),
                        sg.Input(k="-STATUS-", tooltip="The contact's status, e.g. 'Active' or 'Former'"),
                    ],
                    [
                        sg.Text("Primary Phone: "),
                        sg.Input(k="-PHONE_NUMBER-",
                                 tooltip="The contact's primary phone number. You can add more later."),
                    ],
                    [
                        sg.Text("Address: "),
                        sg.Input(k="-ADDRESS-", tooltip="The contact's primary address. You can add more later."),
                    ],
                    [
                        sg.Text("Availability: "),
                        sg.Input(k="-AVAILABILITY-", tooltip="The contact's availability, e.g. weekends or 9am-5pm"),
                    ],
                ],
            )
        ],
        [
            sg.Button("Add Contact", k="-CONFIRM_ADD_CONTACT-"),
            sg.Button("Cancel", k="-CANCEL-"),
        ]
    ]

    return layout


def create_organization():
    layout = [
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Text("Name: "),
                        sg.Input(k="-NAME-", tooltip="The organization's name."),
                    ],
                    [
                        sg.Text("Type: "),
                        sg.Input(k="-TYPE-", tooltip="The organization's type, e.g. 'Food Bank' or 'Shelter'."),
                    ],
                    [
                        sg.Text("Status: "),
                        sg.Input(k="-STATUS-", tooltip="The organization's status, e.g. 'Active' or 'Former'"),
                    ],
                    [
                        sg.Text("Primary Phone: "),
                        sg.Input(k="-PHONE_NUMBER-", tooltip="The organization's primary phone number. You can add "
                                                             "more later."),
                    ],
                    [
                        sg.Text("Address: "),
                        sg.Input(k="-ADDRESS-", tooltip="The organization's primary address. You can add more later."),
                    ],
                ],
            )
        ],
        [
            sg.Button("Add Organization", k="-CONFIRM_ADD_ORGANIZATION-"),
            sg.Button("Cancel", k="-CANCEL-"),
        ]
    ]

    return layout
