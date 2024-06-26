from typing import TYPE_CHECKING
import PySimpleGUI as sg
from ui_management import (
    swap_to_org_viewer,
    swap_to_contact_viewer,
    swap_to_resource_viewer,
)
from utils.enums import Screen
from utils.helpers import format_phone, strip_phone

if TYPE_CHECKING:
    from process.app import App

__all__ = ("EVENT_MAP",)


def _change_title(app: "App", values: dict):
    """
    Triggered when a user tries to change the title of a user
    in an organization. This is only available in the organization
    view.
    """

    # Get the organization ID
    org_id = app.window["-ORG_VIEW-"].metadata

    # Get the contact ID
    try:
        contact_id = app.window["-ORG_CONTACT_INFO_TABLE-"].get()[
            values["-ORG_CONTACT_INFO_TABLE-"][0]
        ][0]
    except IndexError:
        return

    title = sg.popup_get_text(
        "Enter the new title for this contact.", title="Change Title"
    )

    if not title:
        return

    status = app.db.change_contact_title(org_id, contact_id, title)

    if not status:
        sg.popup("Error changing title.")
        return

    swap_to_org_viewer(app, org_id=org_id, push=False)


def _change_name(app: "App"):
    """
    Change the name of a record.
    """

    # Get the ID of the record we're viewing
    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata

        try:
            org = app.db.get_organization(org_id)
        except IndexError:
            return

        layout = [
            [sg.Text("New Name:"), sg.Input(key="-NAME-", default_text=org.name)],
            [sg.Button("Change"), sg.Button("Cancel")],
        ]

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        contact = app.db.get_contact(contact_id)

        layout = [
            [
                sg.Text("New First Name:"),
                sg.Input(key="-FIRST_NAME-", default_text=contact.first_name),
            ],
            [
                sg.Text("New Last Name:"),
                sg.Input(key="-LAST_NAME-", default_text=contact.last_name),
            ],
            [sg.Button("Change"), sg.Button("Cancel")],
        ]

    elif app.current_screen == Screen.RESOURCE_VIEW:
        resource_id = app.window["-RESOURCE_VIEW-"].metadata
        resource = app.db.get_resource(resource_id)

        layout = [
            [sg.Text("New Name:"), sg.Input(key="-NAME-", default_text=resource.name)],
            [sg.Button("Change"), sg.Button("Cancel")],
        ]

    else:
        return

    input_window = sg.Window("Change Name", layout, finalize=True, modal=True)

    event, values = input_window.read()
    input_window.close()

    new_org_name = values.get("-NAME-", "")
    new_first_name = values.get("-FIRST_NAME-", "")
    new_last_name = values.get("-LAST_NAME-", "")

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    if not (new_org_name or new_first_name or new_last_name):
        sg.popup("A name is required!")
        return

    if len(new_org_name) > 50 or len(new_first_name) > 50 or len(new_last_name) > 50:
        confirmation = sg.popup_yes_no(
            "Making a name too long may cause issues with the UI. Are you sure you want to continue?"
        )

        if confirmation == "No" or confirmation == sg.WIN_CLOSED:
            return

    if app.current_screen == Screen.ORG_VIEW:
        app.db.update_organization(org_id, name=new_org_name)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.update_contact(
            contact_id, first_name=new_first_name, last_name=new_last_name
        )
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)

    elif app.current_screen == Screen.RESOURCE_VIEW:
        app.db.update_resource(resource_id, name=new_org_name)
        swap_to_resource_viewer(app, resource_id=resource_id, push=False)

    app.lazy_load_table_values()


def _change_type(app: "App"):
    """
    Change the type of an Organization
    """
    if not app.current_screen == Screen.ORG_VIEW:
        return  # Only organizations can have this info

    org = app.db.get_organization(app.window["-ORG_VIEW-"].metadata)

    input_win = sg.Window(
        "Change Type",
        [
            [sg.Text("New Type:"), sg.Input(key="-TYPE-", default_text=org.type)],
            [sg.Button("Change"), sg.Button("Cancel")],
        ],
        finalize=True,
        modal=True,
    )

    event, values = input_win.read()
    input_win.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    new_type = values.get("-TYPE-", "")

    if not new_type:
        sg.popup("A type is required!")
        return

    if new_type == org.type:
        return

    app.db.update_organization(org.id, type=new_type)
    swap_to_org_viewer(app, org_id=org.id, push=False)


