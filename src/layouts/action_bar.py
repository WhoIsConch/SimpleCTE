import PySimpleGUI as sg
from src.utils.enums import Screen

__all__ = (
    "get_action_bar",
)


def get_action_bar(screen: Screen) -> list:
    if screen == Screen.ORG_SEARCH or screen == Screen.CONTACT_SEARCH:
        return [
            [
                sg.Button("Export by Filter", k="-EXPORT_FILTER-"),
                sg.Button("Export All", k="-EXPORT_ALL-"),
                sg.Button("Settings", k="-SETTINGS-"),
                sg.Button("Backup", k="-BACKUP-"),
                sg.Button("Help", k="-HELP-"),
                sg.Button("Logout", k="-LOGOUT-"),
                sg.Button("Add Record", k="-ADD_RECORD-"),
            ]
        ]
    else:
        return [
            [
                sg.Button("Export", k="-EXPORT-"),
                sg.Button("Settings", k="-SETTINGS-"),
                sg.Button("Backup", k="-BACKUP-"),
                sg.Button("Help", k="-HELP-"),
                sg.Button("Logout", k="-LOGOUT-"),
                sg.Button("Add Record", k="-ADD_RECORD-"),
            ]
        ]
