from enum import Enum


class ChatType(str, Enum):
    public = "public"
    private = "private"
    group = "group"
