from pony import orm
from ftplib import FTP
from enums import DBStatus


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

    def get_contacts(
            self,
            query: str = "",
            field: str = "",
            sort: str = "",
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

        if (not (query or field or sort)) or (not (query or field) and sort):
            db_query = orm.select(c for c in Contact)

        elif not (query or field):
            return False
        
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
        
        return db_query.page(self.contacts_page, 10)


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

        if (not (query or field or sort)) or (not (query or field) and sort):
            db_query = orm.select(o for o in Organization)

        elif not (query or field):
            return False
        
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
        match provider:
            case "sqlite":
                # If the provider is SQLite, we have to check if the user is storing it in an FTP server.
                # If they are, we have to take download it and temporarily store it on our machine.
                if server_address:
                    ftp = FTP(server_address)
                    ftp.login(username, password)
                    ftp.cwd(absolute_path)
                    ftp.retrbinary(
                        "RETR " + absolute_path, open("temp/db.db", "wb").write
                    )
                    ftp.quit()

                    self.bind(
                        provider=provider, filename="data/temp/db.db", create_db=True
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