def _change_status(app: "App"):
    """
    Change the status of a record.
    """

    # Get the ID of the record we're viewing
    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        org = app.db.get_organization(org_id)

        layout = [
            [sg.Text("New Status:"), sg.Input(key="-STATUS-", default_text=org.status)],
            [sg.Button("Change"), sg.Button("Cancel")],
        ]

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        contact = app.db.get_contact(contact_id)

        layout = [
            [
                sg.Text("New Status:"),
                sg.Input(key="-STATUS-", default_text=contact.status),
            ],
            [sg.Button("Change"), sg.Button("Cancel")],
        ]

    else:
        return

    input_window = sg.Window("Change Status", layout, finalize=True, modal=True)

    event, values = input_window.read()
    input_window.close()

    new_org_status = values.get("-STATUS-", "")
    new_contact_status = values.get("-STATUS-", "")

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    if not (new_org_status or new_contact_status):
        sg.popup("A status is required!")
        return

    if len(new_org_status) > 50 or len(new_contact_status) > 50:
        confirmation = sg.popup_yes_no(
            "Making a status too long may cause issues with the UI. Are you sure you want to continue?"
        )

        if confirmation == "No" or confirmation == sg.WIN_CLOSED:
            return

    if app.current_screen == Screen.ORG_VIEW:
        app.db.update_organization(org_id, status=new_org_status)
        swap_to_org_viewer(app, org_id=org_id, push=False)
        app.lazy_load_table_values()

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.update_contact(contact_id, status=new_contact_status)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _edit_availability(app: "App"):
    """
    Change the availability of the record
    """

    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        record = app.db.get_organization(org_id)

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        record = app.db.get_contact(contact_id)

    else:
        return

    layout = [
        [sg.Text("Availability:")],
        [sg.Multiline(record.availability, size=(30, 10), key="-AVAILABILITY-")],
        [sg.Button("Save"), sg.Button("Cancel")],
    ]

    input_window = sg.Window("Edit Availability", layout, finalize=True, modal=True)

    event, values = input_window.read()
    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    new_availability = values["-AVAILABILITY-"]

    if app.current_screen == Screen.ORG_VIEW:
        app.db.update_organization(org_id, availability=new_availability)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.update_contact(contact_id, availability=new_availability)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _edit_contact_info(app: "App", values: dict):
    """
    Manage the contact info of a contact. Not available for other records.
    """
    if app.current_screen != Screen.CONTACT_VIEW:
        return

    try:
        record_id = app.window[app.current_screen.value].metadata
        field_name = app.window["-CONTACT_INFO_TABLE-"].get()[
            values["-CONTACT_INFO_TABLE-"][0]
        ][0]
    except IndexError:
        return

    contact = app.db.get_contact(record_id)

    layout = [
        [sg.Text("Contact Info Name: "), sg.Text(field_name)],
        [
            sg.Multiline(
                contact.contact_info[field_name],
                expand_x=True,
                size=(30, 10),
                key="-CONTACT_INFO_VALUE-",
            )
        ],
        [sg.Button("Edit", key="-EDIT-"), sg.Button("Close", key="-CLOSE-")],
    ]

    window = sg.Window("Contact Info Content", finalize=True, modal=True, layout=layout)

    event, values = window.read()
    window.close()

    if event != "-EDIT-":
        return

    app.db.update_contact_info(
        name=field_name, value=values["-CONTACT_INFO_VALUE-"], contact=record_id
    )

    swap_to_contact_viewer(app, contact_id=record_id, push=False)


def _decide_contact_info_edit(app: "App", values: dict):
    try:
        index = values["-CONTACT_INFO_TABLE-"][0]
        title = app.window["-CONTACT_INFO_TABLE-"].get()[index][0]
    except IndexError:
        return

    if title == "Email":
        event = "Edit Emails"
    elif title == "Phone":
        event = "Edit Phones"
    elif title == "Address":
        event = "Edit Addresses"
    elif title == "Availability":
        event = "Edit Availability"
    else:
        _edit_contact_info(app, values)
        return

    # Trigger the event
    app.window.write_event_value(event, None)


