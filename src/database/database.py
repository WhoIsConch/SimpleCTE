from pony import orm
from ftplib import FTP
from ..utils.enums import DBStatus
from ..utils.helpers import format_phone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..process.app import App


class Database(orm.Database):
    """
    The main database class.
    This holds methods responsible for interacting with the database.
    """

    def __init__(self):
        super().__init__()
        self.contacts_page = 0
        self.organizations_page = 0
        self.status = DBStatus.DISCONNECTED
        self.password = None

    def get_contacts(
            self,
            query: str = "",
            field: str = "",
            sort: str = "",
            paginated: bool = True,
    ):

        """
        Get a list of contacts from the database.
        Field can include, based on the GUI implementation,
        name, status, primary phone, address, custom field name and
        custom field value.
        Sort can be by status, alphabetical, type (commercial/community/other), or 
        association with a resource. 
        """

        field = field.lower()
        query = query.lower()
        sort = sort.lower()
        db_query = None

        if field == "name":
            db_query = orm.select(c for c in Contact if query in c.name.lower())

        elif field == "status":
            db_query = orm.select(c for c in Contact if query in c.status.lower())

        elif field == "primary phone":
            try:
                query = int(query)
            except ValueError:
                return False
            db_query = orm.select(c for c in Contact if query in c.phone_numbers)

        elif field == "address":
            db_query = orm.select(c for c in Contact if query in c.addresses)

        elif field == "custom field name":
            db_query = orm.select(c for c in Contact if query in c.custom_fields.keys())

        elif field == "custom field value":
            db_query = orm.select(c for c in Contact if query in c.custom_fields.values())

        else:
            db_query = orm.select(c for c in Contact)

        if sort == "status":
            db_query = db_query.sort_by(Contact.status)

        elif sort == "alphabetical":
            db_query = db_query.sort_by(Contact.last_name)

        elif sort == "type":
            db_query = db_query.sort_by(Contact.availability)

        elif sort == "resource":
            # Query has the ID of the resource to sort by. So, search for all of the 
            # contacts that are associated with the resource.
            # TODO: Filter by Resource
            db_query = orm.select(c for c in Contact if query in c.resources)

        if paginated:
            return db_query.page(self.contacts_page, 10)
        else:
            return db_query

    def get_organizations(
            self,
            query: str = "",
            field: str = "",
            sort: str = "",
            paginated: bool = True,
    ):
        """
        Get a list of organizations from the database.
        Field can include, based on the GUI implementation,
        name, status, primary phone, address, custom field name and
        custom field value.
        Sort can be by status, alphabetical, type (commercial/community/other), or 
        primary contact. 
        """

        field = field.lower()
        query = query.lower()
        sort = sort.lower()

        db_query = None

        if field == "name":
            db_query = orm.select(o for o in Organization if query in o.name.lower())

        elif field == "status":
            db_query = orm.select(o for o in Organization if query in o.status.lower())

        elif field == "primary phone":
            try:
                query = int(query)
            except ValueError:
                return False
            db_query = orm.select(o for o in Organization if query in o.phones)

        elif field == "address":
            db_query = orm.select(o for o in Organization if query in o.addresses)

        elif field == "custom field name":
            db_query = orm.select(o for o in Organization if query in o.custom_fields.keys())

        elif field == "custom field value":
            db_query = orm.select(o for o in Organization if query in o.custom_fields.values())

        else:
            db_query = orm.select(o for o in Organization)

        if sort == "status":
            db_query = db_query.sort_by(Organization.status)

        elif sort == "alphabetical":
            db_query = db_query.sort_by(Organization.name)

        elif sort == "type":
            db_query = db_query.sort_by(Organization.type)

        elif sort == "primary contact":
            db_query = db_query.sort_by(Organization.contacts.first().last_name)

        if paginated:
            return db_query.page(self.organizations_page, 10)
        else:
            return db_query

    def get_contact(self, contact_id: int) -> "Contact":
        return Contact.get(id=contact_id)

    def get_organization(self, org_id: int) -> "Organization":
        return Organization.get(id=org_id)

    @orm.db_session
    def create_contact(self, **kwargs) -> "Contact":
        values = kwargs.copy()
        if phone := values.get("phone_number", None):
            values["phone_numbers"] = [phone]
            del values["phone_number"]

        if address := values.get("address", None):
            values["addresses"] = [address]
            del values["address"]

        contact = Contact(**values)
        self.commit()

        return contact

    @orm.db_session
    def create_organization(self, **kwargs) -> "Organization":
        values = kwargs.copy()
        if phone := values.get("phone_number", None):
            try:
                values["phones"] = [int(phone)]
            except ValueError:
                values["phones"] = []
            del values["phone_number"]

        if address := values.get("address", None):
            values["addresses"] = [address]
            del values["address"]

        organization = Organization(**values)
        self.commit()

        return organization

    @orm.db_session
    def update_contact(self, contact: "Contact | int", **kwargs) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if contact is None:
            return False

        for key, value in kwargs.items():
            # Discard the value if they are empty and its field is required
            if value == "" and key in ["first_name", "last_name"]:
                continue
            if key == "phone_number":
                contact.phone_numbers = [value]
            elif key == "address":
                contact.addresses = [value]
            else:
                setattr(contact, key, value)

        self.commit()

        return True

    def update_organization(self, org: "Organization | int", **kwargs) -> bool:
        if isinstance(org, int):
            org = Organization.get(id=org)

        if org is None:
            return False

        for key, value in kwargs.items():
            # Discard the value if they are empty and its field is required
            if value == "" and key in ["name", "type"]:
                continue

            if key == "phone_number":
                org.phone_numbers = [value]
            elif key == "address":
                org.addresses = [value]
            else:
                setattr(org, key, value)

        self.commit()

        return True

    @orm.db_session
    def delete_contact(self, contact: "Contact | int") -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if contact is None:
            return False

        contact.delete()
        self.commit()

        return True

    @orm.db_session
    def delete_organization(self, org: "Organization | int") -> bool:
        if isinstance(org, int):
            org = Organization.get(id=org)

        if org is None:
            return False

        org.delete()
        self.commit()

        return True

    @orm.db_session
    def add_contact_to_org(self, contact: "Contact int", org: "Organization | int") -> bool:
        if isinstance(org, int):
            org = Organization.get(id=org)

        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if org is None or contact is None:
            return False

        org.contacts.add(contact)
        self.commit()

        return True

    @orm.db_session
    def remove_contact_from_org(self, contact: "Contact | int", org: "Organization | int") -> bool:
        if isinstance(org, int):
            org = Organization.get(id=org)

        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if org is None or contact is None:
            return False

        org.contacts.remove(contact)
        self.commit()

        return True

    @orm.db_session
    def change_contact_title(self, org: "Organization | int", contact: "Contact | int", title: str) -> bool:
        if isinstance(org, int):
            org = Organization.get(id=org)

        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if org is None or contact is None:
            return False

        contact.org_titles[str(org.id)] = title
        self.commit()

        return True

    @orm.db_session
    def create_resource(self, **kwargs) -> "Resource":
        resource = Resource(**kwargs)
        self.commit()

        return resource

    @orm.db_session
    def delete_resource(self, resource: "Resource | int") -> bool:
        if isinstance(resource, int):
            resource = Resource.get(id=resource)

        if resource is None:
            return False

        resource.delete()
        self.commit()

        return True

    @orm.db_session
    def link_resource(self, resource: "Resource | int", org: "Organization | int" = None,
                      contact: "Contact | int" = None) -> bool:
        if isinstance(resource, int):
            resource = Resource.get(id=resource)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if resource is None or (org is None and contact is None):
            return False

        if org:
            org.resources.add(resource)

        if contact:
            contact.resources.add(resource)

        self.commit()

        return True

    @orm.db_session
    def unlink_resource(self, resource: "Resource | int", org: "Organization | int" = None,
                        contact: "Contact | int" = None) -> bool:
        if isinstance(resource, int):
            resource = Resource.get(id=resource)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if resource is None or (org is None and contact is None):
            return False

        if org:
            org.resources.remove(resource)

        if contact:
            contact.resources.remove(resource)

        self.commit()

        return True

    @orm.db_session
    def create_custom_field(self, name: str, value: str, contact: "Contact | int" = None,
                            org: "Organization | int" = None) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if contact is None and org is None:
            return False

        if contact:
            if contact.custom_fields.get(name, None):
                return False
            contact.custom_fields[name] = value

        if org:
            if org.custom_fields.get(name, None):
                return False
            org.custom_fields[name] = value

        self.commit()

        return True

    @orm.db_session
    def update_custom_field(self, name: str, value: str, contact: "Contact | int" = None,
                            org: "Organization | int" = None) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if contact is None and org is None:
            return False

        if contact:
            contact.custom_fields[name] = value

        if org:
            org.custom_fields[name] = value

        self.commit()

        return True

    @orm.db_session
    def delete_custom_field(self, name: str, contact: "Contact | int" = None, org: "Organization | int" = None) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if contact is None and org is None:
            return False

        if contact:
            del contact.custom_fields[name]

        if org:
            del org.custom_fields[name]

        self.commit()

        return True

    @orm.db_session
    def create_contact_info(self, name: str, value: str, contact: "Contact | int" = None,
                            org: "Organization | int" = None) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if contact is None and org is None:
            return False

        if contact:
            if contact.contact_info.get(name, None):
                return False
            contact.contact_info[name] = value

        if org:
            if org.contact_info.get(name, None):
                return False
            org.contact_info[name] = value

        self.commit()

        return True

    @orm.db_session
    def update_contact_info(self, name: str, value: str, contact: "Contact | int" = None,
                            org: "Organization | int" = None) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if contact is None and org is None:
            return False

        if contact:
            contact.contact_info[name] = value

        if org:
            org.contact_info[name] = value

        self.commit()

        return True

    @orm.db_session
    def delete_contact_info(self, name: str, value=None, contact: "Contact | int" = None,
                            org: "Organization | int" = None) -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if isinstance(org, int):
            org = Organization.get(id=org)

        if contact is None and org is None:
            return False

        contact_diff_values = {
            "phone": "phone_numbers",
            "address": "addresses",
            "email": "emails",
        }

        org_diff_values = {
            "phone": "phones",
            "address": "addresses"
        }

        if contact:
            if name.lower() == "availability":
                contact.availability = ""

            elif name.lower() in contact_diff_values.keys():
                getattr(contact, contact_diff_values[name.lower()]).remove(value)

            else:
                del contact.contact_info[name]

        if org:
            if name in org_diff_values.keys():
                getattr(org, org_diff_values[name]).remove(value)

        self.commit()

        return True

    def construct_database(
            self,
            provider: str,
            absolute_path: str,
            database_name: str | None = None,
            server_address: str | None = None,
            server_port: int | None = None,
            username: str | None = None,
            password: str | None = None,
    ) -> "Database":
        # Perform a different operation based on what type of database is being used
        self.password = password
        match provider:
            case "sqlite":
                # If the provider is SQLite, we have to check if the user is storing it in an FTP server.
                # If they are, we have to take download it and temporarily store it on our machine.
                if server_address:

                    ftp = FTP(server_address)
                    ftp.login(username, password)
                    ftp.cwd(absolute_path[:absolute_path.rfind("/")])
                    ftp.retrbinary(
                        "RETR " + absolute_path, open("../data/temp/db.db", "wb").write
                    )
                    ftp.quit()

                    self.bind(
                        provider=provider, filename="../data/temp/db.db", create_db=True
                    )
                else:
                    self.bind(provider=provider, filename=absolute_path, create_db=True)

            case ["mysql", "postgres"]:
                # if the provider is MySQL or PostgreSQL, we will connect to the database server.
                self.bind(
                    provider=provider,
                    host=server_address,
                    port=server_port,
                    user=username,
                    passwd=password,
                    db=database_name,
                )

            # case "postgres":
            #     db.bind(provider=provider, host=server_address, port=server_port, user=username, password=password, database=database_name)

            case _:
                # In the case that a provider is not specified or is not found, we will return False.
                self.status = DBStatus.DISCONNECTED
                return self

        self.generate_mapping(create_tables=True)
        self.status = DBStatus.CONNECTED
        return self

    def close_database(self, app: "App") -> bool:
        if self.status != DBStatus.CONNECTED:
            return False

        self.disconnect()
        self.status = DBStatus.DISCONNECTED

        if app.settings["database"]["system"] == "sqlite" and app.settings["database"]["address"]:
            ftp = FTP(app.settings["database"]["server_address"])
            ftp.login(app.settings["database"]["username"], self.password)
            ftp.cwd(app.settings["database"]["absolute_path"])
            ftp.storbinary("STOR " + app.settings["database"]["absolute_path"], open("temp/db.db", "rb"))
            ftp.quit()

        return True


