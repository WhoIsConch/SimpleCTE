import PySimpleGUI as sg

__all__ = (
    "get_export_layout",
    "available_export_formats",
)

available_export_formats = (
    "CSV", "JSON", "Markdown", "Excel", "HTML", "Plaintext"
)


def get_export_layout():
    layout = [
        [
            sg.Column(
                justification="right",
                layout=[
                    [
                        sg.Checkbox("Export by Filter", key="-EXPORT_FILTER-", enable_events=True),
                        sg.Push(),
                        sg.Text("Items to Export:", size=(15, 1)),
                        sg.Checkbox("Organizations", key="-EXPORT_ORGS-", default=True),
                        sg.Checkbox("Contacts", key="-EXPORT_CONTACTS-", default=True)
                    ]
                ]
            )
        ],
            [sg.pin(sg.Column(visible=False, justification="left", key="-EXPORT_FILTER_COL-", layout=[
                [
                    sg.Text("Search Query:", size=(15, 1)),
                    sg.InputText(key="-EXPORT_SEARCH_QUERY-", size=(30, 1)),
                ],
                [
                    sg.Text("Filter by:", size=(15, 1)),
                    sg.Combo(["Name", "Type", "Status", "Address", "Phone", "Custom Field", "Contact Info",
                              "Resource"], key="-EXPORT_FILTER_TYPE-", size=(10, 1)),
                ],
                [
                    sg.Text("Sort by:", size=(15, 1)),
                    sg.Combo(["Name", "Type", "Status", "Address", "Phone", "Custom Field", "Contact Info",
                              "Resource"], key="-EXPORT_SORT_TYPE-", size=(10, 1)),
                    sg.Checkbox("Descending", key="-EXPORT_SORT_DESCENDING-")
                ],
            ])),
        ],
        [
         sg.Column(layout=[[
             sg.Text("Export Format:", size=(15, 1)),
             sg.Combo(["CSV", "JSON", "Markdown", "Excel", "HTML", "Plaintext"], key="-EXPORT_FORMAT-",
                      size=(10, 1)),
         ],
             [
                 sg.Text("Export Location:", size=(15, 1)),
                 sg.InputText(key="-EXPORT_PATH-", size=(30, 1)),
                 sg.FolderBrowse(key="-EXPORT_BROWSE-", size=(10, 1)),
             ],
             [
                 sg.Text("Export Name:", size=(15, 1)),
                 sg.InputText(key="-EXPORT_NAME-", size=(30, 1)),
             ],
             [
                 sg.Button("Export", key="-EXPORT_EXPORT-", size=(10, 1)),
                 sg.Button("Cancel", key="-EXPORT_CANCEL-", size=(10, 1)),
             ], ], justification="left")
        ],
    ]

    return layout
