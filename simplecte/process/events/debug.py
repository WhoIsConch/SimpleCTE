import PySimpleGUI as sg

__all__ = ("handle_debug",)


def handle_debug(event: str):
    # Parse out the "function call"
    path, line = event.split("(")[1].strip(")").split(",")

    sg.execute_editor(path, line)
