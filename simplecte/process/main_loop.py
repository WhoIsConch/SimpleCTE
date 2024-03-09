from typing import TYPE_CHECKING
import PySimpleGUI as sg
import webbrowser

from utils.enums import AppStatus, Screen
from ui_management import (
    swap_to_org_viewer,
    swap_to_contact_viewer,
    swap_to_resource_viewer,
    settings_handler,
    backup_handler,
    export_handler,
    add_record_handler,
    help_manager,
)
from layouts import get_field_keys, get_sort_keys, get_first_time_layout
from database import get_table_values, Contact, Organization
from process.events import handle_other_events

if TYPE_CHECKING:
    from process.app import App


__all__ = ("main_loop",)


def _manage_custom_field(app: "App", values: dict, edit=False) -> None:
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
                disabled=not edit,
                key="-CUSTOM_FIELD_VALUE-",
            )
        ],
        [sg.Button("Close", key="-CLOSE-")],
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


def main_loop(app: "App"):
    while True:
        app.status = AppStatus.READY
        event, values = app.window.read()
        app.status = AppStatus.BUSY

        if app.settings.first_time:
            app.settings.first_time = False
            popup = sg.Window(
                "Welcome to SimpleCTE",
                get_first_time_layout(),
                icon="simplecte.ico",
                finalize=True,
                margins=(10, 10),
                modal=True,
            )
            popup.read()
            popup.close()

        if isinstance(event, tuple) and event[2][0] is not None:

            def doubleclick_check() -> bool:
                """
                Checks if the last selected ID is the same as the current ID.
                """
                try:
                    current_id = app.window[event[0]].get()[event[2][0]][0]
                except IndexError:
                    current_id = None
                return (
                    app.last_selected_id == current_id
                    and app.last_selected_id is not None
                )

            if event[0] in [
                "-ORG_TABLE-",
                "-CONTACT_ORGANIZATIONS_TABLE-",
                "-RESOURCE_ORGANIZATIONS_TABLE-",
            ]:
                app.check_doubleclick(
                    swap_to_org_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id),
                )

            elif event[0] in [
                "-CONTACT_TABLE-",
                "-ORG_CONTACT_INFO_TABLE-",
                "-RESOURCE_CONTACTS_TABLE-",
            ]:
                app.check_doubleclick(
                    swap_to_contact_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id),
                )

            elif event[0] in ["-ORG_RESOURCES_TABLE-", "-CONTACT_RESOURCES_TABLE-"]:
                app.check_doubleclick(
                    swap_to_resource_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id),
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

        # Handle any events that may have to do with updating data
        if handle_other_events(app, event, values):
            continue

        elif event == "-SEARCHTYPE-":
            if values["-SEARCHTYPE-"] == "Organizations":
                sort_fields = [
                    s.title() for s in get_sort_keys(screen=Screen.ORG_SEARCH).keys()
                ]
                search_fields = [
                    s.title() for s in get_field_keys(screen=Screen.ORG_SEARCH)
                ]

                app.window["-CONTACT_SCREEN-"].update(visible=False)
                app.window["-ORG_SCREEN-"].update(visible=True)
                app.window["-SEARCH_FIELDS-"].update(values=search_fields)
                app.window["-SORT_TYPE-"].update(values=sort_fields)

                app.stack.clear()
                app.stack.push(Screen.ORG_SEARCH)

            elif values["-SEARCHTYPE-"] == "Contacts":
                sort_fields = [
                    s.title()
                    for s in get_sort_keys(screen=Screen.CONTACT_SEARCH).keys()
                ]
                search_fields = [
                    s.title() for s in get_field_keys(screen=Screen.CONTACT_SEARCH)
                ]

                app.window["-ORG_SCREEN-"].update(visible=False)
                app.window["-CONTACT_SCREEN-"].update(visible=True)
                app.window["-SEARCH_FIELDS-"].update(values=search_fields)
                app.window["-SORT_TYPE-"].update(values=sort_fields)

                app.stack.clear()
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
                        get_table_values(
                            app,
                            Organization,
                            search_info=search_info,
                            descending=values["-SORT_DESCENDING-"],
                        )
                    )

                case Screen.CONTACT_SEARCH:
                    app.window["-CONTACT_TABLE-"].update(
                        get_table_values(
                            app,
                            Contact,
                            search_info=search_info,
                            descending=values["-SORT_DESCENDING-"],
                        )
                    )

            app.lazy_load_table_values(
                search_info, descending=values["-SORT_DESCENDING-"]
            )

        elif event.startswith("-ADD_RECORD-"):
            add_record_handler(app)

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
                [sg.Multiline(resource.value, size=(30, 10), disabled=True)],
                [sg.Button("Close")],
            ]

            view_window = sg.Window(
                "Full Resource Value", layout, finalize=True, modal=True
            )

            _ = view_window.read()
            view_window.close()

        elif event == "Copy ID":
            sg.clipboard_set(app.last_selected_id)

        elif event == "Create Custom Field":
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
                continue

            # Check if the user entered a name and value
            if not values["-FIELD_NAME-"] or not values["-FIELD_VALUE-"]:
                sg.popup("Field name and value are required!")
                continue

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
                continue

            # Get the ID of the record we're viewing

            field = app.db.create_custom_field(**create_kwargs)

            if not field:
                sg.popup(
                    "Error creating custom field.\nPerhaps you used the same name as an existing field?"
                )
                continue

            (swap_args[1])(**(swap_args[0]))

        elif event == "Edit Custom Field":
            _manage_custom_field(app, values, edit=True)

        elif event == "Delete Custom Field":
            # Get the ID of the record we're viewing
            if app.current_screen == Screen.ORG_VIEW:
                org_id = app.window["-ORG_VIEW-"].metadata

                try:
                    field_name = app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[
                        values["-ORG_CUSTOM_FIELDS_TABLE-"][0]
                    ][0]
                except IndexError:
                    continue

            elif app.current_screen == Screen.CONTACT_VIEW:
                contact_id = app.window["-CONTACT_VIEW-"].metadata

                try:
                    field_name = app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[
                        values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]
                    ][0]
                except IndexError:
                    continue

            confirmation = sg.popup_yes_no(
                "Are you sure you want to delete this field?", title="Delete Field"
            )

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
            _manage_custom_field(app, values)

        elif event == "Change Value":
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
                continue

            new_value = values["-NEW_VALUE-"]

            if new_value == resource.value:
                continue

            app.db.update_resource(resource_id, value=new_value)
            swap_to_resource_viewer(app, resource_id=resource_id, push=False)

        elif event == "-UPDATE_TABLES-":
            app.window["-CONTACT_TABLE-"].update(values["-UPDATE_TABLES-"][0])
            app.window["-ORG_TABLE-"].update(values["-UPDATE_TABLES-"][1])

        elif event == "-RESET_BUTTON-":
            # Reset the search parameters
            app.window["-SEARCH_QUERY-"].update("")
            app.window["-SEARCH_FIELDS-"].update("")
            app.window["-SORT_TYPE-"].update("")

            if app.current_screen == Screen.ORG_SEARCH:
                app.window["-ORG_TABLE-"].update(get_table_values(app, Organization))

            elif app.current_screen == Screen.CONTACT_SEARCH:
                app.window["-CONTACT_TABLE-"].update(get_table_values(app, Contact))

            app.lazy_load_table_values()

        elif event.startswith("-HELP-"):
            webbrowser.open("https://github.com/WhoIsConch/SimpleCTE/wiki")

        elif event.startswith("Help::"):
            help_manager(app, event.split("::")[-1])

        elif event.startswith("-SETTINGS-"):
            settings_handler(app)

        elif event.startswith("-BACKUP-"):
            backup_handler(app)

        elif event == "-EXPORT_ALL-":
            # Export all records in the database
            export_handler(app)

        elif event.endswith("STACK"):
            # Handle jumping between screens in the stack
            app.jump_to_screen(event, values)

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
                app,
                search_info={
                    "query": app.window["-SEARCH_QUERY-"].get(),
                    "field": app.window["-SEARCH_FIELDS-"].get(),
                    "sort": app.window["-SORT_TYPE-"].get(),
                    "descending": app.window["-SORT_DESCENDING-"].get(),
                },
                search_type=app.current_screen.name.split("_")[0].lower(),
            )

        elif event in ["-VIEW_RESOURCE-", "View Resource"]:
            if not app.last_selected_id:
                continue

            # View the resource
            swap_to_resource_viewer(app, resource_id=app.last_selected_id)

        else:
            continue
