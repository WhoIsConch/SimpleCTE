import json
import logging
import os
import threading
from datetime import datetime
from typing import Callable

import PySimpleGUI as sg

from database import db
from enums import DBStatus, Screen, AppStatus
from layouts import (
    login_constructor,
    search_constructor,
    empty_org_view_constructor,
    empty_contact_view_constructor,
    swap_to_org_viewer,
    swap_to_contact_viewer,
    get_contact_table,
    get_organization_table,
    create_contact,
    create_organization
)


class Stack:
    """
    Add a stack that will keep track of each screen.
    If a stack is associated with information, such as a Viewer,
    it will also keep track of that information.
    """

    def __init__(self):
        self.stack = []

    def push(self, screen: Screen, data: any = None) -> None:
        self.stack.append((screen, data))

    def pop(self) -> None:
        self.stack.pop()

    def peek(self) -> tuple[Screen, dict | None]:
        return self.stack[-1]


class App:
    def __init__(self):
        self.db = db
        self.logger = logging.getLogger("app")
        self.stack = Stack()
        self.window: sg.Window | None = None
        self.status = AppStatus.BUSY
        self.last_clicked_table_time = None
        self.last_selected_id = None
        self.logger.info("Loading database settings...")

        self.settings = self.load_settings()

        if (
                self.settings["database"]["system"] == "sqlite"
                and self.settings["database"]["location"] == "local"
        ):
            self.logger.info("Constructing SQLite database...")
            self.db.construct_database("sqlite", self.settings["database"]["path"])
            self.stack.push(Screen.ORG_SEARCH)

        elif (
                self.settings["database"]["system"] == "sqlite"
                and self.settings["database"]["location"] == "remote"
        ):
            self.logger.info("Constructing remote SQLite database...")
            self.db.construct_database(
                "sqlite",
                self.settings["database"]["path"],
                server_address=self.settings["database"]["address"],
                server_port=self.settings["database"]["port"],
                username=self.settings["database"]["username"],
            )
            self.stack.push(Screen.ORG_SEARCH)

        elif (
                self.settings["database"]["system"] == "postgres"
                or self.settings["database"]["system"] == "mysql"
        ):
            self.logger.info("Constructing remote database...")
            try:
                self.db.construct_database(
                    self.settings["database"]["system"],
                    self.settings["database"]["name"],
                    server_address=self.settings["database"]["address"],
                    server_port=self.settings["database"]["port"],
                    username=self.settings["database"]["username"],
                    password=self.settings["database"]["password"],
                )
            except Exception:
                self.db.status = (
                    DBStatus.LOGIN_REQUIRED
                )  # TODO: Handle this via Database instead of in App
                self.stack.push(Screen.LOGIN)

        else:
            self.logger.error("Invalid database system!")
            raise ValueError("Invalid database system!")

    @property
    def current_screen(self) -> Screen:
        return self.stack.peek()[0]

    @property
    def last_screen(self) -> Screen:
        return self.stack.stack[-2][0]

    def hide_major_screens(self):
        screens = ["-SEARCH_SCREEN-", "-ORG_VIEW-", "-CONTACT_VIEW-", "-ORG_SCREEN-", "-CONTACT_SCREEN-"]

        for screen in screens:
            self.window[screen].update(visible=False)

    def switch_screen(self, screen: Screen, data=None, push: bool = True) -> None:
        app.last_selected_id = None

        if push:
            self.stack.push(screen, data)

        self.hide_major_screens()

        if screen == Screen.ORG_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-ORG_SCREEN-"].update(visible=True)

        elif screen == Screen.CONTACT_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-CONTACT_SCREEN-"].update(visible=True)

        elif screen == Screen.ORG_VIEW:
            self.window["-ORG_VIEW-"].update(visible=True)

        elif screen == Screen.CONTACT_VIEW:
            self.window["-CONTACT_VIEW-"].update(visible=True)

    def switch_to_last_screen(self) -> None:
        self.stack.pop()

        self.hide_major_screens()

        if self.current_screen == Screen.ORG_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-ORG_SCREEN-"].update(visible=True)

        elif self.current_screen == Screen.CONTACT_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-CONTACT_SCREEN-"].update(visible=True)

        elif self.current_screen == Screen.ORG_VIEW:
            self.window["-ORG_VIEW-"].update(visible=True)
            swap_to_org_viewer(self, org_id=self.stack.peek()[1], push=False)

        elif self.current_screen == Screen.CONTACT_VIEW:
            self.window["-CONTACT_VIEW-"].update(visible=True)
            swap_to_contact_viewer(self, contact_id=self.stack.peek()[1], push=False)

    def load_settings(self) -> dict:
        self.logger.info("Loading settings...")
        try:
            with open(
                    os.path.dirname(os.path.realpath(__file__)) + "\\data\\settings.json",
                    "r",
            ) as f:
                settings: dict = json.load(f)  # Load our settings file

        except FileNotFoundError:
            self.logger.info("No settings found. Creating settings...")
            settings = {
                "database": {
                    "system": "sqlite",
                    "location": "local",
                    "path": "data/db.db",
                    "name": "db.db",
                    "address": "",
                    "port": 0,
                    "username": "",
                },
                "theme": "dark",
            }

            self.save_settings(settings)
            return settings

        db_info = settings.get("database")

        if not (db_info and db_info.get("system")):
            self.logger.info("No database info found. Creating settings...")
            settings["database"] = {
                "system": "sqlite",
                "location": "local",
                "path": "data/database.db",
                "name": "database.db",
                "address": "",
                "port": 0,
                "username": "",
            }

            self.save_settings()

        self.logger.info("Settings loaded!")
        return settings

    def save_settings(self, settings: dict | None = None) -> None:
        self.logger.info("Saving settings...")

        with open(
                os.path.dirname(os.path.realpath(__file__)) + "\\data\\settings.json", "w"
        ) as f:
            json.dump(settings or self.settings, f, indent=4)

        self.logger.info("Settings saved!")