db = Database()


class Organization(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    type = orm.Required(str)

    status = orm.Optional(str)
    addresses = orm.Optional(orm.StrArray)
    phones = orm.Optional(orm.IntArray)
    custom_fields = orm.Optional(orm.Json)

    contacts = orm.Set("Contact")
    resources = orm.Set("Resource")

    @property
    def primary_contact(self):
        contact = self.contacts.filter(
            lambda c: c.org_titles[str(self.id)] == "Primary"
        ).first()
        if contact:
            return contact
        else:
            return None


class Contact(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    first_name = orm.Required(str)
    last_name = orm.Required(str)

    addresses = orm.Optional(orm.StrArray)
    phone_numbers = orm.Optional(orm.IntArray)
    emails = orm.Optional(orm.StrArray)
    availability = orm.Optional(str)
    status = orm.Optional(str)
    contact_info = orm.Optional(orm.Json)
    custom_fields = orm.Optional(orm.Json)

    org_titles = orm.Optional(orm.Json)
    organizations = orm.Set(Organization)
    resources = orm.Set("Resource")

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


class Resource(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    value = orm.Required(str)

    organizations = orm.Set(Organization)
    contacts = orm.Set(Contact)


@orm.db_session
def get_org_table_values(
        app: "App",
        search_info: dict[str, str, str] | None = None,
        paginated: bool = True,
        table_values: list | None = None,
):
    """
    Get the necessary information from the database to populate the search table's organization info.
    """
    if table_values is None:
        table_values = []

    if search_info:
        org_pages = app.db.get_organizations(**search_info, paginated=paginated)

    else:
        org_pages = app.db.get_organizations(paginated=paginated)

    for org in org_pages:
        contact = org.primary_contact
        contact_name = contact.name if contact else "No Primary Contact"
        table_values.append([org.id, org.name, org.type, contact_name, org.status])

    return table_values


@orm.db_session
def get_contact_table_values(
        app: "App",
        search_info: dict[str, str, str] | None = None,
        paginated: bool = True,
        table_values: list | None = None,
):
    """
    Get the necessary information from the database to populate the search table's contact info.
    """
    if table_values is None:
        table_values = []

    if search_info:
        contact_pages = app.db.get_contacts(**search_info, paginated=paginated)

    else:
        contact_pages = app.db.get_contacts(paginated=paginated)

    for contact in contact_pages:
        org = None
        for org in contact.organizations:
            if org.primary_contact == contact:
                break

        if org:
            org_name = org.name

        else:
            org_name = "No Organization"

        table_values.append(
            [
                contact.id,
                contact.name,
                org_name,
                format_phone(contact.phone_numbers[0])
                if contact.phone_numbers
                else "No Phone Number",
            ]
        )

    return table_values