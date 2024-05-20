from enum import Enum


class DBStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    LOGIN_REQUIRED = 3


class Screen(Enum):
    ORG_SEARCH = 1
    ORG_VIEW = "-ORG_VIEW-"
    ORG_CREATE = 3
    CONTACT_SEARCH = 4
    CONTACT_VIEW = "-CONTACT_VIEW-"
    CONTACT_CREATE = 6
    LOGIN = 7
    SETTINGS = 8
    HELP = 9
    BACKUP_SQLITE = 10
    BACKUP_SERVER = 11
    EXPORT = 12
    RESOURCE_CREATE = 13
    RESOURCE_VIEW = "-RESOURCE_VIEW-"


class AppStatus(Enum):
    READY = 1
    BUSY = 2
    ERROR = 3


class BackupInterval(Enum):
    HOURLY = 3600
    DAILY = HOURLY * 24
    WEEKLY = DAILY * 7
    MONTHLY = WEEKLY * 4
    CUSTOM = None
