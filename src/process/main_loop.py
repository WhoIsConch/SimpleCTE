from typing import TYPE_CHECKING
import PySimpleGUI as sg

from ..utils.enums import AppStatus, Screen
from ..ui_management import swap_to_org_viewer, swap_to_contact_viewer, swap_to_resource_viewer, settings_handler, \
    backup_handler, export_handler
from ..database.database import get_org_table_values, get_contact_table_values
from ..layouts import get_create_contact_layout, get_create_org_layout, get_field_keys, get_sort_keys
from ..utils.helpers import format_phone, strip_phone

if TYPE_CHECKING:
    from ..process.app import App


def manage_custom_field(app: 'App', values: dict, edit=False) -> None:
    try:
        record_id = app.window[app.current_screen.value].metadata
    except IndexError:
        return

    method = [
        {
            "app": app,
            "push": False
        }
    ]

    if app.current_screen == Screen.ORG_VIEW:
        record = app.db.get_organization(record_id)
        record_type = "org"
        method.insert(0, swap_to_org_viewer)
        method[1]["org_id"] = record.id

        try:
            field_name = \
                app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[values["-ORG_CUSTOM_FIELDS_TABLE-"][0]][0]

        except IndexError:
            return

    elif app.current_screen == Screen.CONTACT_VIEW:
        record = app.db.get_contact(record_id)
        record_type = "contact"
        method.insert(0, swap_to_contact_viewer)
        method[1]["contact_id"] = record.id

        try:
            field_name = \
                app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[
                    values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]][0]
        except IndexError:
            return

    else:
        return

    name_tooltip = "The names of custom fields cannot be changed. Consider creating a new custom field instead."

    layout = [
        [sg.Text("Custom Field Name: ", tooltip=name_tooltip), sg.Text(field_name, tooltip=name_tooltip)],
        [sg.Multiline(
            record.custom_fields[field_name],
            expand_x=True,
            size=(30, 10),
            horizontal_scroll=True,
            disabled=not edit,
            key="-CUSTOM_FIELD_VALUE-",
        )],
        [sg.Button("Close", key="-CLOSE-")]
    ]

    if edit:
        layout[2].insert(0, sg.Button("Edit", key="-EDIT-"))

    window = sg.Window("Custom Field Content", finalize=True, modal=True, layout=layout)

    event, values = window.read()
    window.close()

    if event == sg.WIN_CLOSED or event == "-CLOSE-":
        return

    elif event != "-EDIT-":
        return

    app.db.update_custom_field(
        name=values["-CUSTOM_FIELD_NAME-"],
        value=values["-CUSTOM_FIELD_VALUE-"],
        **{record_type: record_id}
    )

    method[0](**method[1])


