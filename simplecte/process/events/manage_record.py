from typing import TYPE_CHECKING
import PySimpleGUI as sg

from database import get_table_values
from ui_management import (
    swap_to_org_viewer,
    swap_to_contact_viewer,
    swap_to_resource_viewer,
)
from utils.enums import Screen
from database import Organization, Contact

if TYPE_CHECKING:
    from process.app import App

__all__ = ("EVENT_MAP",)


def _add_contact(app: "App"):
    """
    Add a contact to an organization.
    This should only be emitted from the ORGANIZATION view screen.
    """
    user_input = sg.popup_get_text(
        "Enter the ID of the contact you would like to add.\n\nIf you don't know the ID, you"
        'can find it by searching\nfor the contact, then alt-clicking on it and selecting "Copy ID".',
        title="Add Contact",
    )

    if not user_input:
        return

    try:
        user_input = int(user_input)
    except ValueError:
        sg.popup("Invalid ID!")
        return

    org_id = app.window["-ORG_VIEW-"].metadata

    status = app.db.add_contact_to_org(user_input, org_id)

    if not status:
        sg.popup("Error adding contact.\nPerhaps you used an incorrect ID?")
        return

    swap_to_org_viewer(app, org_id=org_id, push=False)


def _remove_contact(app: "App", values: dict):
    """
    Removes a contact from an organization.
    This should only be emitted from the ORGANIZATION view screen.
    """
    try:
        contact_name = app.window["-ORG_CONTACT_INFO_TABLE-"].get()[
            values["-ORG_CONTACT_INFO_TABLE-"][0]
        ][0]
    except IndexError:
        return

    # Get organization name
    org_id = app.window["-ORG_VIEW-"].metadata

    # Remove contact from organization
    status = app.db.remove_contact_from_org(contact_name, org_id)

    if not status:
        sg.popup("Error removing contact.")
        return

    swap_to_org_viewer(app, org_id=org_id, push=False)


