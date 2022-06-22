from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    text: str
    send_date: datetime
    chat_id: int


class UpdateMessage(BaseModel):
    id: int
    text: str


class MessageInDB(Message):
    id: int

    class Config:
        orm_mode = True
