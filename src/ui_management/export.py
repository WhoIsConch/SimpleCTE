from typing import TYPE_CHECKING

import PySimpleGUI as sg
import pandas as pd

from ..layouts import get_export_layout

if TYPE_CHECKING:
    from ..process.app import App

__all__ = (
    "export_handler",
)


def export_handler(app: "App"):
    """
    Handles the export process.
    :param app: The App object.
    """
    # Create the window
    window = sg.Window("Export", get_export_layout(), finalize=True, modal=True)

    # Create the event loop
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "-EXPORT_CANCEL-":
            break

        if event == "-EXPORT_EXPORT-":
            export_format = values["-EXPORT_FORMAT-"]
            export_path = values["-EXPORT_PATH-"]
            export_name = values["-EXPORT_NAME-"]

            orgs = app.db.get_organizations(paginated=False)
            org_data = [
                [org.id, org.name, org.type, org.status, ", ".join(org.addresses),
                 ", ".join([str(p) for p in org.phones]), "\n".join(f"{field_name}: {field_value}\n" for
                                                                    field_name, field_value in
                                                                    org.custom_fields.items()),
                 ", ".join([str(c.id) for c in org.contacts]), ", ".join(str(r.id) for r in org.resources)]
                for org in orgs
            ]

            contacts = app.db.get_contacts(paginated=False)
            contact_data = [
                [contact.id, contact.first_name, contact.last_name, ", ".join(contact.addresses),
                 ", ".join([str(p) for p in contact.phone_numbers]),
                 ", ".join(contact.emails), contact.availability, contact.status,
                 "\n".join([f"{field_name}: {field_value}" for
                            field_name, field_value in
                            contact.contact_info.items()]), "\n".join(f"{field_name}: {field_value}\n" for
                                                                      field_name, field_value in
                                                                      contact.custom_fields.items()),
                 "\n".join([f"{field_name}: {field_value}" for
                            field_name, field_value in
                            contact.org_titles.items()]), ", ".join(str(r.id) for r in contact.resources),
                 ", ".join(str(o.id) for o in contact.organizations)]
                for contact in contacts
            ]

            org_df = pd.DataFrame(org_data,
                                  columns=["ID", "Name", "Type", "Status", "Addresses", "Phones", "Custom Fields",
                                           "Contacts", "Resources"])
            contact_df = pd.DataFrame(contact_data,
                                      columns=["ID", "First Name", "Last Name", "Addresses", "Phone Numbers", "Emails",
                                               "Availability", "Status", "Contact Info", "Custom Fields", "Org Titles",
                                               "Resources", "Organizations"])

            if export_format == "CSV":
                org_df.to_csv(f"{export_path}/{export_name}_orgs.csv", index=False)
                contact_df.to_csv(f"{export_path}/{export_name}_contacts.csv", index=False)

            elif export_format == "JSON":
                org_df.to_json(f"{export_path}/{export_name}_orgs.json", orient="records")
                contact_df.to_json(f"{export_path}/{export_name}_contacts.json", orient="records")

            elif export_format == "Markdown":
                org_df.to_markdown(f"{export_path}/{export_name}_orgs.md", index=False)
                contact_df.to_markdown(f"{export_path}/{export_name}_contacts.md", index=False)

            elif export_format == "Excel":
                org_df.to_excel(f"{export_path}/{export_name}_orgs.xlsx", index=False)
                contact_df.to_excel(f"{export_path}/{export_name}_contacts.xlsx", index=False)

            elif export_format == "HTML":
                org_df.to_html(f"{export_path}/{export_name}_orgs.html", index=False)
                contact_df.to_html(f"{export_path}/{export_name}_contacts.html", index=False)

            elif export_format == "Plaintext":
                org_df.to_string(f"{export_path}/{export_name}_orgs.txt", index=False)
                contact_df.to_string(f"{export_path}/{export_name}_contacts.txt", index=False)

            else:
                raise ValueError("Invalid export format.")

            break
