import PySimpleGUI as sg
from typing import TYPE_CHECKING
from layouts import get_create_contact_layout, get_create_org_layout
from ui_management import swap_to_contact_viewer, swap_to_org_viewer
from utils.enums import Screen

if TYPE_CHECKING:
    from process.app import App

__all__ = ("add_record_handler",)


def add_record_handler(app: "App"):
    if app.current_screen in [Screen.CONTACT_SEARCH, Screen.CONTACT_VIEW]:
        window = sg.Window(
            "Add Contact", get_create_contact_layout(), modal=True, finalize=True
        )

        while True:
            event, values = window.read()

            if event == "-CANCEL-" or event == sg.WIN_CLOSED:
                window.close()
                return

            elif not (values["-FIRST_NAME-"] and values["-LAST_NAME-"]):
                sg.popup(
                    "First and last name are required to create a contact.",
                    title="Missing required fields.",
                )
                continue

            elif values["-PHONE_NUMBER-"]:
                try:
                    values["-PHONE_NUMBER-"] = int(values["-PHONE_NUMBER-"])
                except ValueError:
                    sg.popup(
                        "Invalid phone number! Phone number must be a continuous string of numbers.",
                        title="Invalid phone number.",
                    )
                    continue

            break

        db_values = {k.lower().replace("-", ""): v for k, v in values.items() if v}
        contact = app.db.create_contact(**db_values)

        swap_to_contact_viewer(app, contact=contact)
        window.close()

    elif app.current_screen in [Screen.ORG_SEARCH, Screen.ORG_VIEW]:
        window = sg.Window(
            "Add Organization", get_create_org_layout(), modal=True, finalize=True
        )

        while True:
            event, values = window.read()

            if event == "-CANCEL-" or event == sg.WIN_CLOSED:
                window.close()
                return

            elif not values["-NAME-"] or not values["-TYPE-"]:
                sg.popup(
                    "Name and type are required to create an organization.",
                    title="Missing required fields.",
                )
                continue

            elif values["-PHONE_NUMBER-"]:
                try:
                    values["-PHONE_NUMBER-"] = int(values["-PHONE_NUMBER-"])
                except ValueError:
                    sg.popup(
                        "Invalid phone number! Phone number must be a continuous string of numbers.",
                        title="Invalid phone number.",
                    )
                    continue

            break

        db_values = {k.lower().replace("-", ""): v for k, v in values.items() if v}
        organization = app.db.create_organization(**db_values)

        swap_to_org_viewer(app, org=organization)
        window.close()

    else:
        return

    app.lazy_load_table_values()
