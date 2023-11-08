import json
import logging
from database import db
import PySimpleGUI as sg
from layouts import login_constructor, search_constructor
from enums import DBStatus, Screen, AppStatus
import os


class App:
    def __init__(self):
        self.db = db
        self.logger = logging.getLogger("app")
        self.screen = Screen.LOGIN
        self.window = None
        self.status = AppStatus.BUSY

        self.logger.info("Loading database settings...")

        self.settings = self.load_settings()

        if (
            self.settings["database"]["system"] == "sqlite"
            and self.settings["database"]["location"] == "local"
        ):
            self.logger.info("Constructing SQLite database...")
            self.db.construct_database("sqlite", self.settings["database"]["path"])
            self.screen = Screen.ORG_SEARCH

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
            self.screen = Screen.ORG_SEARCH

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
                self.screen = Screen.LOGIN

        else:
            self.logger.error("Invalid database system!")
            raise ValueError("Invalid database system!")

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

sg.theme(app.settings["theme"])

if app.screen == Screen.LOGIN:
    app.window = sg.Window("Log In", login_constructor())

else:
    app.window = sg.Window("Welcome", search_constructor(app), finalize=True)

app.window.Font = ("Arial", 12)

while True:
    app.status = AppStatus.READY
    event, values = app.window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    print(event, values)

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
                app.screen = Screen.ORG_SEARCH

            elif values["-SEARCHTYPE-"] == "Contacts":
                app.window["-ORG_SCREEN-"].update(visible=False)
                app.window["-CONTACT_SCREEN-"].update(visible=True)

                app.screen = Screen.CONTACT_SEARCH


print("Hello, world!")
