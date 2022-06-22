from datetime import datetime
from typing import List

from pydantic import BaseModel

from crud.chatType import ChatType


class Chat(BaseModel):
    name: str
    created_date: datetime
    type: str


class CreateChat(BaseModel):
    name: str
    type: ChatType
    user_ids: List[int]


class UpdateChat(BaseModel):
    id: int
    name: str
    user_ids: List[int]


class ChatInDB(Chat):
    id: int

    class Config:
        orm_mode = True