def _add_org(app: "App"):
    """
    Handle adding an organization to a contact.
    This should only be emitted from the CONTACT view screen.
    """
    user_input = sg.popup_get_text(
        "Enter the ID of the organization you would like to add.\n\nIf you don't know the ID, "
        "you can find it by "
        'searching\nfor the organization, then alt-clicking on it and selecting "Copy ID".',
        title="Add Organization",
    )

    contact_id = app.window["-CONTACT_VIEW-"].metadata

    if not user_input:
        return

    try:
        user_input = int(user_input)
    except ValueError:
        sg.popup("Invalid ID!")
        return

    status = app.db.add_contact_to_org(contact_id, user_input)

    if not status:
        sg.popup("Error adding organization.\nPerhaps you used an incorrect ID?")
        return

    swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _remove_org(app: "App", values: dict):
    """
    Removes an organization from a contact.
    This should only be emitted from the CONTACT view screen
    """
    try:
        org_id = app.window["-CONTACT_ORGANIZATIONS_TABLE-"].get()[
            values["-CONTACT_ORGANIZATIONS_TABLE-"][0]
        ][0]
    except IndexError:
        sg.popup("No organization selected!")
        return

    # Get contact name
    contact_id = app.window["-CONTACT_VIEW-"].metadata

    # Remove contact from organization
    status = app.db.remove_contact_from_org(contact_id, org_id)

    if not status:
        sg.popup("Error removing organization.")
        return

    swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _create_resource(app: "App"):
    """
    Create a new resource.
    """
    input_window = sg.Window(
        "Create Resource",
        [
            [sg.Text("Resource Name:"), sg.Input(key="-RESOURCE_NAME-")],
            [sg.Text("Resource Value:"), sg.Input(key="-RESOURCE_VALUE-")],
            [sg.Button("Create"), sg.Button("Cancel")],
        ],
        finalize=True,
        modal=True,
    )

    event, values = input_window.read()

    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    if not values["-RESOURCE_NAME-"] or not values["-RESOURCE_VALUE-"]:
        sg.popup("Resource name and value are required!")
        return

    resource = app.db.create_resource(
        name=values["-RESOURCE_NAME-"], value=values["-RESOURCE_VALUE-"]
    )

    if app.current_screen == Screen.ORG_VIEW:
        app.db.link_resource(
            org=app.window["-ORG_VIEW-"].metadata, resource=resource.id
        )
        swap_to_org_viewer(app, org_id=app.window["-ORG_VIEW-"].metadata, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.link_resource(
            contact=app.window["-CONTACT_VIEW-"].metadata, resource=resource.id
        )
        swap_to_contact_viewer(
            app, contact_id=app.window["-CONTACT_VIEW-"].metadata, push=False
        )


def _delete_resource(app: "App", values: dict):
    if app.current_screen == Screen.ORG_VIEW:
        try:
            resource_id = app.window["-ORG_RESOURCES_TABLE-"].get()[
                values["-ORG_RESOURCES_TABLE-"][0]
            ][0]
        except IndexError:
            return

    elif app.current_screen == Screen.CONTACT_VIEW:
        try:
            resource_id = app.window["-CONTACT_RESOURCES_TABLE-"].get()[
                values["-CONTACT_RESOURCES_TABLE-"][0]
            ][0]
        except IndexError:
            return

    else:
        return

    confirmation = sg.popup_yes_no(
        "Are you sure you want to delete this resource?\nThis will remove the resource for all other "
        "records, too.",
        title="Delete Resource",
    )

    if confirmation == "No" or confirmation == sg.WIN_CLOSED:
        return

    if app.current_screen == Screen.ORG_VIEW:
        app.db.delete_resource(resource_id)

        org_id = app.window["-ORG_VIEW-"].metadata
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.delete_resource(resource_id)

        contact_id = app.window["-CONTACT_VIEW-"].metadata
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _link_resource(app: "App"):
    info_window = sg.Window(
        "Link Resource",
        [
            [sg.Text("Resource ID:"), sg.Input(key="-RESOURCE_ID-")],
            [sg.Button("Link"), sg.Button("Cancel")],
        ],
        finalize=True,
        modal=True,
    )

    event, values = info_window.read()
    info_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    try:
        resource_id = int(values["-RESOURCE_ID-"])
    except ValueError:
        sg.popup("Invalid resource ID!")
        return

    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        app.db.link_resource(org=org_id, resource=resource_id)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        app.db.link_resource(contact=contact_id, resource=resource_id)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _unlink_resource(app: "App", values: dict) -> None:
    # Get the resource ID
    if app.current_screen == Screen.ORG_VIEW:
        try:
            resource_id = app.window["-ORG_RESOURCES_TABLE-"].get()[
                values["-ORG_RESOURCES_TABLE-"][0]
            ][0]
        except IndexError:
            return

    elif app.current_screen == Screen.CONTACT_VIEW:
        try:
            resource_id = app.window["-CONTACT_RESOURCES_TABLE-"].get()[
                values["-CONTACT_RESOURCES_TABLE-"][0]
            ][0]
        except IndexError:
            return

    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata
        app.db.unlink_resource(org=org_id, resource=resource_id)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata
        app.db.unlink_resource(contact=contact_id, resource=resource_id)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


def _link_record(app: "App", values: dict, event: str) -> None:
    # Link an organization to a contact via the Contact View screen
    selected_item = event.split(" ")[-1]

    input_window = sg.Window(
        f"Link {selected_item}",
        layout=[
            [
                sg.Text(f"{selected_item} ID:"),
                sg.Input(key="-RECORD_ID-", size=(10, 20)),
            ],
            [sg.Button("Link"), sg.Button("Cancel")],
        ],
        finalize=True,
        modal=True,
    )

    event, values = input_window.read()
    input_window.close()

    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    try:
        record_id = int(values["-RECORD_ID-"])
    except ValueError:
        sg.popup(f"Invalid {selected_item} ID!")
        return

    resource_id = app.window["-RESOURCE_VIEW-"].metadata

    if selected_item.lower() == "organization":
        app.db.link_resource(org=record_id, resource=resource_id)
    elif selected_item.lower() == "contact":
        app.db.link_resource(contact=record_id, resource=resource_id)

    swap_to_resource_viewer(app, resource_id=resource_id, push=False)


def _unlink_record(app: "App", values: dict, event: str) -> None:
    """
    Unlink an organization or contact from a resource
    """

    selected_item = event.split(" ")[-1]
    resource_id = app.window["-RESOURCE_VIEW-"].metadata

    if selected_item.lower() == "organization":
        record_id = app.window["-RESOURCE_ORGANIZATIONS_TABLE-"].get()[
            values["-RESOURCE_ORGANIZATIONS_TABLE-"][0]
        ][0]
        app.db.unlink_resource(resource=resource_id, org=record_id)

    elif selected_item.lower() == "contact":
        record_id = app.window["-RESOURCE_CONTACTS_TABLE-"].get()[
            values["-RESOURCE_CONTACTS_TABLE-"][0]
        ][0]
        app.db.unlink_resource(resource=resource_id, contact=record_id)

    swap_to_resource_viewer(app, resource_id=resource_id, push=False)


def _delete_record(app: "App"):
    confirmation = sg.popup_yes_no(
        "Are you sure you want to delete this record?", title="Delete Record"
    )

    if confirmation != "Yes":
        return

    match app.current_screen:
        case Screen.ORG_VIEW:
            org_id = app.window["-ORG_VIEW-"].metadata
            app.db.delete_organization(org_id)
            app.switch_to_last_screen()

        case Screen.CONTACT_VIEW:
            contact_id = app.window["-CONTACT_VIEW-"].metadata
            app.db.delete_contact(contact_id)
            app.switch_to_last_screen()

        case Screen.RESOURCE_VIEW:
            app.db.delete_resource(app.window["-RESOURCE_VIEW-"].metadata)
            app.switch_to_last_screen()

        case Screen.ORG_SEARCH:
            app.db.delete_organization(app.last_selected_id)
            app.window["-ORG_TABLE-"].update(get_table_values(app, Organization))

        case Screen.CONTACT_SEARCH:
            app.db.delete_contact(app.last_selected_id)
            app.window["-CONTACT_TABLE-"].update(get_table_values(app, Contact))

    # Reload the table values after the record is deleted
    app.lazy_load_table_values()


def _create_custom_field(app: "App"):
    # Create a new window to get the field name and value
    input_window = sg.Window(
        "Create Custom Field",
        [
            [sg.Text("Field Name:"), sg.Input(key="-FIELD_NAME-")],
            [sg.Text("Field Value:"), sg.Input(key="-FIELD_VALUE-")],
            [sg.Button("Create"), sg.Button("Cancel")],
        ],
        finalize=True,
        modal=True,
    )

    # Read the window and close it
    event, values = input_window.read()
    input_window.close()

    # Check if the user clicked cancel
    if event == "Cancel" or event == sg.WIN_CLOSED:
        return

    # Check if the user entered a name and value
    if not values["-FIELD_NAME-"] or not values["-FIELD_VALUE-"]:
        sg.popup("Field name and value are required!")
        return

    create_kwargs = {
        "name": values["-FIELD_NAME-"],
        "value": values["-FIELD_VALUE-"],
    }

    swap_args = [{"app": app, "push": False}]

    if app.current_screen == Screen.ORG_VIEW:
        create_kwargs["org"] = swap_args[0]["org_id"] = app.window[
            "-ORG_VIEW-"
        ].metadata
        swap_args.append(swap_to_org_viewer)

    elif app.current_screen == Screen.CONTACT_VIEW:
        create_kwargs["contact"] = swap_args[0]["contact_id"] = app.window[
            "-CONTACT_VIEW-"
        ].metadata

        swap_args.append(swap_to_contact_viewer)

    else:
        return

    # Get the ID of the record we're viewing

    field = app.db.create_custom_field(**create_kwargs)

    if not field:
        sg.popup(
            "Error creating custom field.\nPerhaps you used the same name as an existing field?"
        )
        return

    (swap_args[1])(**(swap_args[0]))


def _delete_custom_field(app: "App", values: dict):
    # Get the ID of the record we're viewing
    if app.current_screen == Screen.ORG_VIEW:
        org_id = app.window["-ORG_VIEW-"].metadata

        try:
            field_name = app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[
                values["-ORG_CUSTOM_FIELDS_TABLE-"][0]
            ][0]
        except IndexError:
            return

    elif app.current_screen == Screen.CONTACT_VIEW:
        contact_id = app.window["-CONTACT_VIEW-"].metadata

        try:
            field_name = app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[
                values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]
            ][0]
        except IndexError:
            return

    confirmation = sg.popup_yes_no(
        "Are you sure you want to delete this field?", title="Delete Field"
    )

    if confirmation == "No" or confirmation == sg.WIN_CLOSED:
        return

    # Delete the field
    if app.current_screen == Screen.ORG_VIEW:
        app.db.delete_custom_field(org=org_id, name=field_name)
        swap_to_org_viewer(app, org_id=org_id, push=False)

    elif app.current_screen == Screen.CONTACT_VIEW:
        app.db.delete_custom_field(contact=contact_id, name=field_name)
        swap_to_contact_viewer(app, contact_id=contact_id, push=False)


EVENT_MAP = {
    "Add Contact": _add_contact,
    "Remove Contact": _remove_contact,
    "Add Organization": _add_org,
    "Remove Organization": _remove_org,
    "Create Resource": _create_resource,
    "Delete Resource": _delete_resource,
    "Link Resource": _link_resource,
    "Unlink Resource": _unlink_resource,
    "Link Organization": _link_record,
    "Link Contact": _link_record,
    "Unlink Contact": _unlink_record,
    "Unlink Organization": _unlink_record,
    "Delete Record": _delete_record,
    "Create Custom Field": _create_custom_field,
    "Delete Custom Field": _delete_custom_field,
}
