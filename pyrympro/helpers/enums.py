from enum import Enum, IntEnum


class MediaTypes(Enum):
    NONE = "0"
    EMAIL = "3"
    SMS = "1"
    ALL = "4"


class AlertTypes(IntEnum):
    DAILY_EXCEPTION = 12
    LEAK = 23
    CONSUMPTION_WHILE_AWAY = 1001
