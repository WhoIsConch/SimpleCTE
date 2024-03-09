import PySimpleGUI as sg
from utils.enums import Screen

__all__ = ("get_action_bar",)


def get_action_bar(screen: Screen) -> list:
    if screen == Screen.ORG_SEARCH or screen == Screen.CONTACT_SEARCH:
        return [
            [
                sg.Button("Quit", k="-LOGOUT-", tooltip="Log out of the database"),
                sg.Button(
                    "Export by Filter",
                    k="-EXPORT_FILTER-",
                    tooltip="Export data if it matches the selected " "filter",
                ),
                sg.Button("Export All", k="-EXPORT_ALL-", tooltip="Export all data"),
                sg.Button("Settings", k="-SETTINGS-"),
                sg.Button("Backup", k="-BACKUP-", tooltip="Back up your data"),
                sg.Button(
                    "Add Record", k="-ADD_RECORD-", tooltip="Create a new record"
                ),
                sg.Button("Help", k="-HELP-"),
            ]
        ]
    else:
        layout = [
            [
                sg.Button("Quit", k="-LOGOUT-", tooltip="Log out of the database"),
                sg.Button("Export", k="-EXPORT-", tooltip="Export database data"),
                sg.Button("Settings", k="-SETTINGS-"),
                sg.Button("Backup", k="-BACKUP-", tooltip="Back up your data"),
                sg.Button(
                    "Add Record", k="-ADD_RECORD-", tooltip="Create a new record"
                ),
                sg.Button("Help", k="-HELP-"),
            ]
        ]

        if screen == Screen.RESOURCE_VIEW:
            layout[0].pop(4)

        return layout
