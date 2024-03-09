import PySimpleGUI as sg
from layouts import get_help_layout, get_help_text
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from process.app import App

__all__ = ("help_manager",)


def help_manager(app: "App", key: str):
    layout = get_help_layout()

    window = sg.Window(
        "Help",
        layout,
        finalize=True,
        modal=True,
    )

    window["-HELP_TEXT-"].update(get_help_text(key))

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

    window.close()
