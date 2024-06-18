from ftplib import FTP
from typing import TYPE_CHECKING, Any, Callable

from pony import orm

from utils.enums import DBStatus
from utils.helpers import format_phone
from layouts import get_field_keys, get_sort_keys

if TYPE_CHECKING:
    from process.app import App


__all__ = (
    "Database",
    "db",
    "Organization",
    "Contact",
    "Resource",
    "get_table_values",
    "search_and_destroy",
)


def search_and_destroy(func: "Callable") -> "Callable":
    """
    Decorator for functions that delete an object, so they can
    go through the app's stack and remove the deleted object
    using the app.stack.search_and_pop() function, referencing
    app from the subclass's self.app variable.
    """

    def wrapper(*args, **kwargs):
        app: "App" = args[0].app
        func(*args, **kwargs)
        app.stack.search_and_pop(args[1])

    return wrapper


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
        self.app = None

    @orm.db_session
    def get_records(
        self,
        record_type: "Organization | Contact | str",
        query: str = "",
        field: str = "",
        sort: str = "",
        paginated: bool = True,
        descending: bool = False,
    ) -> orm.core.Query | bool:
        """
        Get a list of records from the database.
        Field can include, based on the GUI implementation,
        name, status, primary phone, address, custom field name and
        custom field value.
        Sort can be by status, alphabetical, type (commercial/community/other), or
        association with a resource.
        """
        field = field.lower()
        query = query.lower()
        sort = sort.lower()

        # Convert the record type from a string to a class,
        # to save from importing the classes in some files.
        if isinstance(record_type, str):
            if record_type.lower() == "contact":
                record_type = Contact

            elif record_type.lower() == "organization":
                record_type = Organization

            elif record_type.lower() == "resource":
                record_type = Resource

            else:
                return False

        record_type_str = (
            "organization"
            if record_type == Organization
            else ("contact" if record_type == Contact else "resource")
        )
        field_key = get_field_keys(record=record_type_str)
        sort_key = get_sort_keys(record=record_type_str)

        if sort and sort not in sort_key:
            sort = ""

        if (
            field == "phone" or field == "id" or field == "associated with resource..."
        ) and not query.isdigit():
            return False

        if field == "phone" or field == "id":
            query = int(query)

        if not field or field not in field_key.keys():
            db_query = orm.select(r for r in record_type)

        elif (
            field == "custom field name"
            or field == "custom field value"
            or field == "contact info name"
            or field == "contact info value"
        ):
            db_query = orm.select(r for r in record_type)

            # Horrible, horrible hack to get around the fact that PonyORM doesn't support
            # querying JSON fields by keys or values.
            exclude_ids = []

            for record in db_query:
                for key in (
                    getattr(record, field_key[field]).keys()
                    if field == "custom field name" or field == "contact info name"
                    else getattr(record, field_key[field]).values()
                ):
                    if query in key.lower():
                        break
                else:
                    exclude_ids.append(record.id)

            db_query = db_query.filter(lambda r: r.id not in exclude_ids)

        elif field == "id":
            db_query = orm.select(
                r for r in record_type if getattr(r, field_key[field]) == int(query)
            )

        elif field == "associated with resource...":
            resource = Resource.get(id=int(query))

            if resource is None:
                return False

            db_query = orm.select(
                r for r in record_type if resource in getattr(r, field_key[field])
            )

        elif field == "address" or field == "phone" or field == "email":
            # Search through each item in the array, making each item lowercase if its a string
            # using the same hacky method as above, unfortunately.
            db_query = orm.select(r for r in record_type)

            exclude_ids = []

            for record in db_query:
                for f in getattr(record, field_key[field]):
                    if str(query) in (f.lower() if isinstance(f, str) else str(f)):
                        break
                else:
                    exclude_ids.append(record.id)

            db_query = db_query.filter(lambda r: r.id not in exclude_ids)

        elif not getattr(record_type, field_key[field]).is_string:
            db_query = orm.select(
                r for r in record_type if query in getattr(r, field_key[field])
            )

        else:
            db_query = orm.select(
                r for r in record_type if query in getattr(r, field_key[field]).lower()
            )

        # Sort the results
        if sort:
            # order the results by the specified field
            if descending:
                db_query = db_query.order_by(
                    orm.desc(getattr(record_type, sort_key[sort]))
                )
            else:
                db_query = db_query.order_by(getattr(record_type, sort_key[sort]))

        if paginated:
            return db_query.page(
                self.contacts_page
                if record_type == Contact
                else (self.organizations_page if record_type == Organization else 1),
                10,
            )
        else:
            return db_query

    @orm.db_session
    def get_contact(self, contact_id: int) -> "Contact":
        return Contact.get(id=contact_id)

    @orm.db_session
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

    @orm.db_session
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

    @search_and_destroy
    @orm.db_session
    def delete_contact(self, contact: "Contact | int") -> bool:
        if isinstance(contact, int):
            contact = Contact.get(id=contact)

        if contact is None:
            return False

        contact.delete()
        self.commit()

        return True

    @search_and_destroy
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
    def add_contact_to_org(
        self, contact: "Contact | int", org: "Organization | int"
    ) -> bool:
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
    def remove_contact_from_org(
        self, contact: "Contact | int", org: "Organization | int"
    ) -> bool:
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
    def change_contact_title(
        self, org: "Organization | int", contact: "Contact | int", title: str
    ) -> bool:
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
    def update_resource(self, resource: "Resource | int", **kwargs) -> "Resource":
        if isinstance(resource, int):
            resource = Resource.get(id=resource)

        for key, value in kwargs.items():
            setattr(resource, key, value)

        self.commit()
        return resource

    @orm.db_session
    def get_resource(self, resource_id: int) -> "Resource":
        return Resource.get(id=resource_id)

    @search_and_destroy
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
    def link_resource(
        self,
        resource: "Resource | int",
        org: "Organization | int" = None,
        contact: "Contact | int" = None,
    ) -> bool:
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
    def unlink_resource(
        self,
        resource: "Resource | int",
        org: "Organization | int" = None,
        contact: "Contact | int" = None,
    ) -> bool:
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
    def create_custom_field(
        self,
        name: str,
        value: str,
        contact: "Contact | int" = None,
        org: "Organization | int" = None,
    ) -> bool:
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
    def update_custom_field(
        self,
        name: str,
        value: str,
        contact: "Contact | int" = None,
        org: "Organization | int" = None,
    ) -> bool:
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
    def delete_custom_field(
        self,
        name: str,
        contact: "Contact | int" = None,
        org: "Organization | int" = None,
    ) -> bool:
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
    def create_contact_info(
        self,
        name: str,
        value: str,
        contact: "Contact | int" = None,
        org: "Organization | int" = None,
    ) -> bool:
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
    def update_contact_info(
        self,
        name: str,
        value: str,
        contact: "Contact | int" = None,
        org: "Organization | int" = None,
    ) -> bool:
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
    def delete_contact_info(
        self,
        name: str,
        value=None,
        contact: "Contact | int" = None,
        org: "Organization | int" = None,
    ) -> bool:
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

        org_diff_values = {"phone": "phones", "address": "addresses"}

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
                    ftp.cwd(absolute_path[: absolute_path.rfind("/")])
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
        """
        Close the database connection. This does not do much at the moment,
        but it may be useful in the future for implementing other databases types.
        """

        if self.status != DBStatus.CONNECTED:
            return False

        return True


