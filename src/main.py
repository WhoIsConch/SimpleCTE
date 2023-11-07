import json
import logging
from enum import Enum
from database import construct_database
import PySimpleGUI as sg
from layouts import (
    login_constructor,
    main_constructor
    )

class DBStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    LOGIN_REQUIRED = 3


class App:
    def __init__(self):
        self.db = None
        self.db_status = DBStatus.DISCONNECTED
        self.logger = logging.getLogger("app") 

        self.logger.info("Loading database settings...")

        self.settings = self.load_settings()

        if self.settings["database"]["system"] == "sqlite" and self.settings["database"]["location"] == "local":
            self.logger.info("Constructing SQLite database...")
            self.db = construct_database(
                "sqlite",
                self.settings["database"]["path"]
            )
            self.db_status = DBStatus.CONNECTED
        elif self.settings["database"]["system"] == "sqlite" and self.settings["database"]["location"] == "remote":
            self.logger.info("Constructing remote SQLite database...")
            self.db = construct_database(
                "sqlite",
                self.settings["database"]["path"],
                server_address=self.settings["database"]["address"],
                server_port=self.settings["database"]["port"],
                username=self.settings["database"]["username"]
            )
            self.db_status = DBStatus.CONNECTED
        elif self.settings["database"]["system"] == "postgres" or self.settings["database"]["system"] == "mysql":
            self.logger.info("Constructing remote database...")
            try:
                self.db = construct_database(
                    self.settings["database"]["system"],
                    self.settings["database"]["name"],
                    server_address=self.settings["database"]["address"],
                    server_port=self.settings["database"]["port"],
                    username=self.settings["database"]["username"],
                    password=self.settings["database"]["password"]
                )
            except Exception:
                self.db_status = DBStatus.LOGIN_REQUIRED
        else:
            self.logger.error("Invalid database system!")
            raise ValueError("Invalid database system!")

    def load_settings(self) -> dict:
        self.logger.info("Loading settings...")
        try:
            with open("data/settings.json", "r") as f:
                settings: dict = json.load(f) # Load our settings file

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
                "theme": "dark"
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

        with open("data/settings.json", "w") as f:
            json.dump(settings or self.settings, f, indent=4)
        
        self.logger.info("Settings saved!")

app = App()

sg.theme(app.settings["theme"])

if app.db_status == DBStatus.LOGIN_REQUIRED:
    window = sg.Window("Log In", login_constructor())

else:
    window = sg.Window("Welcome", main_constructor())

while True:
    event, values = window.read()

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




print("Hello, world!")