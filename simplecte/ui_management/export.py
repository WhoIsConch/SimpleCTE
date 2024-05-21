import os
from typing import TYPE_CHECKING

import PySimpleGUI as sg
import pandas as pd
from pony import orm

from layouts import get_export_layout, available_export_formats

if TYPE_CHECKING:
    from process.app import App
    from database.database import Organization, Contact

__all__ = ("export_handler",)


def _get_org_data(org: "Organization") -> list:
    org_data = [
        org.id,
        org.name,
        org.type,
        org.status,
        ", ".join(org.addresses),
        ", ".join([str(p) for p in org.phones]),
        "\n".join(
            f"{field_name}: {field_value}\n"
            for field_name, field_value in org.custom_fields.items()
        ),
        ", ".join([str(c.id) for c in org.contacts]),
        ", ".join(str(r.id) for r in org.resources),
    ]

    return org_data


def _get_contact_data(contact: "Contact") -> list:
    contact_data = [
        contact.id,
        contact.first_name,
        contact.last_name,
        ", ".join(contact.addresses),
        ", ".join([str(p) for p in contact.phone_numbers]),
        ", ".join(contact.emails),
        contact.availability,
        contact.status,
        "\n".join(
            [
                f"{field_name}: {field_value}"
                for field_name, field_value in contact.contact_info.items()
            ]
        ),
        "\n".join(
            f"{field_name}: {field_value}\n"
            for field_name, field_value in contact.custom_fields.items()
        ),
        "\n".join(
            [
                f"{field_name}: {field_value}"
                for field_name, field_value in contact.org_titles.items()
            ]
        ),
        ", ".join(str(r.id) for r in contact.resources),
        ", ".join(str(o.id) for o in contact.organizations),
    ]

    return contact_data


def update_info(info: dict, window: sg.Window, type: str):
    window[f"-EXPORT_FILTER_TYPE_{type}-"].update(value=info["field"])
    window[f"-EXPORT_SEARCH_QUERY_{type}-"].update(info["query"])
    window[f"-EXPORT_SORT_TYPE_{type}-"].update(info["sort"])
    window[f"-EXPORT_SORT_DESCENDING_{type}-"].update(info["descending"])


