import PySimpleGUI as sg
from src.utils.enums import Screen
from ..layouts import get_action_bar

__all__ = (
    "get_search_layout",
)


def get_search_layout(
        screen: Screen,
) -> list:
    fields = [
        "Name",
        "Status",
        "Primary Phone",
        "Address",
        "Custom Field Name",
        "Custom Field Value",
    ]
    filters = ["Status", "Alphabetical", "Type", "Associated with resource..."]

    layout = [
        [
            sg.Column(
                expand_x=True,
                element_justification="left",
                background_color=sg.theme_progress_bar_color()[1],
                pad=((0, 0), (0, 10)),
                layout=[
                    [
                        sg.Column(
                            pad=5,
                            element_justification="left",
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=get_action_bar(screen),
                        ),
                        sg.Push(background_color=sg.theme_progress_bar_color()[1]),
                        sg.Column(
                            element_justification="right",
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "View: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                        pad=((0, 0), (0, 0)),
                                    ),
                                    sg.Combo(
                                        ["Contacts", "Organizations"],
                                        k="-SEARCHTYPE-",
                                        default_value="Contacts"
                                        if screen == Screen.CONTACT_SEARCH
                                        else "Organizations",
                                        enable_events=True,
                                        pad=((0, 5), (0, 0)),
                                    ),
                                ]
                            ],
                        ),
                    ]
                ],
            )
        ],
        [
            sg.Column(
                expand_x=True,
                pad=((0, 0), (0, 10)),
                layout=[
                    [
                        sg.Button("Search", k="-SEARCH_BUTTON-"),
                        sg.Text("Search Query:"),
                        sg.Input(k="-SEARCH_QUERY-", expand_x=True),
                    ],
                    [
                        sg.Text("Search Fields:"),
                        sg.Combo(fields, k="-SEARCH_FIELDS-", expand_x=True),
                        sg.Text("Search Filters:"),
                        sg.Combo(filters, k="-SORT_TYPE-", expand_x=True),
                    ],
                ],
            )
        ],
        [
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                expand_y=True,
                element_justification="center",
                key="-ORG_SCREEN-",
                visible=screen == Screen.ORG_SEARCH,
                layout=[
                    [
                        sg.Text(
                            "Organization Search",
                            background_color=sg.theme_progress_bar_color()[1],
                            font=("Arial", 20),
                        )
                    ],
                    [
                        sg.Table(
                            headings=["ID", "Organization Name", "Type", "Primary Contact", "Status"],
                            values=[],
                            visible_column_map=[False, True, True, True, True],
                            expand_x=True,
                            font=("Arial", 15),
                            right_click_menu=[
                                "&Right",
                                ["View", "Copy ID", "Delete"],
                            ],
                            right_click_selects=True,
                            enable_click_events=True,
                            k="-ORG_TABLE-",
                            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                            row_height=40,
                            alternating_row_color=sg.theme_progress_bar_color()[1],
                            justification="center",
                            num_rows=5,
                        ),
                    ],
                ],
            ),
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                expand_y=True,
                element_justification="center",
                key="-CONTACT_SCREEN-",
                visible=screen == Screen.CONTACT_SEARCH,
                layout=[
                    [
                        sg.Text(
                            "Contact Search",
                            background_color=sg.theme_progress_bar_color()[1],
                            font=("Arial", 20),
                        ),
                    ],
                    [
                        sg.Table(
                            headings=["ID", "Name", "Primary Organization", "Primary Phone"],
                            values=[],
                            visible_column_map=[False, True, True, True],
                            expand_x=True,
                            font=("Arial", 15),
                            right_click_menu=[
                                "&Right",
                                ["View", "Copy ID", "Delete"],
                            ],
                            right_click_selects=True,
                            k="-CONTACT_TABLE-",
                            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                            row_height=40,
                            alternating_row_color=sg.theme_progress_bar_color()[1],
                            justification="center",
                            enable_click_events=True,
                            num_rows=5,
                        ),
                    ],
                ],
            ),
        ],
    ]

    return layout
