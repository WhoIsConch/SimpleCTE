import logging
from typing import Callable
from datetime import datetime
import PySimpleGUI as sg
import os
import sys

from utils.enums import Screen, AppStatus, DBStatus
from process.stack import Stack
from process.settings import Settings
from sqlalchemy import create_engine
from layouts import (
    get_search_layout, 
    get_contact_view_layout, 
    get_org_view_layout, 
    get_resource_view_layout, 
    get_login_layout,
)
from ui_management import swap_to_org_viewer, swap_to_contact_viewer, swap_to_resource_viewer
from database import get_table_values, Contact, Organization, Resource


__all__ = (
    "App",
)


class App:
    """
    The App class is the main class that runs the application.
    It is responsible for managing most functions of the application
    and keeping essential information in a central location.
    """
    ICON_PATH = os.path.join(os.path.dirname(__file__), '../data/simplecte.ico')

    def __init__(self):
        self.logger = logging.getLogger("app")
        self.stack = Stack()
        self.window: sg.Window | None = None
        self.status = AppStatus.BUSY
        self.last_clicked_table_time = None
        self.last_selected_id: int | None = None
        self.logger.info("Loading database settings...")
        self.settings: Settings = Settings("data/settings.json")
        self.settings.load_settings()

        self.engine = create_engine(self.settings.database_path)

        # Configure GUI-related settings
        sg.set_global_icon(self.ICON_PATH)
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

    def update_exit_menu(self):
        """
        Will update the right-click menu of the exit button to show all
        the screens in the stack.
        """
        menu = [
                "",
                # Subscripts remove the last item in the list and reverse it
                [screen + f"::{index}-STACK" for index, screen in enumerate(self.stack.generate_previews())][:-1][::-1]
            ]
        self.window["-EXIT_1-"].set_right_click_menu(menu)
        self.window["-EXIT_1_CONTACT-"].set_right_click_menu(menu)

    def jump_to_screen(self, event: str, data: dict):
        """
        Jump to a screen in the stack.
        """
        index = int(event.split("::")[1].split("-")[0])
        self.stack.jump_to(index + 1)
        self.switch_to_last_screen()

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

        self.update_exit_menu()

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
            record_id = self.stack.peek()[1].id
            screen = self.current_screen.value

            self.window[screen].update(visible=True)

            if self.current_screen == Screen.ORG_VIEW:
                swap_to_org_viewer(self, org_id=record_id, push=False)

            elif self.current_screen == Screen.CONTACT_VIEW:
                swap_to_contact_viewer(self, contact_id=record_id, push=False)

            elif self.current_screen == Screen.RESOURCE_VIEW:
                swap_to_resource_viewer(self, resource_id=record_id, push=False)

        self.update_exit_menu()

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
                get_table_values(self, Contact, amount=None, search_info=search_info,
                                         descending=descending),
                get_table_values(self, Organization, amount=None, search_info=search_info,
                                     descending=descending)
            ]
            # time.sleep(3)

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
            self.window["-CONTACT_TABLE-"].update(get_table_values(self, Contact))
            self.window["-ORG_TABLE-"].update(get_table_values(self, Organization))

    def restart(self):
        """
        Restart the app. Due to database stuff, this will need
        to restart the entire program and re-run the file.
        """
        self.logger.info("Restarting...")
        self.window.close()
        os.execv(sys.executable, ["python"] + sys.argv)