def _edit_emails(app: "App"):
    # Get the ID of the record we're viewing
    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        record = app.db.get_organization(org_id)

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        record = app.db.get_contact(contact_id)

    else:
        return

    layout = [
        [sg.Text("Emails, one per line\n(The first email is primary):")],
        [
            sg.Multiline(
                "\n".join(list(record.emails or [])), size=(30, 10), key="-EMAILS-"
            )
        ],
        [sg.Button("Save"), sg.Button("Cancel")],
    ]

    input_window = sg.Window("Edit Emails", layout, finalize=True, modal=True)

    event, values = input_window.read()
    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    new_emails = values["-EMAILS-"].split("\n")

    if app.current_screen == Screen.ORG_VIEW:
        app.db.update_organization(org_id, emails=new_emails)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.update_contact(contact_id, emails=new_emails)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _edit_addresses(app: "App"):
    # Get the ID of the record we're viewing
    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        record = app.db.get_organization(org_id)

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        record = app.db.get_contact(contact_id)

    layout = [
        [sg.Text("Addresses, one per line\n(The first address is primary):")],
        [
            sg.Multiline(
                "\n".join(list(record.addresses)),
                size=(30, 10),
                key="-ADDRESSES-",
                horizontal_scroll=True,
            )
        ],
        [sg.Button("Save"), sg.Button("Cancel")],
    ]

    input_window = sg.Window("Edit Addresses", layout, finalize=True, modal=True)

    event, values = input_window.read()
    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    new_addresses = values["-ADDRESSES-"].split("\n")

    if app.current_screen == Screen.ORG_VIEW:
        app.db.update_organization(org_id, addresses=new_addresses)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.update_contact(contact_id, addresses=new_addresses)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _edit_phones(app: "App"):
    # Get the ID of the record we're viewing
    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        record = app.db.get_organization(org_id)

        phones = [format_phone(phone, False) for phone in record.phones]

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata

        record = app.db.get_contact(contact_id)
        phones = [format_phone(phone, False) for phone in record.phone_numbers]

    else:
        return

    layout = [
        [sg.Text("Phone Numbers, one per line\n(The first number is primary):")],
        [
            sg.Multiline(
                "\n".join(list(phones)),
                size=(30, 10),
                key="-PHONES-",
                horizontal_scroll=True,
            )
        ],
        [sg.Button("Save"), sg.Button("Cancel")],
    ]

    input_window = sg.Window("Edit Phones", layout, finalize=True, modal=True)

    # Window Loop
    while True:
        event, values = input_window.read()

        if event == "Cancel" or event == sg.WIN_CLOSED:
            input_window.close()
            return

        try:
            # Make sure each phone number is valid
            new_phones = [
                int(strip_phone(phone)) for phone in values["-PHONES-"].split("\n")
            ]
        except ValueError:
            sg.popup(
                "Invalid phone number! Phone number must be a continuous string of numbers, or a string "
                "of numbers separated by dashes or parentheses."
            )
            continue

        if app.current_screen == Screen.ORG_VIEW:
            app.db.update_organization(org_id, phones=new_phones)
            swap_to_org_viewer(app, org_id=org_id, push=False)

        elif app.current_screen == Screen.CONTACT_VIEW:
            app.db.update_contact(contact_id, phone_numbers=new_phones)
            swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        input_window.close()


