from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

import schemas.chat as schema
from core.db.models import Chat, UserChat, User, Message, UserMessageStatusLog
from crud.chatType import ChatType

chat_database = [
    {
        "id": 1,
        "name": "Чат 1",
        "created_date": datetime(2022, 4, 20, 19, 39, 0),
        "type": ChatType.group,
    }
]

user_chat_database = [
    {
        "user_id": 1,
        "chat_id": 1
    },
    {
        "user_id": 2,
        "chat_id": 1
    },
]


def create_chat(db: Session, chat: schema.CreateChat):
    chat_db = Chat(name=chat.name, type=chat.type)
    db.add(chat_db)
    db.commit()

    user_chats = []
    for user_id in chat.user_ids:
        user_chats.append(UserChat(user_id=user_id, chat_id=chat_db.id))

    db.add_all(user_chats)
    db.commit()
    return chat_db


def add_user(db: Session, user_id: int, chat_id: int):
    user_chat = UserChat(user_id=user_id, chat_id=chat_id)
    db.add(user_chat)
    db.commit()
    return user_chat


def delete_user(db: Session, user_id: int, chat_id: int):
    db.query(UserChat).filter(UserChat.chat_id == chat_id, UserChat.user_id == user_id).delete()
    db.commit()


def get_chat_by_id(db: Session, chat_id: int, user_id: int):
    chat = db.query(Chat).join(UserChat).filter(Chat.id == chat_id).filter(
        UserChat.user_id == user_id).one_or_none()
    users = []
    if chat is not None:
        users = db.query(User).join(UserChat).filter(UserChat.chat_id == chat_id).all()
    chat.users = users
    return chat


def update_chat(db: Session, user_id: int, chat: schema.UpdateChat):
    user_chat = db.query(Chat) \
        .join(UserChat) \
        .filter(Chat.id == chat.id) \
        .filter(UserChat.user_id == user_id) \
        .one_or_none()

    if user_chat is not None:
        for param, value in chat.dict().items():
            setattr(user_chat, param, value)
        db.commit()

        user_id_by_chat_rows = db.query(UserChat.user_id) \
            .filter(UserChat.chat_id == chat.id) \
            .filter(UserChat.user_id.in_(chat.user_ids)) \
            .all()
        user_ids_by_chat = list(map(lambda row: row['user_id'], user_id_by_chat_rows))

        user_ids_for_add = set(chat.user_ids).difference(user_ids_by_chat)
        user_ids_for_delete = set(user_ids_by_chat).difference(chat.user_ids)

        user_chats_for_adding = []
        for user_id_for_add in user_ids_for_add:
            user_chats_for_adding.append(UserChat(user_id=user_id_for_add, chat_id=chat.id))
        db.add_all(user_chats_for_adding)

        db.query(UserChat).filter(UserChat.chat_id == chat.id).filter(
            UserChat.user_id.in_(user_ids_for_delete)).delete()
        db.commit()

        return user_chat


def delete_chat(db: Session, chat_id: int, user_id: int):
    user_chat = db.query(Chat) \
        .join(UserChat) \
        .filter(Chat.id == chat_id) \
        .filter(UserChat.user_id == user_id) \
        .one_or_none()

    if user_chat is not None:
        db.query(Chat).filter(Chat.id == chat_id).delete()
        db.query(UserChat).filter(UserChat.chat_id == chat_id).delete()
        db.commit()


def get_chats_with_latest_activity(db: Session, user_id: int, count: int):
    last_statuses = db.query(UserMessageStatusLog.message_id,
                             func.max(UserMessageStatusLog.created_date).label('last_created_date')) \
        .group_by(UserMessageStatusLog.message_id) \
        .subquery()

    chats = db.query(Chat) \
                .join(Message) \
                .join(UserMessageStatusLog) \
                .join(last_statuses, (UserMessageStatusLog.message_id == last_statuses.c.message_id) & (
            UserMessageStatusLog.created_date == last_statuses.c.last_created_date)) \
                .filter(UserMessageStatusLog.user_id == user_id)[:count]

    return chats
