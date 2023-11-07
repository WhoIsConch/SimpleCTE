from pony import orm
from ftplib import FTP
from enums import DBStatus

class Database(orm.Database):
    def __init__(self):
        super().__init__()
        self.contacts_page = 0
        self.organizations_page = 0
        self.status = DBStatus.DISCONNECTED

    def get_contacts(self):
        return orm.select(c for c in Contact).page(self.contacts_page, 10)
    
    def get_organizations(self):
        return orm.select(o for o in Organization).page(self.organizations_page, 10)

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
        match (provider):
            case "sqlite":
                # If the provider is SQLite, we have to check if the user is storing it in an FTP server.
                # If they are, we have to take download it and temporarily store it on our machine.
                if server_address:
                    ftp = FTP(server_address)
                    ftp.login(username, password)
                    ftp.cwd(absolute_path)
                    ftp.retrbinary("RETR " + absolute_path, open("temp/db.db", 'wb').write)
                    ftp.quit()

                    self.bind(provider=provider, filename="data/temp/db.db", create_db=True)
                else:
                    self.bind(provider=provider, filename=absolute_path, create_db=True)

            case ["mysql", "postgres"]:
                # if the provider is MySQL or PostgreSQL, we will connect to the database server.
                self.bind(provider=provider, host=server_address, port=server_port, user=username, passwd=password, db=database_name)

            # case "postgres":
            #     db.bind(provider=provider, host=server_address, port=server_port, user=username, password=password, database=database_name)

            case _:
                # In the case that a provider is not specified or is not found, we will return False.
                self.status = DBStatus.DISCONNECTED
                return self
        
        self.generate_mapping(create_tables=True)
        self.status = DBStatus.CONNECTED
        return self

    @orm.db_session
    def populate_database():
        Contact()

db = Database()

class Organization(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    type = orm.Required(str)

    status = orm.Optional(str)
    addresses = orm.Optional(orm.StrArray)
    phones = orm.Optional(orm.IntArray)
    custom_fields = orm.Optional(orm.Json)

    contacts = orm.Set('Contact')
    resources = orm.Set('Resource')

class Contact(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)

    addresses = orm.Optional(orm.StrArray)
    phone_numbers = orm.Optional(orm.IntArray)
    emails = orm.Optional(orm.StrArray)
    availability = orm.Optional(str)
    contact_info = orm.Optional(orm.Json)
    custom_fields = orm.Optional(orm.Json)

    org_titles = orm.Optional(orm.Json)
    organizations = orm.Set(Organization)
    resources = orm.Set('Resource')
    
class Resource(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    value = orm.Optional(str)

    organizations = orm.Set(Organization)
    contacts = orm.Set(Contact)


