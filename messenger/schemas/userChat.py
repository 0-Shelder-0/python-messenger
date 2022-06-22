from pydantic import BaseModel


class UserChat(BaseModel):
    user_id: int
    chat_id: int