@orm.db_session
def export_handler(
    app: "App",
    org_id: int | None = None,
    contact_id: int | None = None,
    search_info: dict | None = None,
    search_type: str | None = None,
):
    """
    Handles the export process.
    """
    # Create the window
    window = sg.Window("Export", get_export_layout(), finalize=True, modal=True)

    contact_search_info = {}
    org_search_info = {}

    if search_type and search_info:
        if search_type.lower() == "contact":
            contact_search_info = search_info
            update_info(contact_search_info, window, "Contact")

        elif search_type.lower() == "org":
            org_search_info = search_info
            update_info(org_search_info, window, "Organization")

        window["-EXPORT_FILTER_COL-"].update(visible=True)
        window["-EXPORT_FILTER-"].update(value=True)

    # Create the event loop
    while True:
        event, values = window.read()

        print(event, values)

        if event == sg.WIN_CLOSED or event == "-EXPORT_CANCEL-":
            window.close()
            break

        for d, r in zip(
            [contact_search_info, org_search_info], ["Contact", "Organization"]
        ):
            d["field"] = values[f"-EXPORT_FILTER_TYPE_{r}-"]
            d["query"] = values[f"-EXPORT_SEARCH_QUERY_{r}-"]
            d["sort"] = values[f"-EXPORT_SORT_TYPE_{r}-"]
            d["descending"] = values[f"-EXPORT_SORT_DESCENDING_{r}-"]

        if event == "-EXPORT_FILTER-":
            window["-EXPORT_FILTER_COL-"].update(visible=values["-EXPORT_FILTER-"])

        elif event == "-EXPORT_EXPORT-":
            # Get the export information
            export_format = values["-EXPORT_FORMAT-"]
            export_path = values["-EXPORT_PATH-"]
            export_name = values["-EXPORT_NAME-"]
            export_orgs = values["-EXPORT_ORGS-"]
            export_contacts = values["-EXPORT_CONTACTS-"]
            export_resources = values["-EXPORT_RESOURCES-"]
            export_items = []

            if not export_contacts and not export_orgs:
                sg.popup("You must select a type of record to export.")
                continue

            # Deny invalid export formats
            if export_format.lower() not in [
                f.lower() for f in available_export_formats
            ]:
                sg.popup("Invalid export format.", title="Error")
                continue

            # Deny invalid export paths
            if not export_path or not os.path.exists(export_path):
                sg.popup("Invalid export path.", title="Error")
                continue

            # Deny invalid export names
            if not export_name:
                sg.popup("Invalid export name.", title="Error")
                continue

            # Create an "exporting" window that closes once the export is complete.
            exporting_window = sg.Window(
                "Exporting...", [[sg.Text("Exporting...")]], finalize=True, modal=True
            )

            if export_orgs:
                orgs = app.db.get_records(
                    "Organization",
                    paginated=False,
                    **org_search_info,
                )
                org_data = [_get_org_data(org) for org in orgs]

                org_df = pd.DataFrame(
                    org_data,
                    columns=[
                        "ID",
                        "Name",
                        "Type",
                        "Status",
                        "Addresses",
                        "Phones",
                        "Custom Fields",
                        "Contacts",
                        "Resources",
                    ],
                )
                export_items.append((org_df, "orgs"))

            if export_contacts:
                contacts = app.db.get_records(
                    "Contact",
                    paginated=False,
                    **contact_search_info,
                )
                contact_data = [_get_contact_data(contact) for contact in contacts]

                contact_df = pd.DataFrame(
                    contact_data,
                    columns=[
                        "ID",
                        "First Name",
                        "Last Name",
                        "Addresses",
                        "Phone Numbers",
                        "Emails",
                        "Availability",
                        "Status",
                        "Contact Info",
                        "Custom Fields",
                        "Org Titles",
                        "Resources",
                        "Organizations",
                    ],
                )
                export_items.append((contact_df, "contacts"))

            if export_resources:
                resources = app.db.get_records(
                    "Resource",
                    paginated=False,
                )
                resource_data = [
                    [
                        resource.id,
                        resource.name,
                        resource.value,
                        ", ".join([str(c.id) for c in resource.contacts]),
                        ", ".join([str(o.id) for o in resource.organizations]),
                    ]
                    for resource in resources
                ]

                resource_df = pd.DataFrame(
                    resource_data,
                    columns=["ID", "Name", "Value", "Contacts", "Organizations"],
                )
                export_items.append((resource_df, "resources"))

            if org_id:
                org = _get_org_data(app.db.get_organization(org_id))
                org_df = pd.DataFrame(
                    [org],
                    columns=[
                        "ID",
                        "Name",
                        "Type",
                        "Status",
                        "Addresses",
                        "Phones",
                        "Custom Fields",
                        "Contacts",
                        "Resources",
                    ],
                )

                export_items.append((org_df, "orgs"))

            if contact_id:
                contact = _get_contact_data(app.db.get_contact(contact_id))
                contact_df = pd.DataFrame(
                    [contact],
                    columns=[
                        "ID",
                        "First Name",
                        "Last Name",
                        "Addresses",
                        "Phone Numbers",
                        "Emails",
                        "Availability",
                        "Status",
                        "Contact Info",
                        "Custom Fields",
                        "Org Titles",
                        "Resources",
                        "Organizations",
                    ],
                )

                export_items.append((contact_df, "contacts"))

            for df in export_items:
                if export_format == "CSV":
                    df[0].to_csv(
                        f"{export_path}/{export_name}_{df[1]}.csv", index=False
                    )

                elif export_format == "JSON":
                    df[0].to_json(
                        f"{export_path}/{export_name}_{df[1]}.json", index=False
                    )

                elif export_format == "Markdown":
                    df[0].to_markdown(
                        f"{export_path}/{export_name}_{df[1]}.md", index=False
                    )

                elif export_format == "Excel":
                    df[0].to_excel(
                        f"{export_path}/{export_name}_{df[1]}.xlsx", index=False
                    )

                elif export_format == "HTML":
                    df[0].to_html(
                        f"{export_path}/{export_name}_{df[1]}.html", index=False
                    )

                elif export_format == "Plaintext":
                    df[0].to_string(
                        f"{export_path}/{export_name}_{df[1]}.txt", index=False
                    )

            exporting_window.close()
            sg.popup("Export complete.", title="Success")
            window.close()

            break

        else:
            continue
