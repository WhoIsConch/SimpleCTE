import PySimpleGUI as sg

from utils.enums import Screen
from layouts import get_action_bar

__all__ = (
    "get_contact_view_layout",
    "get_org_view_layout",
    "get_viewer_head",
    "get_resource_view_layout",
)


def get_viewer_head(contact: bool = False) -> list:
    viewer_head = [
        [
            sg.Column(
                layout=get_action_bar(Screen.ORG_VIEW),
                background_color=sg.theme_progress_bar_color()[1],
                element_justification="left",
                right_click_menu=["", ["Help::ACTION_BAR", "View Code"]],
            ),
            sg.Push(),
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                element_justification="right",
                layout=[
                    [
                        sg.Button(
                            "Delete",
                            k="-DELETE-" if not contact else "-DELETE_CONTACT-",
                        ),
                        sg.Button(
                            "Back", k="-EXIT-" if not contact else "-EXIT_CONTACT-"
                        ),
                    ]
                ],
            ),
        ],
        [
            sg.Column(
                expand_x=True,
                layout=[
                    [
                        sg.Button(
                            "Back",
                            k="-EXIT_1-" if not contact else "-EXIT_1_CONTACT-",
                            expand_y=True,
                            expand_x=True,
                            tooltip=" Go back to the previous screen. Alt-click to view all "
                            "screens you have recently viewed. ",
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            right_click_menu=["", ["Change Name", "Change Type"]]
                            if not contact
                            else ["", ["Change Name"]],
                            key="-NAME_COLUMN-",
                            layout=[
                                [
                                    sg.Text(
                                        "Name: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                        key="-NAME_TEXT-",
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-NAME-"
                                        if not contact
                                        else "-CONTACT_NAME-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            right_click_menu=["", ["Change Status"]],
                            layout=[
                                [
                                    sg.Text(
                                        "Status: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-STATUS-"
                                        if not contact
                                        else "-CONTACT_STATUS-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            right_click_menu=[
                                "",
                                [
                                    "Edit Phones",
                                    "View All Phones",
                                    "Code BTS::CODE(simplecte/process/events/edit_info.py,433)",
                                    "Code LYT::CODE(simplecte/layouts/viewer.py,111)",
                                ],
                            ],
                            layout=[
                                [
                                    sg.Text(
                                        "Primary Phone: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-PHONE-"
                                        if not contact
                                        else "-CONTACT_PHONE-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            right_click_menu=[
                                "",
                                [
                                    "Edit Addresses",
                                    "View All Addresses",
                                    "Code BTS::CODE(simplecte/process/events/edit_info.py,391)",
                                    "Code LYT::CODE(simplecte/layouts/viewer.py,138)",
                                ],
                            ],
                            layout=[
                                [
                                    sg.Text(
                                        "Address: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-ADDRESS-"
                                        if not contact
                                        else "-CONTACT_ADDRESS-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            background_color=sg.theme_progress_bar_color()[1],
                            right_click_menu=["", ["Edit Emails", "View All Emails"]],
                            layout=[
                                [
                                    sg.Text(
                                        "Primary Email: ",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-EMAIL-"
                                        if not contact
                                        else "-CONTACT_EMAIL-",
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    ),
                                ],
                            ],
                        ),
                    ]
                ],
            )
        ],
        [sg.Sizer(800, 0)],
    ]
    return viewer_head


def get_contact_view_layout():
    return [
        [
            sg.Column(
                expand_x=True,
                layout=get_viewer_head(True),
            )
        ],
        [
            sg.Column(
                expand_x=True,
                background_color=sg.theme_progress_bar_color()[1],
                right_click_menu=["", ["Help::CONTACT_VIEWER"]],
                layout=[
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Contact Info", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_INFO_TABLE-",
                                        headings=["Title", "Value"],
                                        right_click_menu=[
                                            "",
                                            [
                                                "View More::CONTACT_INFO",
                                                "Add::CONTACT_INFO",
                                                "Edit::CONTACT_INFO",
                                                "Delete::CONTACT_INFO",
                                                "Help::CONTACT_VIEWER",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Organizations", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_ORGANIZATIONS_TABLE-",
                                        headings=["ID", "Name", "Status"],
                                        visible_column_map=[False, True, True],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        enable_click_events=True,
                                        right_click_menu=[
                                            "&Right",
                                            [
                                                "View",
                                                "Copy ID",
                                                "Add Organization",
                                                "Remove Organization",
                                                "Help::CONTACT_VIEWER",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ],
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Associated Resources", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_RESOURCES_TABLE-",
                                        headings=["ID", "Name", "Value"],
                                        visible_column_map=[False, True, True],
                                        right_click_menu=[
                                            "",
                                            [
                                                "View Resource",
                                                "Create Resource",
                                                "Link Resource",
                                                "Unlink Resource",
                                                "Delete Resource",
                                                "Copy ID",
                                            ],
                                            "Help::RESOURCE_TABLE",
                                        ],
                                        right_click_selects=True,
                                        enable_click_events=True,
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            expand_y=True,
                            layout=[
                                [sg.Text("Custom Fields", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-CONTACT_CUSTOM_FIELDS_TABLE-",
                                        headings=["Name", "Value"],
                                        right_click_menu=[
                                            "",
                                            [
                                                "View Full Content",
                                                "Create Custom Field",
                                                "Edit Custom Field",
                                                "Delete Custom Field",
                                                "Help::CUSTOM_FIELDS",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ],
                ],
            )
        ],
    ]


def get_org_view_layout():
    return [
        [
            sg.Column(
                expand_x=True,
                layout=get_viewer_head(),
            )
        ],
        [
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                right_click_menu=["", ["Help::ORG_VIEWER"]],
                layout=[
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Organization Contacts", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-ORG_CONTACT_INFO_TABLE-",
                                        headings=[
                                            "ID",
                                            "Name",
                                            "Title",
                                            "Email",
                                            "Phone",
                                        ],
                                        visible_column_map=[
                                            False,
                                            True,
                                            True,
                                            True,
                                            True,
                                        ],
                                        font=("Arial", 15),
                                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                        row_height=30,
                                        alternating_row_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                        justification="center",
                                        num_rows=5,
                                        auto_size_columns=True,
                                        expand_x=True,
                                        enable_click_events=True,
                                        right_click_menu=[
                                            "&Right",
                                            [
                                                "View",
                                                "Copy ID",
                                                "Change Title",
                                                "Add Contact",
                                                "Remove Contact",
                                                "Help::ORG_VIEWER",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        )
                    ],
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Associated Resources", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-ORG_RESOURCES_TABLE-",
                                        headings=["ID", "Name", "Value"],
                                        visible_column_map=[False, True, True],
                                        font=("Arial", 15),
                                        right_click_menu=[
                                            "",
                                            [
                                                "View Resource",
                                                "Create Resource",
                                                "Link Resource",
                                                "Unlink Resource",
                                                "Delete Resource",
                                                "Copy ID",
                                                "Help::RESOURCE_TABLE",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        enable_click_events=True,
                                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                        row_height=30,
                                        alternating_row_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                        justification="center",
                                        num_rows=5,
                                        auto_size_columns=True,
                                        expand_x=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Custom Fields", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-ORG_CUSTOM_FIELDS_TABLE-",
                                        headings=["Name", "Value"],
                                        font=("Arial", 15),
                                        right_click_menu=[
                                            "",
                                            [
                                                "View Full Content",
                                                "Create Custom Field",
                                                "Edit Custom Field",
                                                "Delete Custom Field",
                                                "Help::CUSTOM_FIELDS",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                        row_height=30,
                                        alternating_row_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                        justification="center",
                                        num_rows=5,
                                        auto_size_columns=True,
                                        expand_x=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ],
                ],
            )
        ],
    ]


def get_resource_view_layout():
    return [
        [
            sg.Column(
                expand_x=True,
                right_click_menu=["", ["Help::RESOURCE_VIEW"]],
                layout=[
                    [
                        sg.Column(
                            layout=get_action_bar(Screen.RESOURCE_VIEW),
                            background_color=sg.theme_progress_bar_color()[1],
                            element_justification="left",
                        ),
                        sg.Column(
                            background_color=sg.theme_progress_bar_color()[1],
                            element_justification="right",
                            layout=[
                                [
                                    sg.Button("Delete", k="-DELETE_RESOURCE-"),
                                    sg.Button("Back", k="-EXIT_RESOURCE-"),
                                ]
                            ],
                        ),
                    ],
                    [
                        sg.Button(
                            "Back", k="-EXIT_1_RESOURCE-", expand_y=True, expand_x=True
                        ),
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            right_click_menu=[
                                "",
                                ["Change Name", "Help::RESOURCE_VIEW"],
                            ],
                            background_color=sg.theme_progress_bar_color()[1],
                            layout=[
                                [
                                    sg.Text(
                                        "Resource Name",
                                        font=("Arial", 13),
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-RESOURCE_NAME-",
                                        font=("Arial", 15),
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                            ],
                        ),
                        sg.Column(
                            element_justification="center",
                            justification="left",
                            right_click_menu=[
                                "",
                                [
                                    "Change Value",
                                    "View Full Value",
                                    "Help::RESOURCE_VIEW",
                                ],
                            ],
                            background_color=sg.theme_progress_bar_color()[1],
                            expand_x=True,
                            layout=[
                                [
                                    sg.Text(
                                        "Resource Value",
                                        font=("Arial", 13),
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                                [
                                    sg.Text(
                                        "",
                                        key="-RESOURCE_VALUE-",
                                        font=("Arial", 15),
                                        background_color=sg.theme_progress_bar_color()[
                                            1
                                        ],
                                    )
                                ],
                            ],
                        ),
                    ],
                ],
            )
        ],
        [
            sg.Column(
                background_color=sg.theme_progress_bar_color()[1],
                expand_x=True,
                layout=[
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [
                                    sg.Text(
                                        "Associated Organizations", font=("Arial", 13)
                                    )
                                ],
                                [
                                    sg.Table(
                                        key="-RESOURCE_ORGANIZATIONS_TABLE-",
                                        headings=[
                                            "ID",
                                            "Name",
                                            "Status",
                                            "Primary Contact",
                                        ],
                                        visible_column_map=[False, True, True, True],
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        enable_click_events=True,
                                        right_click_menu=[
                                            "&Right",
                                            [
                                                "View::RESOURCE_ORG",
                                                "Copy ID",
                                                "Link Organization",
                                                "Unlink Organization",
                                                "Help::RESOURCE_VIEW",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ],
                    [
                        sg.Column(
                            element_justification="center",
                            expand_x=True,
                            layout=[
                                [sg.Text("Associated Contacts", font=("Arial", 13))],
                                [
                                    sg.Table(
                                        key="-RESOURCE_CONTACTS_TABLE-",
                                        headings=["ID", "Name", "Email", "Phone"],
                                        visible_column_map=[False, True, True, True],
                                        right_click_menu=[
                                            "",
                                            [
                                                "View::RESOURCE_CONTACT",
                                                "Copy ID",
                                                "Link Contact",
                                                "Unlink Contact",
                                                "Help::RESOURCE_VIEW",
                                            ],
                                        ],
                                        right_click_selects=True,
                                        enable_click_events=True,
                                        expand_x=True,
                                        font=("Arial", 15),
                                        num_rows=5,
                                        size=(500, 200),
                                        values=[[]],
                                    )
                                ],
                            ],
                        ),
                    ],
                ],
            )
        ],
    ]