def add_contact_info(app: "App"):
    # Show a basic prompt for the user to enter the contact info

    input_window = sg.Window(
        "Add Contact Info",
        [
            [
                sg.Text(
                    "Add new contact info. If you want to add an address, email, or phone,\nconsider "
                    'alt-clicking an entry in the table and selecting "Edit."'
                )
            ],
            [sg.Text("Contact Info Type:"), sg.Input(key="-CONTACT_INFO_TYPE-")],
            [sg.Text("Contact Info Value:"), sg.Input(key="-CONTACT_INFO_VALUE-")],
            [sg.Button("Add"), sg.Button("Cancel")],
        ],
        finalize=True,
        modal=True,
    )

    event, values = input_window.read()
    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    if not values["-CONTACT_INFO_TYPE-"] or not values["-CONTACT_INFO_VALUE-"]:
        sg.popup("Contact info type and value are required!")
        return

    if (
        len(values["-CONTACT_INFO_TYPE-"]) > 50
        or len(values["-CONTACT_INFO_VALUE-"]) > 50
    ):
        confirmation = sg.popup_yes_no(
            "Making a contact info type or value too long may cause issues with the UI. Are you sure you "
            "want to continue?"
        )

        if confirmation == "No" or confirmation == sg.WIN_CLOSED:
            return

    # Check if any other contact info has the same title
    for title in app.window["-CONTACT_INFO_TABLE-"].get():
        if title[0] == values["-CONTACT_INFO_TYPE-"]:
            sg.popup("A contact info type with that name already exists!")
            continue

    # Get the contact ID
    contact_id = app.window["-CONTACT_VIEW-"].metadata

    # Add the contact info
    app.db.create_contact_info(
        values["-CONTACT_INFO_TYPE-"],
        values["-CONTACT_INFO_VALUE-"],
        contact=contact_id,
    )

    # Reload the table values
    swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def delete_contact_info(app: "App", values: dict):
    # Get the contact info ID
    try:
        contact_info_name = app.window["-CONTACT_INFO_TABLE-"].get()[
            values["-CONTACT_INFO_TABLE-"][0]
        ][0]
        contact_info_value = app.window["-CONTACT_INFO_TABLE-"].get()[
            values["-CONTACT_INFO_TABLE-"][0]
        ][1]
    except IndexError:
        return

    # Get the contact ID
    contact_id = app.window["-CONTACT_VIEW-"].metadata

    # Delete the contact info
    if contact_info_name.lower() == "phone":
        contact_info_value = int(strip_phone(contact_info_value))

    app.db.delete_contact_info(
        contact_info_name, contact_info_value, contact=contact_id
    )

    # Reload the table values
    swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _manage_custom_field(app: "App", values: dict) -> None:
    try:
        record_id = app.window[app.current_screen.value].metadata
    except IndexError:
        return

    method = [{"app": app, "push": False}]

    if app.current_screen == Screen.ORG_VIEW:
        record = app.db.get_organization(record_id)
        record_type = "org"
        method.insert(0, swap_to_org_viewer)
        method[1]["org_id"] = record.id

        try:
            field_name = app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[
                values["-ORG_CUSTOM_FIELDS_TABLE-"][0]
            ][0]

        except IndexError:
            return

    elif app.current_screen == Screen.CONTACT_VIEW:
        record = app.db.get_contact(record_id)
        record_type = "contact"
        method.insert(0, swap_to_contact_viewer)
        method[1]["contact_id"] = record.id

        try:
            field_name = app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[
                values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]
            ][0]
        except IndexError:
            return

    else:
        return

    name_tooltip = "The names of custom fields cannot be changed. Consider creating a new custom field instead."

    layout = [
        [
            sg.Text("Custom Field Name: ", tooltip=name_tooltip),
            sg.Text(field_name, tooltip=name_tooltip),
        ],
        [
            sg.Multiline(
                record.custom_fields[field_name],
                expand_x=True,
                size=(30, 10),
                key="-CUSTOM_FIELD_VALUE-",
            )
        ],
        [sg.Button("Edit", key="-EDIT-"), sg.Button("Close", key="-CLOSE-")],
    ]

    window = sg.Window("Custom Field Content", finalize=True, modal=True, layout=layout)

    event, values = window.read()
    window.close()

    if event == sg.WIN_CLOSED or event == "-CLOSE-":
        return

    elif event != "-EDIT-":
        return

    app.db.update_custom_field(
        name=field_name,
        value=values["-CUSTOM_FIELD_VALUE-"],
        **{record_type: record_id},
    )

    app.db.update_custom_field(
        name=field_name,
        value=values["-CUSTOM_FIELD_VALUE-"],
        **{record_type: record_id},
    )

    method[0](**method[1])


def _change_value(app: "App"):
    # Change the value of a resource
    resource_id = app.window["-RESOURCE_VIEW-"].metadata
    resource = app.db.get_resource(resource_id)

    layout = [
        [sg.Text("Full Resource Value:")],
        [sg.Multiline(resource.value, size=(30, 10), key="-NEW_VALUE-")],
        [sg.Button("Close")],
    ]

    input_window = sg.Window("Change Value", layout, finalize=True, modal=True)

    event, values = input_window.read()
    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    new_value = values["-NEW_VALUE-"]

    if new_value == resource.value:
        return

    app.db.update_resource(resource_id, value=new_value)
    swap_to_resource_viewer(app, resource_id=resource_id, push=False)


def _update_tables(app: "App", values: dict):
    app.window["-CONTACT_TABLE-"].update(values["-UPDATE_TABLES-"][0])
    app.window["-ORG_TABLE-"].update(values["-UPDATE_TABLES-"][1])


EVENT_MAP = {
    "Change Title": _change_title,
    "Change Name": _change_name,
    "Change Type": _change_type,
    "Change Status": _change_status,
    "Edit Availability": _edit_availability,
    "Edit::CONTACT_INFO": _decide_contact_info_edit,
    "View More::CONTACT_INFO": _decide_contact_info_edit,
    "Edit Emails": _edit_emails,
    "View All Emails": _edit_emails,
    "Edit Addresses": _edit_addresses,
    "View All Addresses": _edit_addresses,
    "Edit Phones": _edit_phones,
    "View All Phones": _edit_phones,
    "Add::CONTACT_INFO": add_contact_info,
    "Delete::CONTACT_INFO": delete_contact_info,
    "Edit Custom Field": _manage_custom_field,
    "View Full Content": _manage_custom_field,
    "Change Value": _change_value,
    "Update Tables": _update_tables,
}
