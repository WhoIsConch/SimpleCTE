import PySimpleGUI as sg

__all__ = ("get_first_time_layout",)

_welcome_text = """• You can change the app's theme and open a different database at any time in the `settings` menu.

• Alt-click menus are available on most components for more options, including the `back` button.

• You can back up your database in the `settings` menu, and export your data to different file types in the `export` menu.

• More help is always available by alt-clicking a component and selecting `help`, or selecting the `help` button at the top of the screen to open a web page with more information.
"""


def get_first_time_layout() -> list[list[sg.Element]]:
    """
    Return the layout that shows when it is a user's first time
    opening the app. This layout welcomes the user and offers
    tips on how to use the program.
    """
    return [
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Text(
                            "Welcome to SimpleCTE!",
                            font=("Arial", 15),
                            justification="center",
                        ),
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text(
                            "It looks like this is your first time using SimpleCTE. "
                            "Here are a few things to know:"
                        )
                    ],
                    [sg.Multiline(_welcome_text, size=(60, 10), disabled=True)],
                    [sg.Button("Got it!", key="-FIRST_TIME_CLOSE-")],
                ],
            )
        ]
    ]
