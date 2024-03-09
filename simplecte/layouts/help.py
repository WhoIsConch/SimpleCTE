import PySimpleGUI as sg

__all__ = (
    "get_help_text",
    "get_help_layout",
)

ACTION_BAR = """
The action bar is the bar at the top of the screen that contains various buttons. The buttons that may be present include:

- Logout: Logs you out of the database.
- Export: Exports the single selected record.
- Export by Filter: Displays the Export screen with the current filter applied.
- Export All: Exports all records in the database.
- Settings: Opens the settings menu.
- Backup: Backs up the database.
- Add Record: Creates a new record.
- Help: Opens the help menu.

The buttons that are present depend on the screen you are on. When in a Search screen, all buttons, including two Export buttons, are present. When in a View screen, the Export by Filter button is not present. When in the Resource View screen, the Add Record button is not present.

When in the Resource View screen, the Add Record button is not present. This is because the Resource View screen, unlike View screens, is not where much of the magic happens with Resources. Resources must be bound to a Contact or Organization, and are deleted otherwise. Resources also cannot be linked to other Resources, so creating an empty resource will not be useful. Instead, Resources are created when adding a Resource to a Contact or Organization.
"""

SEARCH_BAR = """
The Search bar is a bar near the top of the screen that contains various fields. These fields are used to filter the data in the database. The items present in the Search bar include:

- Search: Searches for records that contain the given text in any field.
- Search Query: The text to search in a field for.
- Search in: The field to search for the Search Query in.
- Sort by: The field to sort the results by. Can be sorted in ascending or descending order.
"""

SEARCH_SCREEN = """
The Search Screen is the main screen of SimpleCTE. Using the Search Screen allows a user to search for and view records in the database. The Search Screen is composed of the following parts:

- Action Bar: The bar at the top of the screen that contains various buttons.
- Search Bar: The bar near the top of the screen that contains various fields.
- Search Results: The results of the search, displayed in a table. By default, all records are displayed.

For example, say you want to search for all Contacts that have the name "John". You would type "John" into the Search Query field, select "Name" in the Search in field, and click the Search button. The results would then be displayed in the Search Results table. You can then click on a record to view it in the View screen.
"""

viewer_header = """
The Viewer Header is a section at the top of a View screen that contains the Action Bar, along with various other fields
about an object. The fields present in the Viewer Header include:

- Name: The name of the object.
- Status: The status of the object.
- Type: The type of the object [ Organizations Only ].
- Primary Phone: The primary phone number of the object. Alt-clicking this field will display options to view or edit all known phone numbers for the object.
- Primary Email: The primary email address of the object. Alt-clicking this field will display options to view or edit all known email addresses for the object.
- Address: The primary address of the object. Alt-clicking this field will display options to view or edit all known addresses for the object.
- Exit: A button to exit the View screen, back to the last screen you were on.

The fields present in the Viewer Header depend on the type of object you are viewing. For example, the while viewing an Organization, the Name field loses its label, Name, and is replaced by the Organization's name. Underneath the organization's name is the Type field, which is not present when viewing a Contact. The Primary Phone, Primary Email, and Address fields are present for both Contacts and Organizations, but are not present for Resources, which only have a Name and Value field.
"""

ORG_VIEWER = """
The Organization Viewer is a screen that displays information about an Organization. The Organization Viewer is composed of the following parts:

- Viewer Header: The header at the top of the screen that contains various fields about the Organization.
- Organization Contacts: A table that displays all Contacts that are linked to the Organization.
- Associated Resources: A table that displays all Resources that are linked to the Organization.
- Custom Fields: A table that displays all custom fields that are linked to the Organization.

Double-clicking or alt-clicking on any entry of a table will open the View screen for that entry. For example, double-clicking on a Contact in the Organization Contacts table will open the Contact Viewer for that Contact. Custom Fields do not follow this rule, however you can still view and edit the field by alt-clicking.
"""

