from enum import Enum


class UserMessageStatus(str, Enum):
    sent = "sent"
    read = "read"