db = Database()


class Organization(db.Entity):
    """
    An organization is a business or other professional non-human
    entity that can be associated with the school or CTE department.
    """

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    type = orm.Required(str)

    status = orm.Optional(str)
    addresses = orm.Optional(orm.StrArray)
    phones = orm.Optional(orm.IntArray)
    emails = orm.Optional(orm.StrArray)
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
    """
    A contact is an individual person that can be associated
    with a business or resource.
    """

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
    """
    A resource can act as an "agreement" of sorts between organizations and/or contacts.
    This can also be used simply to relate data between organizations and contacts.
    """

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    value = orm.Required(str)

    organizations = orm.Set(Organization)
    contacts = orm.Set(Contact)


@orm.db_session
def get_table_values(
    app: "App",
    record: "Organization | Contact",
    search_info: dict[str, Any] | None = None,
    descending: bool = False,
) -> list:
    """
    Get the necessary information from the database to populate the search table's info.
    """
    table_values = []

    # Make sure we don't have an empty search_info
    if search_info is None:
        search_info = {}

    # If we can't get records based on the search info, get all records
    record_pages = app.db.get_records(
        record, **search_info, paginated=False, descending=descending
    )

    if not record_pages:
        record_pages = app.db.get_records(record, paginated=False)

    # Iterate through the records to format them in a way that can be displayed in the table
    for rec in record_pages:
        if record == Organization:
            contact = rec.primary_contact
            contact_name = contact.name if contact else "No Primary Contact"
            table_values.append([rec.id, rec.name, rec.type, contact_name, rec.status])

        else:
            org = None
            for org in rec.organizations:
                if org.primary_contact == rec:
                    break

            if org:
                org_name = org.name

            else:
                org_name = "No Organization"

            table_values.append(
                [
                    rec.id,
                    rec.name,
                    org_name,
                    format_phone(rec.phone_numbers[0])
                    if rec.phone_numbers
                    else "No Phone Number",
                ]
            )

    return table_values
