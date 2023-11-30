import logging
from typing import Callable
from datetime import datetime
import PySimpleGUI as sg
import os
import sys

from ..utils.enums import Screen, AppStatus, DBStatus
from ..process.stack import Stack
from ..process.settings import Settings
from ..database.database import db, get_org_table_values, get_contact_table_values
from ..layouts import get_search_layout, get_contact_view_layout, get_org_view_layout, get_resource_view_layout, \
    get_login_layout
from ..ui_management.viewers import swap_to_org_viewer, swap_to_contact_viewer, swap_to_resource_viewer


class App:
    """
    The App class is the main class that runs the application.
    It is responsible for managing most functions of the application
    and keeping essential information in a central location.
    """

    def __init__(self):
        self.db = db
        self.db.app = self
        self.logger = logging.getLogger("app")
        self.stack = Stack()
        self.window: sg.Window | None = None
        self.status = AppStatus.BUSY
        self.last_clicked_table_time = None
        self.last_selected_id = None
        self.logger.info("Loading database settings...")
        self.settings: Settings = Settings("data/settings.json")
        self.settings.load_settings()

        # Decide which database configuration to use
        if (
                self.settings.database_system == "sqlite"
                and self.settings.database_location == "local"
        ):
            self.logger.info("Constructing SQLite database...")
            self.db.construct_database("sqlite", self.settings.absolute_database_path)
            self.stack.push(Screen.ORG_SEARCH)

        elif (
                self.settings.database_system == "sqlite"
                and self.settings.database_location == "remote"
        ):
            self.logger.info("Constructing remote SQLite database...")
            self.db.construct_database(
                "sqlite",
                self.settings.absolute_database_path,
                server_address=self.settings.database_address,
                server_port=self.settings.database_port,
                username=self.settings.database_username,
            )
            self.stack.push(Screen.ORG_SEARCH)

        elif (
                self.settings.database_system == "postgres"
                or self.settings.database_system == "mysql"
        ):
            self.logger.info("Constructing remote database...")
            try:
                self.db.construct_database(
                    self.settings.database_system,
                    self.settings.database_name,
                    server_address=self.settings.database_address,
                    server_port=self.settings.database_port,
                    username=self.settings.database_username,
                    password=self.settings.database_password,
                )
            except Exception:
                self.db.status = (
                    DBStatus.LOGIN_REQUIRED
                )
                self.stack.push(Screen.LOGIN)

        else:
            self.logger.error("Invalid database system!")
            raise ValueError("Invalid database system!")

        # Configure GUI-related settings
        sg.theme(self.settings.theme)

        self.show_start_screen()
        self.lazy_load_table_values()
        self.window.Font = ("Arial", 12)

    @property
    def current_screen(self) -> Screen:
        """
        Get the last screen in the stack.
        """
        return self.stack.peek()[0]

    @property
    def last_screen(self) -> Screen:
        """
        Get the second-to-last screen in the stack.
        """
        return self.stack.stack[-2][0]

    def hide_major_screens(self):
        """
        Hide all major screens.
        Major screens include the search screens, the org/contact view screens, and the create screens.
        """
        screens = ["-SEARCH_SCREEN-", "-ORG_VIEW-", "-CONTACT_VIEW-", "-ORG_SCREEN-", "-CONTACT_SCREEN-",
                   "-RESOURCE_VIEW-"]

        for screen in screens:
            self.window[screen].update(visible=False)

    def switch_screen(self, screen: Screen, data=None, push: bool = True) -> None:
        """
        Switch to a new screen.
        """
        self.last_selected_id = None

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

        elif screen == Screen.RESOURCE_VIEW:
            self.window["-RESOURCE_VIEW-"].update(visible=True)

    def switch_to_last_screen(self) -> None:
        """
        Switch the app back to the second-to-last screen in the stack.
        """
        self.stack.pop()

        self.hide_major_screens()

        if self.current_screen == Screen.ORG_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-ORG_SCREEN-"].update(visible=True)

        elif self.current_screen == Screen.CONTACT_SEARCH:
            self.window["-SEARCH_SCREEN-"].update(visible=True)
            self.window["-CONTACT_SCREEN-"].update(visible=True)

        else:
            record_id = self.stack.peek()[1]
            screen = self.current_screen.value

            self.window[screen].update(visible=True)

            if self.current_screen == Screen.ORG_VIEW:
                swap_to_org_viewer(self, org_id=record_id, push=False)

            elif self.current_screen == Screen.CONTACT_VIEW:
                swap_to_contact_viewer(self, contact_id=record_id, push=False)

            elif self.current_screen == Screen.RESOURCE_VIEW:
                swap_to_resource_viewer(self, resource_id=record_id, push=False)

    def check_doubleclick(self, callback: Callable, args: tuple, check: "Callable | None" = None) -> None:
        """
        Check if a table was double-clicked. If it was, run the callback.
        """
        if (self.last_clicked_table_time is not None) and (
                (datetime.now() - self.last_clicked_table_time).total_seconds() < 0.5
        ):
            if check and check():
                callback(*args)

            self.last_clicked_table_time = None
        else:
            self.last_clicked_table_time = datetime.now()

    def lazy_load_table_values(self, search_info: dict = None, descending: bool = False):
        """
        Load the values for the search tables, in the case there is a
        lot of info in the database to decrease load times.
        """

        # Use empty lists to retrieve the information from the threads.
        def get_values():
            values = [
                get_contact_table_values(self, paginated=False, search_info=search_info,
                                         descending=descending),
                get_org_table_values(self, paginated=False, search_info=search_info,
                                     descending=descending)
            ]

            return values

        self.window.start_thread(
            get_values,
            end_key="-UPDATE_TABLES-"
        )

    def show_start_screen(self):
        """
        Decide which screen to start the app on.
        """
        if self.current_screen == Screen.LOGIN:
            self.window = sg.Window("Log In to your SimpleCTE Database", get_login_layout())

        else:
            self.window = sg.Window(
                "SimpleCTE",
                finalize=True,
                layout=[
                    [
                        sg.Column(
                            layout=get_search_layout(self.current_screen),
                            key="-SEARCH_SCREEN-",
                            visible=True,
                        ),
                        sg.Column(
                            layout=get_org_view_layout(),
                            key="-ORG_VIEW-",
                            visible=False,
                        ),
                        sg.Column(
                            layout=get_contact_view_layout(),
                            key="-CONTACT_VIEW-",
                            visible=False,
                        ),
                        sg.Column(
                            layout=get_resource_view_layout(),
                            key="-RESOURCE_VIEW-",
                            visible=False,
                        )
                    ]
                ],
            )

    def restart(self):
        """
        Restart the app. Due to database stuff, this will need
        to restart the entire program and re-run the file.
        """
        self.logger.info("Restarting...")
        self.window.close()
        os.execv(sys.executable, ["python"] + sys.argv)
