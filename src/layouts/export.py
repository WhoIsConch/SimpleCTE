import PySimpleGUI as sg

__all__ = (
    "get_export_layout",
)


def get_export_layout():
    layout = [
        [
            sg.Text("Export Format:", size=(15, 1)),
            sg.Combo(["CSV", "JSON", "Markdown", "Excel", "HTML", "Plaintext"], key="-EXPORT_FORMAT-", size=(10, 1)),
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
        ],
    ]

    return layout