app = App()


def check_doubleclick(callback: Callable, args: tuple, check: Callable | None = None) -> None:
    if (app.last_clicked_table_time is not None) and (
            (datetime.now() - app.last_clicked_table_time).total_seconds() < 0.5
    ):
        if check and check():
            callback(*args)

        app.last_clicked_table_time = None
    else:
        app.last_clicked_table_time = datetime.now()


def lazy():
    contact_values = []
    org_values = []

    get_contact_table(app, values_only=True, lazy=True, table_values=contact_values)
    get_organization_table(app, values_only=True, lazy=True, table_values=org_values)

    while not app.status == AppStatus.READY:
        pass

    app.window["-CONTACT_TABLE-"].update(values=contact_values)
    app.window["-ORG_TABLE-"].update(values=org_values)


def start_lazy():
    threading.Thread(target=lazy).start()


sg.theme(app.settings["theme"])

if app.current_screen == Screen.LOGIN:
    app.window = sg.Window("Log In to your SimpleCTE Database", login_constructor())

else:
    app.window = sg.Window(
        "SimpleCTE",
        finalize=True,
        layout=[
            [
                sg.Column(
                    layout=search_constructor(app),
                    key="-SEARCH_SCREEN-",
                    visible=True,
                ),
                sg.Column(
                    layout=empty_org_view_constructor(),
                    key="-ORG_VIEW-",
                    visible=False,
                ),
                sg.Column(
                    layout=empty_contact_view_constructor(),
                    key="-CONTACT_VIEW-",
                    visible=False,
                ),
            ]
        ],
    )

app.window.Font = ("Arial", 12)
start_lazy()

