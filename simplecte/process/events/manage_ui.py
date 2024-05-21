from typing import TYPE_CHECKING
from ui_management import (
    swap_to_org_viewer,
    swap_to_contact_viewer,
)
from database import get_table_values, Contact, Organization
from utils.enums import Screen
import PySimpleGUI as sg

if TYPE_CHECKING:
    from process.app import App

__all__ = ("EVENT_MAP",)


def _view(app: "App", values: dict):
    method = None

    match app.current_screen:
        case Screen.ORG_SEARCH:
            if not values["-ORG_TABLE-"]:
                return

            method = swap_to_org_viewer

        case Screen.CONTACT_VIEW:
            if not values["-CONTACT_ORGANIZATIONS_TABLE-"]:
                return

            method = swap_to_org_viewer

        case Screen.CONTACT_SEARCH:
            if not values["-CONTACT_TABLE-"]:
                return

            method = swap_to_contact_viewer

        case Screen.ORG_VIEW:
            if not values["-ORG_CONTACT_INFO_TABLE-"]:
                return

            method = swap_to_contact_viewer

    if app.last_selected_id and method:
        method(app, app.last_selected_id)


def _view_resource_org(app: "App", values: dict):
    if not values["-RESOURCE_ORGANIZATIONS_TABLE-"]:
        return

    if app.last_selected_id:
        swap_to_org_viewer(app, org_id=app.last_selected_id)


def _view_resource_contact(app: "App", values: dict):
    if not values["-RESOURCE_CONTACTS_TABLE-"]:
        return

    if app.last_selected_id:
        swap_to_contact_viewer(app, contact_id=app.last_selected_id)


def _view_full_value(app: "App"):
    resource = app.db.get_resource(app.window["-RESOURCE_VIEW-"].metadata)

    layout = [
        [sg.Text("Full Resource Value:")],
        [sg.Multiline(resource.value, size=(30, 10), disabled=True)],
        [sg.Button("Close")],
    ]

    view_window = sg.Window("Full Resource Value", layout, finalize=True, modal=True)

    _ = view_window.read()
    view_window.close()


def _reset_search(app: "App"):
    # Reset the search parameters
    app.window["-SEARCH_QUERY-"].update("")
    app.window["-SEARCH_FIELDS-"].update("")
    app.window["-SORT_TYPE-"].update("")

    if app.current_screen == Screen.ORG_SEARCH:
        app.window["-ORG_TABLE-"].update(get_table_values(app, Organization))

    elif app.current_screen == Screen.CONTACT_SEARCH:
        app.window["-CONTACT_TABLE-"].update(get_table_values(app, Contact))

    app.lazy_load_table_values()


def _execute_search(app: "App", values: dict):
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

    app.lazy_load_table_values(search_info, descending=values["-SORT_DESCENDING-"])


EVENT_MAP = {
    "View": _view,
    "View::RESOURCE_ORG": _view_resource_org,
    "View::RESOURCE_CONTACT": _view_resource_contact,
    "View Full Value": _view_full_value,
    "-RESET_BUTTON-": _reset_search,
    "-SEARCH_BUTTON-": _execute_search,
}
