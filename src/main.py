from typing import Callable
import json
import logging
from database import db
import PySimpleGUI as sg
from layouts import (
    login_constructor,
    search_constructor,
    empty_org_view_constructor,
    empty_contact_view_constructor,
    swap_to_org_viewer,
    swap_to_contact_viewer,
)
from enums import DBStatus, Screen, AppStatus
import os
from datetime import datetime


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
        self.last_clicked_index = None
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
    
    def switch_screen(self, screen: Screen, data = None, push: bool = True) -> None:
        if push:
            self.stack.push(screen, data)

        self.window["-SEARCH_SCREEN-"].update(visible=False)
        self.window["-ORG_VIEW-"].update(visible=False)
        self.window["-CONTACT_VIEW-"].update(visible=False)
        self.window["-ORG_SCREEN-"].update(visible=False)
        self.window["-CONTACT_SCREEN-"].update(visible=False)

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

        self.window["-SEARCH_SCREEN-"].update(visible=False)
        self.window["-ORG_VIEW-"].update(visible=False)
        self.window["-CONTACT_VIEW-"].update(visible=False)
        self.window["-ORG_SCREEN-"].update(visible=False)
        self.window["-CONTACT_SCREEN-"].update(visible=False)

        if self.current_screen == Screen.ORG_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-ORG_SCREEN-"].update(visible=True)
        
        elif self.current_screen == Screen.CONTACT_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-CONTACT_SCREEN-"].update(visible=True)
        
        elif self.current_screen == Screen.ORG_VIEW:
            self.window["-ORG_VIEW-"].update(visible=True)
            swap_to_org_viewer(self, org_name=self.stack.peek()[1])
        
        elif self.current_screen == Screen.CONTACT_VIEW:
            self.window["-CONTACT_VIEW-"].update(visible=True)
            swap_to_contact_viewer(self, contact_name=self.stack.peek()[1])


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

    def save_settings(self, settings: dict | None) -> None:
        self.logger.info("Saving settings...")

        with open(
            os.path.dirname(os.path.realpath(__file__)) + "\\data\\settings.json", "w"
        ) as f:
            json.dump(settings or self.settings, f, indent=4)

        self.logger.info("Settings saved!")

app = App()

def check_doubleclick(callback: Callable, args: set, check: Callable | None = None) -> None:
    if (app.last_clicked_table_time is not None) and (
        (datetime.now() - app.last_clicked_table_time).total_seconds() < 0.5
    ):
        if not (check and check()): 
            callback(*args)

        app.last_clicked_table_time = None
    else:
        app.last_clicked_table_time = datetime.now()


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

while True:
    app.status = AppStatus.READY
    event, values = app.window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    print(event, values, "\n")

    if isinstance(event, tuple) and event[2][0] is not None:
        def doubleclick_check():
            return app.last_clicked_index != event[2][0] and app.last_clicked_index is not None

        match event[0]:
            case "-ORG_TABLE-" | "-CONTACT_ORGANIZATIONS_TABLE-":
                check_doubleclick(
                    swap_to_org_viewer, 
                    check=doubleclick_check,
                    args=(app, event[2])
                    )
                
            case "-CONTACT_TABLE-" | "-ORG_CONTACT_INFO_TABLE-":
                check_doubleclick(
                    swap_to_contact_viewer, 
                    check=doubleclick_check,
                    args=(app, event[2])
                    )
        
    elif event == "View":
        value = None
        method = None

        match app.current_screen:
            case Screen.ORG_SEARCH:
                if not values["-ORG_TABLE-"]:
                    continue

                value = values["-ORG_TABLE-"][0]
                method = swap_to_org_viewer

            case Screen.CONTACT_VIEW:
                if not values["-CONTACT_ORGANIZATIONS_TABLE-"]:
                    continue

                value = values["-CONTACT_ORGANIZATIONS_TABLE-"][0]
                method = swap_to_org_viewer
            
            case Screen.CONTACT_SEARCH:
                if not values["-CONTACT_TABLE-"]:
                    continue

                value = values["-CONTACT_TABLE-"][0]
                method = swap_to_contact_viewer
            
            case Screen.ORG_VIEW:
                if not values["-ORG_CONTACT_INFO_TABLE-"]:
                    continue

                value = values["-ORG_CONTACT_INFO_TABLE-"][0]
                method = swap_to_contact_viewer

        if value is not None and method is not None:
            method(app, (value, 0))

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
                    "sort": values["-SEARCH_SORT-"],
                }

print("Hello, world!")