CONTACT_VIEWER = """
The Contact Viewer is a screen that displays information about a Contact. The Contact Viewer is composed of the following parts:

- Viewer Header: The header at the top of the screen that contains various fields about the Contact.
- Contact Info: A table that displays information related to how to get in touch with the contact.
- Organizations: A table that displays all Organizations that are linked to the Contact.
- Associated Resources: A table that displays all Resources that are linked to the Contact.
- Custom Fields: A table that displays all custom fields that are linked to the Contact.

Double-clicking or alt-clicking on any entry of a table will open the View screen for that entry. For example, double-clicking on an Organization in the Organizations table will open the Organization Viewer for that Organization. Custom Fields do not follow this rule, however you can still view and edit the field by alt-clicking.
"""

RESOURCE_VIEW = """
The Resource Viewer is a screen that displays information about a Resource. The Resource Viewer is composed of the following parts:

- Viewer Header: The header at the top of the screen that contains various fields about the Resource.
- Associated Contacts: A table that displays all Contacts that are linked to the Resource.
- Associated Organizations: A table that displays all Organizations that are linked to the Resource.

Double-clicking or alt-clicking on any entry of a table will open the View screen for that entry. For example, double-clicking on a Contact in the Associated Contacts table will open the Contact Viewer for that Contact.
"""

RESOURCE_TABLE = """
Resource tables are tables that display information about Resources. Resource tables are present in the following screens:

- Organization Viewer: Displays all Resources that are linked to the Organization.
- Contact Viewer: Displays all Resources that are linked to the Contact.

Resource tables are composed of Name and Value columns. Alt-clicking on any entry in a resource table will bring up the following options:

- View Resource: Opens the Resource Viewer for the selected Resource.
- Create Resource: Opens the Resource creation form and automatically links it to the selected Contact or Organization.
- Link Resource: Links the specified Resource to the selected Contact or Organization.
- Unlink Resource: Unlinks the selected Resource from the selected Contact or Organization.
- Delete Resource: Deletes the selected Resource and removes it from all Contacts and Organizations.
- Copy ID: Copies the ID of the selected Resource to your clipboard.
- Help: Opens the help menu.

"""

CUSTOM_FIELDS = """
Custom fields are fields that can be added to Contacts and Organizations. Custom fields are present in the following screens:

- Organization Viewer: Displays all custom fields that are linked to the Organization.
- Contact Viewer: Displays all custom fields that are linked to the Contact.

Custom fields are composed of a Name and Value column. Alt-clicking on any entry in a custom field table will bring up the following options:

- View Full Content: Opens a popup that displays the full content of the custom field.
- Create Custom Field: Opens a form to create a new custom field.
- Edit Custom Field: Opens a form to edit the selected custom field.
- Delete Custom Field: Deletes the selected custom field.
- Help: Opens the help menu.

"""

_help_mapping = {
    "ACTION_BAR": ACTION_BAR,
    "SEARCH_BAR": SEARCH_BAR,
    "SEARCH": SEARCH_SCREEN,
    "VIEWER_HEADER": viewer_header,
    "ORG_VIEWER": ORG_VIEWER,
    "CONTACT_VIEWER": CONTACT_VIEWER,
    "RESOURCE_VIEW": RESOURCE_VIEW,
    "RESOURCE_TABLE": RESOURCE_TABLE,
    "CUSTOM_FIELDS": CUSTOM_FIELDS,
}


def get_help_text(key: str) -> str:
    return _help_mapping.get(key, "")


def get_help_layout() -> list:
    return [
        [
            sg.Column(
                expand_x=True,
                pad=((0, 0), (0, 10)),
                right_click_menu=["", ["Help::HELP"]],
                layout=[
                    [
                        sg.Text("Help", font=("Helvetica", 25)),
                    ],
                    [
                        sg.Text(
                            "This is the help screen. Here, you can find information about how to use SimpleCTE. "
                            "Click on a button or field to learn more about it.",
                            pad=((0, 0), (0, 10)),
                        )
                    ],
                    [
                        sg.Multiline(
                            k="-HELP_TEXT-",
                            disabled=True,
                            expand_x=True,
                            expand_y=True,
                            pad=((0, 0), (0, 10)),
                            size=(50, 20),
                            font=("Helvetica", 15),
                        ),
                    ],
                ],
            )
        ]
    ]
