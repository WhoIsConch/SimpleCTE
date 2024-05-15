import PySimpleGUI as sg

__all__ = ("EVENT_MAP",)

def display_code(app):
    sg.execute_editor("simplecte/process/events/debug.py")

EVENT_MAP = {
    "View Code": display_code
}