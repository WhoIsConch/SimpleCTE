from enum import Enum


class DBStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    LOGIN_REQUIRED = 3


class Screen(Enum):
    ORG_SEARCH = 1
    ORG_VIEW = 2
    ORG_CREATE = 3
    CONTACT_SEARCH = 4
    CONTACT_VIEW = 5
    CONTACT_CREATE = 6
    LOGIN = 7
    SETTINGS = 8
    HELP = 9
    BACKUP_SQLITE = 10
    BACKUP_SERVER = 11
    EXPORT = 12
    RESOURCE_CREATE = 13
