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
from process.events import handle_other_events

if TYPE_CHECKING:
    from process.app import App


__all__ = ("main_loop",)


def main_loop(app: "App"):
    while True:
        # AppStatus was meant to tell the lazy-loaded values when the app
        # is ready for them to update in another thread. I don't think it
        # does anything anymore.
        app.status = AppStatus.READY
        event, values = app.window.read()
        app.status = AppStatus.BUSY

        # The first time a user loads the program, they deserve a warm welcome!
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

        # Handle double-click events
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

        elif event.startswith("-ADD_RECORD-"):
            add_record_handler(app)

        elif event == "Copy ID":
            sg.clipboard_set(app.last_selected_id)

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