while True:
    app.status = AppStatus.READY
    event, values = app.window.read()
    app.status = AppStatus.BUSY

    if event == sg.WIN_CLOSED or event == "Exit":
        break

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


        match event[0]:
            case "-ORG_TABLE-" | "-CONTACT_ORGANIZATIONS_TABLE-":
                check_doubleclick(
                    swap_to_org_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id)
                )

            case "-CONTACT_TABLE-" | "-ORG_CONTACT_INFO_TABLE-":
                check_doubleclick(
                    swap_to_contact_viewer,
                    check=doubleclick_check,
                    args=(app, app.last_selected_id)
                )
        try:
            app.last_selected_id = app.window[event[0]].get()[event[2][0]][0]
        except IndexError:
            app.last_selected_id = None
    else:
        match event:
            case "-LOGIN-":
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

            case "-SEARCHTYPE-":
                if values["-SEARCHTYPE-"] == "Organizations":
                    app.window["-CONTACT_SCREEN-"].update(visible=False)
                    app.window["-ORG_SCREEN-"].update(visible=True)
                    app.stack.push(Screen.ORG_SEARCH)

                elif values["-SEARCHTYPE-"] == "Contacts":
                    app.window["-ORG_SCREEN-"].update(visible=False)
                    app.window["-CONTACT_SCREEN-"].update(visible=True)

                    app.stack.push(Screen.CONTACT_SEARCH)

            case "-EXIT-" | "-EXIT_1-" | "-CONTACT_EXIT-" | "-CONTACT_EXIT_1-":
                app.switch_to_last_screen()

            case "-SEARCH_BUTTON-":
                search_info = {
                    "query": values["-SEARCH_QUERY-"],
                    "field": values["-SEARCH_FIELDS-"],
                    "sort": values["-SORT_TYPE-"],
                }

                match app.current_screen:
                    case Screen.ORG_SEARCH:
                        app.window["-ORG_TABLE-"].update(
                            get_organization_table(app, values_only=True, search_info=search_info))

                    case Screen.CONTACT_SEARCH:
                        app.window["-CONTACT_TABLE-"].update(
                            get_contact_table(app, values_only=True, search_info=search_info))

            case "-ADD_RECORD-":
                match app.current_screen:
                    case Screen.CONTACT_SEARCH:
                        new_window = sg.Window("Add Contact", create_contact(), modal=True, finalize=True)
                        event, values = new_window.read()
                        new_window.close()

                        if event == "-CANCEL-":
                            continue

                        if not (values["-FIRST_NAME-"] and values["-LAST_NAME-"]):
                            sg.popup("First and last name are required to create a contact.")
                            continue

                        elif values["-PHONE_NUMBER-"]:
                            try:
                                values["-PHONE_NUMBER-"] = int(values["-PHONE_NUMBER-"])
                            except ValueError:
                                sg.popup("Invalid phone number! Phone number must be a continuous string of numbers.")
                                continue

                        db_values = {k.lower().replace("-", ""): v for k, v in values.items() if v}

                        contact = app.db.create_contact(**db_values)

                        swap_to_contact_viewer(app, contact=contact)

                    case Screen.ORG_SEARCH:
                        new_window = sg.Window("Add Organization", create_organization(), modal=True, finalize=True)
                        event, values = new_window.read()
                        new_window.close()

                        if event == "-CANCEL-":
                            continue

                        if not values["-NAME-"] or not values["-TYPE-"]:
                            sg.popup("Name and type are required to create an organization.")
                            continue

                        db_values = {k.lower().replace("-", ""): v for k, v in values.items() if v}

                        organization = app.db.create_organization(**db_values)

                        swap_to_org_viewer(app, org=organization)

                start_lazy()

            case "View":
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

            case "Add Contact":
                user_input = sg.popup_get_text(
                    "Enter the ID of the contact you would like to add.\n\nIf you don't know the ID, you can find it by"
                    "searching\nfor the contact, then alt-clicking on it and selecting \"Copy ID\".",
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

            case "Remove Contact":
                # Get contact selected in the table
                try:
                    contact_name = app.window["-ORG_CONTACT_INFO_TABLE-"].get()[values["-ORG_CONTACT_INFO_TABLE-"][0]][
                        0]
                except IndexError:
                    sg.popup("No contact selected!")
                    continue

                # Get organization name
                org_id = app.window["-ORG_VIEW-"].metadata

                # Remove contact from organization
                status = app.db.remove_contact_from_org(contact_name, org_id)

                if not status:
                    sg.popup("Error removing contact.")
                    continue

                swap_to_org_viewer(app, org_id=org_id, push=False)

            case "Add Organization":
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

            case "Remove Organization":
                # Get organization selected in the table
                try:
                    org_id = \
                        app.window["-CONTACT_ORGANIZATIONS_TABLE-"].get()[values["-CONTACT_ORGANIZATIONS_TABLE-"][0]][0]
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

            case "Copy ID":
                sg.clipboard_set(app.last_selected_id)

            case "Change Title":
                # Triggered when a user tries to change the title of a user
                # in an organization. This is only available in the organization
                # view.

                # Get the organization ID
                org_id = app.window["-ORG_VIEW-"].metadata

                # Get the contact ID
                try:
                    contact_id = app.window["-ORG_CONTACT_INFO_TABLE-"].get()[values["-ORG_CONTACT_INFO_TABLE-"][0]][0]
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

            case "Delete" | "-DELETE-" | "-CONTACT_DELETE-":
                confirmation = sg.popup_yes_no("Are you sure you want to delete this record?", title="Delete Record")

                if confirmation == "Yes":
                    match app.current_screen:
                        case Screen.ORG_VIEW:
                            org_id = app.window["-ORG_VIEW-"].metadata
                            app.db.delete_organization(org_id)
                            app.switch_to_last_screen()

                        case Screen.CONTACT_VIEW:
                            contact_id = app.window["-CONTACT_VIEW-"].metadata
                            app.db.delete_contact(contact_id)
                            app.switch_to_last_screen()

                        case Screen.ORG_SEARCH:
                            app.db.delete_organization(app.last_selected_id)
                            app.window["-ORG_TABLE-"].update(get_organization_table(app, values_only=True))

                        case Screen.CONTACT_SEARCH:
                            app.db.delete_contact(app.last_selected_id)
                            app.window["-CONTACT_TABLE-"].update(get_contact_table(app, values_only=True))

                    # Reload the table values after the record is deleted
                    start_lazy()

            case "Create Resource":
                input_window = sg.Window("Create Resource", [
                    [sg.Text("Resource Name:"), sg.Input(key="-RESOURCE_NAME-")],
                    [sg.Text("Resource Value:"), sg.Input(key="-RESOURCE_VALUE-")],
                    # TODO: Possibly create new Resource Viewer screen
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

            case "Delete Resource":

                if app.current_screen == Screen.ORG_VIEW:
                    try:
                        resource_id = app.window["-ORG_RESOURCES_TABLE-"].get()[values["-ORG_RESOURCES_TABLE-"][0]][0]
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

            case "Link Resource":
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

            case "Unlink Resource":
                # Get the resource ID
                if app.current_screen == Screen.ORG_VIEW:
                    try:
                        resource_id = app.window["-ORG_RESOURCES_TABLE-"].get()[values["-ORG_RESOURCES_TABLE-"][0]][0]
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

            case "Create Custom Field":
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

                # Get the ID of the record we're viewing
                if app.current_screen == Screen.ORG_VIEW:
                    org_id = app.window["-ORG_VIEW-"].metadata

                    field = app.db.create_custom_field(
                        name=values["-FIELD_NAME-"],
                        value=values["-FIELD_VALUE-"],
                        org=org_id
                    )

                    if not field:
                        sg.popup("Error creating custom field.\nPerhaps you used the same name as an existing field?")
                        continue

                    swap_to_org_viewer(app, org_id=org_id, push=False)

                elif app.current_screen == Screen.CONTACT_VIEW:
                    contact_id = app.window["-CONTACT_VIEW-"].metadata

                    field = app.db.create_custom_field(
                        name=values["-FIELD_NAME-"],
                        value=values["-FIELD_VALUE-"],
                        contact=contact_id
                    )

                    if not field:
                        sg.popup("Error creating custom field.\nPerhaps you used the same name as an existing field?")
                        continue

                    swap_to_contact_viewer(app, contact_id=contact_id, push=False)

            case "Edit Custom Field":
                # Get the ID of the record we're viewing
                if app.current_screen == Screen.ORG_VIEW:
                    org_id = app.window["-ORG_VIEW-"].metadata

                    try:
                        field_name = app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[values["-ORG_CUSTOM_FIELDS_TABLE-"][0]][0]
                        field_value = app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[values["-ORG_CUSTOM_FIELDS_TABLE-"][0]][1]
                    except IndexError:
                        continue

                elif app.current_screen == Screen.CONTACT_VIEW:
                    contact_id = app.window["-CONTACT_VIEW-"].metadata

                    try:
                        field_name = app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]][0]
                        field_value = app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]][1]
                    except IndexError:
                        continue

                # Create a new window to get the field name and value
                input_window = sg.Window("Edit Custom Field", [
                    [sg.Text("Field Name:"), sg.Input(
                        key="-FIELD_NAME-", default_text=field_name, disabled=True, tooltip="Field names cannot be "
                                                                                            "edited. Consider "
                                                                                            "deleting the field and "
                                                                                            "creating a new one "
                                                                                            "instead.")],
                    [sg.Text("Field Value:"), sg.Input(key="-FIELD_VALUE-", default_text=field_value)],
                    [sg.Button("Edit"), sg.Button("Cancel")]
                ], finalize=True, modal=True)

                # Read the window and close it
                event, values = input_window.read()
                input_window.close()

                # Check if the user clicked cancel
                if event == "Cancel" or event == sg.WIN_CLOSED:
                    continue

                # Check if the user entered a name and value
                if not values["-FIELD_VALUE-"]:
                    sg.popup("A field value is required! Consider deleting the record instead.")
                    continue

                # Reload the table values
                if app.current_screen == Screen.ORG_VIEW:
                    # Update the field
                    app.db.update_custom_field(
                        org=org_id,
                        name=values["-FIELD_NAME-"],
                        value=values["-FIELD_VALUE-"]
                    )
                    swap_to_org_viewer(app, org_id=org_id, push=False)

                elif app.current_screen == Screen.CONTACT_VIEW:
                    # Update the field
                    app.db.update_custom_field(
                        contact=contact_id,
                        name=values["-FIELD_NAME-"],
                        value=values["-FIELD_VALUE-"]
                    )
                    swap_to_contact_viewer(app, contact_id=contact_id, push=False)

            case "Delete Custom Field":
                # Get the ID of the record we're viewing
                if app.current_screen == Screen.ORG_VIEW:
                    org_id = app.window["-ORG_VIEW-"].metadata

                    try:
                        field_name = app.window["-ORG_CUSTOM_FIELDS_TABLE-"].get()[values["-ORG_CUSTOM_FIELDS_TABLE-"][0]][0]
                    except IndexError:
                        continue

                elif app.current_screen == Screen.CONTACT_VIEW:
                    contact_id = app.window["-CONTACT_VIEW-"].metadata

                    try:
                        field_name = app.window["-CONTACT_CUSTOM_FIELDS_TABLE-"].get()[values["-CONTACT_CUSTOM_FIELDS_TABLE-"][0]][0]
                    except IndexError:
                        continue

                confirmation = sg.popup_yes_no(
                    "Are you sure you want to delete this field?\nThis will remove the field for all other "
                    "records, too.",
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

            case "Change Name":
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
                        name = app.window["-CONTACT_NAME-"].get()
                    except IndexError:
                        continue

                    layout = [
                        [sg.Text("New First Name:"), sg.Input(key="-FIRST_NAME-", default_text=contact.first_name)],
                        [sg.Text("New Last Name:"), sg.Input(key="-LAST_NAME-", default_text=contact.last_name)],
                        [sg.Button("Change"), sg.Button("Cancel")]
                    ]

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
                    confirmation = sg.popup_yes_no("Making a name too long may cause issues with the UI. Are you sure you want to continue?")

                    if confirmation == "No" or confirmation == sg.WIN_CLOSED:
                        continue

                if app.current_screen == Screen.ORG_VIEW:
                    app.db.update_organization(org_id, name=new_org_name)
                    swap_to_org_viewer(app, org_id=org_id, push=False)

                elif app.current_screen == Screen.CONTACT_VIEW:
                    app.db.update_contact(contact_id, first_name=new_first_name, last_name=new_last_name)
                    swap_to_contact_viewer(app, contact_id=contact_id, push=False)

                start_lazy()

            case _:
                continue

print("Hello, world!")
