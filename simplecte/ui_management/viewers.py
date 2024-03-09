from typing import TYPE_CHECKING

from pony.orm import db_session

from database.database import Organization, Contact, Resource
from utils.enums import Screen
from utils.helpers import format_phone

if TYPE_CHECKING:
    from process.app import App

__all__ = (
    "swap_to_org_viewer",
    "swap_to_contact_viewer",
    "swap_to_resource_viewer",
)


def sanitize(string: str | int, max_length: int = 10) -> str:
    """
    Sanitize the string by removing newlines and truncating it if it is too long.
    """
    string = str(string)

    if "\n" in string:
        string = string.split("\n")[0]

    if len(string) > max_length:
        string = string[:max_length] + "..."

    return string


def get_custom_field_info(custom_fields: dict) -> list:
    """
    Compile the information of each custom field into a table, sanitizing the values.
    """
    return_values = []

    for key, value in custom_fields.items():
        return_values.append([sanitize(key, 20), sanitize(value, 15)])

    return return_values


@db_session
def swap_to_org_viewer(
    app: "App",
    org_id: int | None = None,
    org: Organization | None = None,
    push: bool = True,
) -> None:
    """
    Get ready to swap the UI to the organization viewer screen.
    """
    if org_id:
        org = Organization.get(id=org_id)

    if not org:
        raise ValueError("Must provide either ID or Organization.")

    contact_table_values = []
    resource_table_values = []

    # Compile the information of each org-related contact into a table
    for contact in org.contacts:
        contact_table_values.append(
            [
                contact.id,
                contact.name,
                sanitize(contact.org_titles.get(str(org.id), "No Title"), 20)
                if contact.org_titles
                else "No Title",
                contact.emails[0] if contact.emails else "No Email",
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    # Add available resources to the table of organization resources
    for resource in org.resources:
        resource_table_values.append(
            [resource.id, resource.name, sanitize(resource.value, 20)]
        )

    # Add the custom fields to the table of custom fields
    custom_field_table_values = get_custom_field_info(org.custom_fields)

    # Update all the data in the screen to the new organization
    app.window["-ORG_VIEW-"].metadata = org.id
    app.window["-ORG_CONTACT_INFO_TABLE-"].update(values=contact_table_values)
    app.window["-ORG_RESOURCES_TABLE-"].update(values=resource_table_values)
    app.window["-ORG_CUSTOM_FIELDS_TABLE-"].update(values=custom_field_table_values)

    app.window["-NAME-"].update(sanitize(org.type, 15))
    app.window["-NAME_TEXT-"].update(sanitize(org.name, 30), font=("Arial", 11))

    app.window["-STATUS-"].update(sanitize(org.status))
    app.window["-PHONE-"].update(
        sanitize(format_phone(org.phones[0]), 20) if org.phones else "No phone number"
    )
    app.window["-ADDRESS-"].update(
        sanitize(org.addresses[0], 30) if org.addresses else "No address"
    )
    app.window["-EMAIL-"].update(
        sanitize(org.emails[0], 20) if org.emails else "No email"
    )

    app.switch_screen(
        Screen.ORG_VIEW, data=org, push=push
    )  # Switch to the organization viewer screen


@db_session
def swap_to_contact_viewer(
    app: "App",
    contact_id: int | None = None,
    contact: Contact | None = None,
    push: bool = True,
) -> None:
    """
    Get ready to swap the UI to the contact viewer screen.
    """
    if contact_id:
        contact = Contact.get(id=contact_id)

    if not contact:
        raise ValueError("Must provide either ID or Contact.")

    contact_info_table_values = []
    organization_table_values = []
    resource_table_values = []

    # An ungodly amount of loops to compile all the information into tables
    for number in contact.phone_numbers:
        contact_info_table_values.append(["Phone", sanitize(format_phone(number), 20)])

    for addresses in contact.addresses:
        contact_info_table_values.append(["Address", sanitize(addresses, 20)])

    for email in contact.emails:
        contact_info_table_values.append(["Email", sanitize(email, 20)])

    contact_info_table_values.append(
        [
            "Availability",
            sanitize(contact.availability)
            if contact.availability
            else "No Recorded Availability",
        ]
    )

    for key, value in contact.contact_info.items():
        contact_info_table_values.append([key, sanitize(value, 20)])

    for org in contact.organizations:
        organization_table_values.append(
            [org.id, sanitize(org.name, 20), sanitize(org.status, 10)]
        )

    for resource in contact.resources:
        resource_table_values.append(
            [resource.id, resource.name, sanitize(resource.value, 20)]
        )

    custom_field_table_values = get_custom_field_info(contact.custom_fields)

    # Update all the data in the screen to the new contact
    app.window["-CONTACT_VIEW-"].metadata = contact.id
    app.window["-CONTACT_INFO_TABLE-"].update(values=contact_info_table_values)
    app.window["-CONTACT_ORGANIZATIONS_TABLE-"].update(values=organization_table_values)
    app.window["-CONTACT_RESOURCES_TABLE-"].update(values=resource_table_values)
    app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].update(values=custom_field_table_values)

    app.window["-CONTACT_NAME-"].update(sanitize(contact.name, 30))
    app.window["-CONTACT_STATUS-"].update(sanitize(contact.status, 12))
    app.window["-CONTACT_PHONE-"].update(
        sanitize(format_phone(contact.phone_numbers[0]), 20)
        if contact.phone_numbers
        else "No phone number"
    )
    app.window["-CONTACT_ADDRESS-"].update(
        sanitize(contact.addresses[0], 20) if contact.addresses else "No address"
    )
    app.window["-CONTACT_EMAIL-"].update(
        sanitize(contact.emails[0], 30) if contact.emails else "No email"
    )

    app.switch_screen(
        Screen.CONTACT_VIEW, data=contact, push=push
    )  # Switch to the contact viewer screen


@db_session
def swap_to_resource_viewer(
    app: "App",
    resource_id: int | None = None,
    resource: Resource | None = None,
    push: bool = True,
) -> None:
    """
    Get ready to swap the UI to the resource viewer screen.
    """
    if resource_id:
        resource = Resource.get(id=resource_id)

    if not resource:
        raise ValueError("Must provide either ID or Resource.")

    contacts_values = []  # ID, Name, Email, and phone
    organizations_values = []  # ID, Name, Status, and Primary Contact

    # Compile the information of each resource-related contact into a table
    for contact in resource.contacts:
        contacts_values.append(
            [
                contact.id,
                contact.name,
                contact.emails[0] if contact.emails else "No Email",
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    # Compile the information of each resource-related organization into a table
    for org in resource.organizations:
        if org.primary_contact:
            primary = org.primary_contact.name
        else:
            primary = "No Primary Contact"
        organizations_values.append(
            [
                org.id,
                org.name,
                org.status,
                primary,
            ]
        )

    # Deprecate the displayed values in case they are above desired length
    if len(resource.name) > 20:
        name = resource.name[:20] + "..."

    else:
        name = resource.name

    if len(resource.value) > 20:
        value = resource.value[:20] + "..."

    else:
        value = resource.value

    # Update all the data in the screen to the new resource
    app.window["-RESOURCE_VIEW-"].metadata = resource.id
    app.window["-RESOURCE_NAME-"].update(name)
    app.window["-RESOURCE_VALUE-"].update(value)

    app.window["-RESOURCE_CONTACTS_TABLE-"].update(values=contacts_values)
    app.window["-RESOURCE_ORGANIZATIONS_TABLE-"].update(values=organizations_values)

    app.switch_screen(Screen.RESOURCE_VIEW, data=resource, push=push)