def main_loop(app: "App"):
    while True:
        app.status = AppStatus.READY
        event, values = app.window.read()
        app.status = AppStatus.BUSY

        print(event, values, "\n")

        if isinstance(event, tuple) and event[2][0] is not None:
            def doubleclick_check() -> bool:
                """
                Checks if the last selected ID is the same as the current ID.
                """
                try:
                    current_id = app.window[event[0]].get()[event[2][0]][0]
                except IndexError:
                    current_id = None
                return app.last_selected_id == current_id and app.last_selected_id is not None

            if event[0] in ["-ORG_TABLE-", "-CONTACT_ORGANIZATIONS_TABLE-", "-RESOURCE_ORGANIZATIONS_TABLE-"]:
                app.check_doubleclick(
                    swap_to_org_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id)
                )

            elif event[0] in ["-CONTACT_TABLE-", "-ORG_CONTACT_INFO_TABLE-", "-RESOURCE_CONTACTS_TABLE-"]:
                app.check_doubleclick(
                    swap_to_contact_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id)
                )

            elif event[0] in ["-ORG_RESOURCES_TABLE-", "-CONTACT_RESOURCES_TABLE-"]:
                app.check_doubleclick(
                    swap_to_resource_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id)
                )

            try:
                app.last_selected_id = app.window[event[0]].get()[event[2][0]][0]
            except IndexError:
                app.last_selected_id = None

            continue

        # To not use methods such as startswith on other types
        if not isinstance(event, str) and event != sg.WIN_CLOSED:
            continue

        if event == sg.WIN_CLOSED or event.startswith("-LOGOUT-"):
            app.db.close_database(app)
            app.window.close()
            break

        if event == "-LOGIN-":
            server_address = values["-SERVER-"]
            server_port = values["-PORT-"]
            database_name = values["-DBNAME-"]
            username = values["-USERNAME-"]
            password = values["-PASSWORD-"]

            try:
                server_port = int(server_port)
            except ValueError:
                sg.popup("Invalid port!")
                continue

        elif event == "-SEARCHTYPE-":
            if values["-SEARCHTYPE-"] == "Organizations":
                sort_fields = [s.title() for s in get_sort_keys(screen=Screen.ORG_SEARCH).keys()]
                search_fields = [s.title() for s in get_field_keys(screen=Screen.ORG_SEARCH)]

                app.window["-CONTACT_SCREEN-"].update(visible=False)
                app.window["-ORG_SCREEN-"].update(visible=True)
                app.window["-SEARCH_FIELDS-"].update(values=search_fields)
                app.window["-SORT_TYPE-"].update(values=sort_fields)
                app.stack.push(Screen.ORG_SEARCH)

            elif values["-SEARCHTYPE-"] == "Contacts":
                sort_fields = [s.title() for s in get_sort_keys(screen=Screen.CONTACT_SEARCH).keys()]
                search_fields = [s.title() for s in get_field_keys(screen=Screen.CONTACT_SEARCH)]

                app.window["-ORG_SCREEN-"].update(visible=False)
                app.window["-CONTACT_SCREEN-"].update(visible=True)
                app.window["-SEARCH_FIELDS-"].update(values=search_fields)
                app.window["-SORT_TYPE-"].update(values=sort_fields)

                app.stack.push(Screen.CONTACT_SEARCH)

        elif event.startswith("-EXIT"):
            app.switch_to_last_screen()

        elif event == "-SEARCH_BUTTON-":
            search_info = {
                "query": values["-SEARCH_QUERY-"],
                "field": values["-SEARCH_FIELDS-"],
                "sort": values["-SORT_TYPE-"],
            }

            match app.current_screen:
                case Screen.ORG_SEARCH:
                    app.window["-ORG_TABLE-"].update(
                        get_org_table_values(app, search_info=search_info,
                                             descending=values["-SORT_DESCENDING-"])
                    )

                case Screen.CONTACT_SEARCH:
                    app.window["-CONTACT_TABLE-"].update(
                        get_contact_table_values(app, search_info=search_info,
                                                 descending=values["-SORT_DESCENDING-"])
                    )

        elif event.startswith("-ADD_RECORD-"):
            if app.current_screen in [Screen.CONTACT_SEARCH, Screen.CONTACT_VIEW]:
                new_window = sg.Window("Add Contact", get_create_contact_layout(), modal=True,
                                       finalize=True)
                event, values = new_window.read()
                new_window.close()

                if event == "-CANCEL-" or event == sg.WIN_CLOSED:
                    continue

                if not (values["-FIRST_NAME-"] and values["-LAST_NAME-"]):
                    sg.popup("First and last name are required to create a contact.")
                    continue

                elif values["-PHONE_NUMBER-"]:
                    try:
                        values["-PHONE_NUMBER-"] = int(values["-PHONE_NUMBER-"])
                    except ValueError:
                        sg.popup(
                            "Invalid phone number! Phone number must be a continuous string of numbers.")
                        continue

                db_values = {k.lower().replace("-", ""): v for k, v in values.items() if v}

                contact = app.db.create_contact(**db_values)

                swap_to_contact_viewer(app, contact=contact)

            elif app.current_screen in [Screen.ORG_SEARCH, Screen.ORG_VIEW]:
                new_window = sg.Window("Add Organization", get_create_org_layout(), modal=True,
                                       finalize=True)
                event, values = new_window.read()
                new_window.close()

                if event == "-CANCEL-" or event == sg.WIN_CLOSED:
                    continue

                if not values["-NAME-"] or not values["-TYPE-"]:
                    sg.popup("Name and type are required to create an organization.")
                    continue

                db_values = {k.lower().replace("-", ""): v for k, v in values.items() if v}

                organization = app.db.create_organization(**db_values)

                swap_to_org_viewer(app, org=organization)

            else:
                continue

            app.lazy_load_table_values()

        elif event == "View":
            method = None

            match app.current_screen:
                case Screen.ORG_SEARCH:
                    if not values["-ORG_TABLE-"]:
                        continue

                    method = swap_to_org_viewer

                case Screen.CONTACT_VIEW:
                    if not values["-CONTACT_ORGANIZATIONS_TABLE-"]:
                        continue

                    method = swap_to_org_viewer

                case Screen.CONTACT_SEARCH:
                    if not values["-CONTACT_TABLE-"]:
                        continue

                    method = swap_to_contact_viewer

                case Screen.ORG_VIEW:
                    if not values["-ORG_CONTACT_INFO_TABLE-"]:
                        continue

                    method = swap_to_contact_viewer

            if app.last_selected_id and method:
                method(app, app.last_selected_id)

        elif event == "View::RESOURCE_ORG":
            if not values["-RESOURCE_ORGANIZATIONS_TABLE-"]:
                continue

            if app.last_selected_id:
                swap_to_org_viewer(app, org_id=app.last_selected_id)

        elif event == "View::RESOURCE_CONTACT":
            if not values["-RESOURCE_CONTACTS_TABLE-"]:
                continue

            if app.last_selected_id:
                swap_to_contact_viewer(app, contact_id=app.last_selected_id)

        elif event == "View Full Value":
            resource = app.db.get_resource(app.window["-RESOURCE_VIEW-"].metadata)

            layout = [
                [sg.Text("Full Resource Value:")],
                [sg.Multiline(resource.value, size=(30, 10), horizontal_scroll=True, disabled=True)],
                [sg.Button("Close")]
            ]

            view_window = sg.Window("Full Resource Value", layout, finalize=True, modal=True)

            _ = view_window.read()
            view_window.close()

        elif event == "Add Contact":
            user_input = sg.popup_get_text(
                "Enter the ID of the contact you would like to add.\n\nIf you don't know the ID, you"
                "can find it by searching\nfor the contact, then alt-clicking on it and selecting \"Copy ID\".",
                title="Add Contact",
            )

            if not user_input:
                continue

            try:
                user_input = int(user_input)
            except ValueError:
                sg.popup("Invalid ID!")
                continue

            org_id = app.window["-ORG_VIEW-"].metadata

            status = app.db.add_contact_to_org(user_input, org_id)

            if not status:
                sg.popup("Error adding contact.\nPerhaps you used an incorrect ID?")
                continue

            swap_to_org_viewer(app, org_id=org_id, push=False)

        elif event == "Remove Contact":
            # Get contact selected in the table
            try:
                contact_name = \
                    app.window["-ORG_CONTACT_INFO_TABLE-"].get()[values["-ORG_CONTACT_INFO_TABLE-"][0]][
                        0]
            except IndexError:
                continue

            # Get organization name
            org_id = app.window["-ORG_VIEW-"].metadata

            # Remove contact from organization
            status = app.db.remove_contact_from_org(contact_name, org_id)

            if not status:
                sg.popup("Error removing contact.")
                continue

            swap_to_org_viewer(app, org_id=org_id, push=False)

        elif event == "Add Organization":
            # Add an organization to the contact.
            user_input = sg.popup_get_text(
                "Enter the ID of the organization you would like to add.\n\nIf you don't know the ID, "
                "you can find it by"
                "searching\nfor the organization, then alt-clicking on it and selecting \"Copy ID\".",
                title="Add Organization",
            )

            contact_id = app.window["-CONTACT_VIEW-"].metadata

            if not user_input:
                continue

            try:
                user_input = int(user_input)
            except ValueError:
                sg.popup("Invalid ID!")
                continue

            status = app.db.add_contact_to_org(contact_id, user_input)

            if not status:
                sg.popup("Error adding organization.\nPerhaps you used an incorrect ID?")
                continue

            swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Remove Organization":
            # Get organization selected in the table
            try:
                org_id = \
                    app.window["-CONTACT_ORGANIZATIONS_TABLE-"].get()[
                        values["-CONTACT_ORGANIZATIONS_TABLE-"][0]][0]
            except IndexError:
                sg.popup("No organization selected!")
                continue

            # Get contact name
            contact_id = app.window["-CONTACT_VIEW-"].metadata

            # Remove contact from organization
            status = app.db.remove_contact_from_org(contact_id, org_id)

            if not status:
                sg.popup("Error removing organization.")
                continue

            swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Copy ID":
            sg.clipboard_set(app.last_selected_id)

        elif event == "Change Title":
            # Triggered when a user tries to change the title of a user
            # in an organization. This is only available in the organization
            # view.

            # Get the organization ID
            org_id = app.window["-ORG_VIEW-"].metadata

            # Get the contact ID
            try:
                contact_id = \
                    app.window["-ORG_CONTACT_INFO_TABLE-"].get()[values["-ORG_CONTACT_INFO_TABLE-"][0]][0]
            except IndexError:
                continue

            title = sg.popup_get_text("Enter the new title for this contact.", title="Change Title")

            if not title:
                continue

            status = app.db.change_contact_title(org_id, contact_id, title)

            if not status:
                sg.popup("Error changing title.")
                continue

            swap_to_org_viewer(app, org_id=org_id, push=False)

        elif event == "Create Resource":
            input_window = sg.Window("Create Resource", [
                [sg.Text("Resource Name:"), sg.Input(key="-RESOURCE_NAME-")],
                [sg.Text("Resource Value:"), sg.Input(key="-RESOURCE_VALUE-")],
                [sg.Button("Create"), sg.Button("Cancel")]
            ], finalize=True, modal=True)

            event, values = input_window.read()

            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            if not values["-RESOURCE_NAME-"] or not values["-RESOURCE_VALUE-"]:
                sg.popup("Resource name and value are required!")
                continue

            resource = app.db.create_resource(name=values["-RESOURCE_NAME-"], value=values["-RESOURCE_VALUE-"])

            if app.current_screen == Screen.ORG_VIEW:
                app.db.link_resource(org=app.window["-ORG_VIEW-"].metadata, resource=resource.id)
                swap_to_org_viewer(app, org_id=app.window["-ORG_VIEW-"].metadata, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.link_resource(contact=app.window["-CONTACT_VIEW-"].metadata, resource=resource.id)
                swap_to_contact_viewer(app, contact_id=app.window["-CONTACT_VIEW-"].metadata, push=False)

        elif event == "Delete Resource":
            if app.current_screen == Screen.ORG_VIEW:
                try:
                    resource_id = app.window["-ORG_RESOURCES_TABLE-"].get()[values["-ORG_RESOURCES_TABLE-"][0]][
                        0]
                except IndexError:
                    continue

            elif app.current_screen == Screen.CONTACT_VIEW:
                try:
                    resource_id = \
                        app.window["-CONTACT_RESOURCES_TABLE-"].get()[values["-CONTACT_RESOURCES_TABLE-"][0]][0]
                except IndexError:
                    continue

            confirmation = sg.popup_yes_no(
                "Are you sure you want to delete this resource?\nThis will remove the resource for all other "
                "records, too.",
                title="Delete Resource")

            if confirmation == "No" or confirmation == sg.WIN_CLOSED:
                continue

            if app.current_screen == Screen.ORG_VIEW:
                app.db.delete_resource(resource_id)

                org_id = app.window["-ORG_VIEW-"].metadata
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.delete_resource(resource_id)

                contact_id = app.window["-CONTACT_VIEW-"].metadata
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Link Resource":
            # Get the resource ID
            info_window = sg.Window("Link Resource", [
                [sg.Text("Resource ID:"), sg.Input(key="-RESOURCE_ID-")],
                [sg.Button("Link"), sg.Button("Cancel")]
            ], finalize=True, modal=True)

            event, values = info_window.read()
            info_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            try:
                resource_id = int(values["-RESOURCE_ID-"])
            except ValueError:
                sg.popup("Invalid resource ID!")
                continue

            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                app.db.link_resource(org=org_id, resource=resource_id)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                app.db.link_resource(contact=contact_id, resource=resource_id)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Unlink Resource":
            # Get the resource ID
            if app.current_screen == Screen.ORG_VIEW:
                try:
                    resource_id = app.window["-ORG_RESOURCES_TABLE-"].get()[values["-ORG_RESOURCES_TABLE-"][0]][
                        0]
                except IndexError:
                    continue

            elif app.current_screen == Screen.CONTACT_VIEW:
                try:
                    resource_id = \
                        app.window["-CONTACT_RESOURCES_TABLE-"].get()[values["-CONTACT_RESOURCES_TABLE-"][0]][0]
                except IndexError:
                    continue

            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                app.db.unlink_resource(org=org_id, resource=resource_id)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                app.db.unlink_resource(contact=contact_id, resource=resource_id)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Create Custom Field":
            # Create a new window to get the field name and value
            input_window = sg.Window("Create Custom Field", [
                [sg.Text("Field Name:"), sg.Input(key="-FIELD_NAME-")],
                [sg.Text("Field Value:"), sg.Input(key="-FIELD_VALUE-")],
                [sg.Button("Create"), sg.Button("Cancel")]
            ], finalize=True, modal=True)

            # Read the window and close it
            event, values = input_window.read()
            input_window.close()

            # Check if the user clicked cancel
            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            # Check if the user entered a name and value
            if not values["-FIELD_NAME-"] or not values["-FIELD_VALUE-"]:
                sg.popup("Field name and value are required!")
                continue

            create_kwargs = {
                "name": values["-FIELD_NAME-"],
                "value": values["-FIELD_VALUE-"]
            }

            swap_args = [
                {
                    "app": app,
                    "push": False
                }
            ]

            if app.current_screen == Screen.ORG_VIEW:
                create_kwargs["org"] = swap_args[0]["org_id"] = app.window["-ORG_VIEW-"].metadata
                swap_args.append(swap_to_org_viewer)

            elif app.current_screen == Screen.CONTACT_VIEW:
                create_kwargs["contact"] = swap_args[0]["contact_id"] = app.window["-CONTACT_VIEW-"].metadata

                swap_args.append(swap_to_contact_viewer)

            else:
                continue

            # Get the ID of the record we're viewing

            field = app.db.create_custom_field(**create_kwargs)

            if not field:
                sg.popup(
                    "Error creating custom field.\nPerhaps you used the same name as an existing field?")
                continue

            (swap_args[1])(**(swap_args[0]))

        elif event == "Edit Custom Field":
            manage_custom_field(app, values, edit=True)

        elif event == "Delete Custom Field":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata

                try:
                    field_name = \
                        app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[values["-ORG_CUSTOM_FIELDS_TABLE-"][0]][0]
                except IndexError:
                    continue

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata

                try:
                    field_name = \
                        app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[
                            values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]][0]
                except IndexError:
                    continue

            confirmation = sg.popup_yes_no(
                "Are you sure you want to delete this field?",
                title="Delete Field")

            if confirmation == "No" or confirmation == sg.WIN_CLOSED:
                continue

            # Delete the field
            if app.current_screen == Screen.ORG_VIEW:
                app.db.delete_custom_field(org=org_id, name=field_name)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.delete_custom_field(contact=contact_id, name=field_name)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "View Full Content":
            # For custom fields
            manage_custom_field(app, values)

        elif event == "Change Name":
            # Change the name of a record.

            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata

                try:
                    name = app.window["-NAME-"].get()
                except IndexError:
                    continue

                layout = [
                    [sg.Text("New Name:"), sg.Input(key="-NAME-", default_text=name)],
                    [sg.Button("Change"), sg.Button("Cancel")]
                ]

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                contact = app.db.get_contact(contact_id)

                try:
                    name = app.window["-NAME-"].get()
                except IndexError:
                    continue

                layout = [
                    [sg.Text("New First Name:"), sg.Input(key="-FIRST_NAME-", default_text=contact.first_name)],
                    [sg.Text("New Last Name:"), sg.Input(key="-LAST_NAME-", default_text=contact.last_name)],
                    [sg.Button("Change"), sg.Button("Cancel")]
                ]

            elif app.current_screen == Screen.RESOURCE_VIEW:
                resource_id = app.window["-RESOURCE_VIEW-"].metadata
                resource = app.db.get_resource(resource_id)

                try:
                    name = app.window["-RESOURCE_NAME-"].get()
                except IndexError:
                    continue

                layout = [
                    [sg.Text("New Name:"), sg.Input(key="-NAME-", default_text=resource.name)],
                    [sg.Button("Change"), sg.Button("Cancel")]
                ]

            else:
                continue

            input_window = sg.Window("Change Name", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            new_org_name = values.get("-NAME-", "")
            new_first_name = values.get("-FIRST_NAME-", "")
            new_last_name = values.get("-LAST_NAME-", "")

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            if not (new_org_name or new_first_name or new_last_name):
                sg.popup("A name is required!")
                continue

            if len(new_org_name) > 50 or len(new_first_name) > 50 or len(new_last_name) > 50:
                confirmation = sg.popup_yes_no(
                    "Making a name too long may cause issues with the UI. Are you sure you want to continue?")

                if confirmation == "No" or confirmation == sg.WIN_CLOSED:
                    continue

            if app.current_screen == Screen.ORG_VIEW:
                app.db.update_organization(org_id, name=new_org_name)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.update_contact(contact_id, first_name=new_first_name, last_name=new_last_name)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

            elif app.current_screen == Screen.RESOURCE_VIEW:
                app.db.update_resource(resource_id, name=new_org_name)
                swap_to_resource_viewer(app, resource_id=resource_id, push=False)

            app.lazy_load_table_values()

        elif event == "Change Status":
            # Change the status of a record.

            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata

                try:
                    status = app.window["-STATUS-"].get()
                except IndexError:
                    continue

                layout = [
                    [sg.Text("New Status:"), sg.Input(key="-STATUS-", default_text=status)],
                    [sg.Button("Change"), sg.Button("Cancel")]
                ]

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                contact = app.db.get_contact(contact_id)

                try:
                    status = app.window["-STATUS-"].get()
                except IndexError:
                    continue

                layout = [
                    [sg.Text("New Status:"), sg.Input(key="-STATUS-", default_text=contact.status)],
                    [sg.Button("Change"), sg.Button("Cancel")]
                ]

            input_window = sg.Window("Change Status", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            new_org_status = values.get("-STATUS-", "")
            new_contact_status = values.get("-STATUS-", "")

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            if not (new_org_status or new_contact_status):
                sg.popup("A status is required!")
                continue

            if len(new_org_status) > 50 or len(new_contact_status) > 50:
                confirmation = sg.popup_yes_no(
                    "Making a status too long may cause issues with the UI. Are you sure you want to continue?")

                if confirmation == "No" or confirmation == sg.WIN_CLOSED:
                    continue

            if app.current_screen == Screen.ORG_VIEW:
                app.db.update_organization(org_id, status=new_org_status)
                swap_to_org_viewer(app, org_id=org_id, push=False)
                app.lazy_load_table_values()

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.update_contact(contact_id, status=new_contact_status)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "View All Phones":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

                phones = [format_phone(phone) for phone in record.phones]

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata

                record = app.db.get_contact(contact_id)
                phones = [format_phone(phone) for phone in record.phone_numbers]

            layout = [
                [sg.Text("Phone Numbers:")],
                [sg.Multiline("\n".join(list(phones)), size=(30, 10), disabled=True, horizontal_scroll=True)],
                [sg.Button("Close")]
            ]

            input_window = sg.Window("View All Phones", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

        elif event == "Edit Phones":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

                phones = [format_phone(phone) for phone in record.phones]

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata

                record = app.db.get_contact(contact_id)
                phones = [format_phone(phone) for phone in record.phone_numbers]

            layout = [
                [sg.Text("Phone Numbers, one per line\n(The first number is primary):")],
                [sg.Multiline("\n".join(list(phones)), size=(30, 10), key="-PHONES-", horizontal_scroll=True)],
                [sg.Button("Save"), sg.Button("Cancel")]
            ]

            input_window = sg.Window("Edit Phones", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            try:
                new_phones = [int(strip_phone(phone)) for phone in values["-PHONES-"].split("\n")]
            except ValueError:
                sg.popup(
                    "Invalid phone number! Phone number must be a continuous string of numbers, or a string "
                    "of numbers separated by dashes or parentheses.")
                continue

            if app.current_screen == Screen.ORG_VIEW:
                app.db.update_organization(org_id, phones=new_phones)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.update_contact(contact_id, phone_numbers=new_phones)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "View All Addresses":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                record = app.db.get_contact(contact_id)

            layout = [
                [sg.Text("Addresses:")],
                [sg.Multiline("\n".join(list(record.addresses)), size=(30, 10), disabled=True,
                              horizontal_scroll=True)],
                [sg.Button("Close")]
            ]

            input_window = sg.Window("View All Addresses", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

        elif event == "Edit Addresses":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                record = app.db.get_contact(contact_id)

            layout = [
                [sg.Text("Addresses, one per line\n(The first address is primary):")],
                [sg.Multiline("\n".join(list(record.addresses)), size=(30, 10), key="-ADDRESSES-",
                              horizontal_scroll=True)],
                [sg.Button("Save"), sg.Button("Cancel")]
            ]

            input_window = sg.Window("Edit Addresses", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            new_addresses = values["-ADDRESSES-"].split("\n")

            if app.current_screen == Screen.ORG_VIEW:
                app.db.update_organization(org_id, addresses=new_addresses)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.update_contact(contact_id, addresses=new_addresses)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "View All Emails":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                record = app.db.get_contact(contact_id)

            layout = [
                [sg.Text("Emails:")],
                [sg.Multiline("\n".join(list(record.emails)), size=(30, 10), disabled=True,
                              horizontal_scroll=True)],
                [sg.Button("Close")]
            ]

            input_window = sg.Window("View All Emails", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

        elif event == "Edit Emails":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                record = app.db.get_contact(contact_id)

            layout = [
                [sg.Text("Emails, one per line\n(The first email is primary):")],
                [sg.Multiline("\n".join(list(record.emails)), size=(30, 10), key="-EMAILS-")],
                [sg.Button("Save"), sg.Button("Cancel")]
            ]

            input_window = sg.Window("Edit Emails", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            new_emails = values["-EMAILS-"].split("\n")

            if app.current_screen == Screen.ORG_VIEW:
                app.db.update_organization(org_id, emails=new_emails)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.update_contact(contact_id, emails=new_emails)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Edit Availability":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                record = app.db.get_organization(org_id)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                record = app.db.get_contact(contact_id)

            layout = [
                [sg.Text("Availability:")],
                [sg.Multiline(record.availability, size=(30, 10), key="-AVAILABILITY-")],
                [sg.Button("Save"), sg.Button("Cancel")]
            ]

            input_window = sg.Window("Edit Availability", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            new_availability = values["-AVAILABILITY-"]

            if app.current_screen == Screen.ORG_VIEW:
                app.db.update_organization(org_id, availability=new_availability)
                swap_to_org_viewer(app, org_id=org_id, push=False)

            elif app.current_screen == Screen.CONTACT_VIEW:
                app.db.update_contact(contact_id, availability=new_availability)
                swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Edit::CONTACT_INFO":
            # If the contact info is one of Email, Phone, or Address, trigger
            # The appropriate event.
            index = values["-CONTACT_INFO_TABLE-"][0]
            title = app.window["-CONTACT_INFO_TABLE-"].get()[index][0]

            if title == "Email":
                event = "Edit Emails"
            elif title == "Phone":
                event = "Edit Phones"
            elif title == "Address":
                event = "Edit Addresses"
            elif title == "Availability":
                event = "Edit Availability"
            else:
                continue

            # Trigger the event
            event = app.window.write_event_value(event, None)

        elif event == "View More::CONTACT_INFO":
            # If the contact info is one of Email, Phone, or Address, trigger
            # The appropriate event.
            index = values["-CONTACT_INFO_TABLE-"][0]
            title = app.window["-CONTACT_INFO_TABLE-"].get()[index][0]

            if title == "Email":
                event = "View All Emails"
            elif title == "Phone":
                event = "View All Phones"
            elif title == "Address":
                event = "View All Addresses"
            else:
                continue

            # Trigger the event
            event = app.window.write_event_value(event, None)

        elif event == "Add::CONTACT_INFO":
            # Show a basic prompt for the user to enter the contact info

            input_window = sg.Window("Add Contact Info", [
                [sg.Text("Add new contact info. If you want to add an address, email, or phone,\nconsider "
                         "alt-clicking an entry in the table and selecting \"Edit.\"")],
                [sg.Text("Contact Info Type:"), sg.Input(key="-CONTACT_INFO_TYPE-")],
                [sg.Text("Contact Info Value:"), sg.Input(key="-CONTACT_INFO_VALUE-")],
                [sg.Button("Add"), sg.Button("Cancel")]
            ], finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            if not values["-CONTACT_INFO_TYPE-"] or not values["-CONTACT_INFO_VALUE-"]:
                sg.popup("Contact info type and value are required!")
                continue

            if len(values["-CONTACT_INFO_TYPE-"]) > 50 or len(values["-CONTACT_INFO_VALUE-"]) > 50:
                confirmation = sg.popup_yes_no(
                    "Making a contact info type or value too long may cause issues with the UI. Are you sure you "
                    "want to continue?")

                if confirmation == "No" or confirmation == sg.WIN_CLOSED:
                    continue

            # Check if any other contact info has the same title
            for title in app.window["-CONTACT_INFO_TABLE-"].get():
                if title[0] == values["-CONTACT_INFO_TYPE-"]:
                    sg.popup("A contact info type with that name already exists!")
                    continue

            # Get the contact ID
            contact_id = app.window["-CONTACT_VIEW-"].metadata

            # Add the contact info
            app.db.create_contact_info(values["-CONTACT_INFO_TYPE-"], values["-CONTACT_INFO_VALUE-"],
                                       contact=contact_id)

            # Reload the table values
            swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Delete::CONTACT_INFO":
            # Get the contact info ID
            try:
                contact_info_name = \
                    app.window["-CONTACT_INFO_TABLE-"].get()[values["-CONTACT_INFO_TABLE-"][0]][0]
                contact_info_value = \
                    app.window["-CONTACT_INFO_TABLE-"].get()[values["-CONTACT_INFO_TABLE-"][0]][1]
            except IndexError:
                continue

            # Get the contact ID
            contact_id = app.window["-CONTACT_VIEW-"].metadata

            # Delete the contact info
            if contact_info_name.lower() == "phone":
                contact_info_value = int(strip_phone(contact_info_value))

            app.db.delete_contact_info(contact_info_name, contact_info_value, contact=contact_id)

            # Reload the table values
            swap_to_contact_viewer(app, contact_id=contact_id, push=False)

        elif event == "Change Value":
            # Change the value of a resource
            resource_id = app.window["-RESOURCE_VIEW-"].metadata
            resource = app.db.get_resource(resource_id)

            layout = [
                [sg.Text("Full Resource Value:")],
                [sg.Multiline(resource.value, size=(30, 10), horizontal_scroll=True, key="-NEW_VALUE-")],
                [sg.Button("Close")]
            ]

            input_window = sg.Window("Change Value", layout, finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            new_value = values["-NEW_VALUE-"]

            if new_value == resource.value:
                continue

            app.db.update_resource(resource_id, value=new_value)
            swap_to_resource_viewer(app, resource_id=resource_id, push=False)

        elif event in ["Link Organization", "Link Contact"]:
            # Link an organization to a contact via the Contact View screen
            selected_item = event.split(" ")[-1]

            input_window = sg.Window(f"Link {selected_item}", layout=[
                [sg.Text(f"{selected_item} ID:"), sg.Input(key="-RECORD_ID-", size=(10, 20))
                 ],
                [sg.Button("Link"), sg.Button("Cancel")]
            ], finalize=True, modal=True)

            event, values = input_window.read()
            input_window.close()

            if event == "Cancel" or event == sg.WIN_CLOSED:
                continue

            try:
                record_id = int(values["-RECORD_ID-"])
            except ValueError:
                sg.popup(f"Invalid {record} ID!")
                continue

            resource_id = app.window["-RESOURCE_VIEW-"].metadata

            if selected_item.lower() == "organization":
                app.db.link_resource(org=record_id, resource=resource_id)
            elif selected_item.lower() == "contact":
                app.db.link_resource(contact=record_id, resource=resource_id)

            swap_to_resource_viewer(app, resource_id=resource_id, push=False)

        elif event in ["Unlink Contact", "Unlink Organization"]:
            # Unlink an organization or contact from a resource
            selected_item = event.split(" ")[-1]
            resource_id = app.window["-RESOURCE_VIEW-"].metadata

            if selected_item.lower() == "organization":
                record_id = \
                app.window["-RESOURCE_ORGANIZATIONS_TABLE-"].get()[values["-RESOURCE_ORGANIZATIONS_TABLE-"][0]][0]
                app.db.unlink_resource(resource=resource_id, org=record_id)

            elif selected_item.lower() == "contact":
                record_id = app.window["-RESOURCE_CONTACTS_TABLE-"].get()[values["-RESOURCE_CONTACTS_TABLE-"][0]][0]
                app.db.unlink_resource(resource=resource_id, contact=record_id)

            swap_to_resource_viewer(app, resource_id=resource_id, push=False)

        elif event.lower().strip("-").startswith("delete"):
            confirmation = sg.popup_yes_no("Are you sure you want to delete this record?",
                                           title="Delete Record")

            if confirmation != "Yes":
                continue

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
                    app.window["-ORG_TABLE-"].update(get_org_table_values(app))

                case Screen.CONTACT_SEARCH:
                    app.db.delete_contact(app.last_selected_id)
                    app.window["-CONTACT_TABLE-"].update(get_contact_table_values(app))

            # Reload the table values after the record is deleted
            app.lazy_load_table_values()

        elif event == "-UPDATE_TABLES-":
            app.window["-CONTACT_TABLE-"].update(values["-UPDATE_TABLES-"][0])
            app.window["-ORG_TABLE-"].update(values["-UPDATE_TABLES-"][1])

        elif event.startswith("-SETTINGS-"):
            settings_handler(app)

        elif event.startswith("-BACKUP-"):
            backup_handler(app)

        elif event == "-EXPORT_ALL-":
            # Export all records in the database
            export_handler(app)

        elif event.startswith("-EXPORT-"):
            # Export the selected record
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata
                export_handler(app, org_id=org_id)

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata
                export_handler(app, contact_id=contact_id)

            else:
                export_handler(app)

        elif event == "-EXPORT_FILTER-":
            # Export based on the current search parameters
            export_handler(
                app, search_info={
                    "query": app.window["-SEARCH_QUERY-"].get(),
                    "field": app.window["-SEARCH_FIELDS-"].get(),
                    "sort": app.window["-SORT_TYPE-"].get(),
                }
            )

        elif event in ["-VIEW_RESOURCE-", "View Resource"]:
            # View the resource
            swap_to_resource_viewer(app, resource_id=app.last_selected_id)

        else:
            continue
