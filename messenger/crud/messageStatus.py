from enum import Enum


class MessageStatus(str, Enum):
    sent = "sent"
    changed = "changed"
