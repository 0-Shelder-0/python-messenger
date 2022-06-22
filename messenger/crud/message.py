from datetime import date

from sqlalchemy.orm import Session

import schemas.message as schema
from core.db.models import Message, MessageStatusLog, UserChat, UserMessageStatusLog, Chat
from crud.messageStatus import MessageStatus
from crud.userMessageStatus import UserMessageStatus


def create_message(db: Session, message: schema.Message, current_user_id: int):
    message_db = Message(text=message.text, send_date=message.send_date, user_id=current_user_id,
                         chat_id=message.chat_id)
    db.add(message_db)
    db.commit()

    message_status = MessageStatusLog(status=MessageStatus.sent, message_id=message_db.id)
    db.add(message_status)

    user_chat_id_rows = db.query(UserChat.user_id).filter(UserChat.chat_id == message.chat_id).all()
    user_chat_ids = list(map(lambda row: row['user_id'], user_chat_id_rows))
    user_message_status_logs = []
    for user_id in user_chat_ids:
        log = UserMessageStatusLog(status=UserMessageStatus.sent, user_id=user_id, message_id=message_db.id)
        user_message_status_logs.append(log)

    db.add_all(user_message_status_logs)
    db.commit()

    return message_db


def update_message(db: Session, user_id: int, message: schema.UpdateMessage):
    message_db = db.query(Message).filter(Message.id == message.id).filter(Message.user_id == user_id).one_or_none()
    if message_db is not None:
        message_db.text = message.text
        db.commit()
        add_message_status_log(db=db, status=MessageStatus.changed, message_id=message_db.id)

    return message_db


def delete_message(db: Session, message_id: int, user_id: int):
    db.query(Message).filter(Message.id == message_id).filter(Message.user_id == user_id).delete()
    db.commit()


def get_last_messages_in_chat(db: Session, chat_id: int, user_id: int, count: int):
    now = date.today()
    messages = db.query(Message).join(Chat) \
                   .filter(Message.chat_id == chat_id) \
                   .filter(Message.user_id == user_id) \
                   .filter(Message.send_date <= now) \
                   .order_by(Message.send_date.desc())[:count]
    all_message_ids = list(map(lambda m: m.id, messages))

    read_message_id_rows = db.query(UserMessageStatusLog.message_id) \
        .filter(UserMessageStatusLog.message_id.in_(all_message_ids)) \
        .filter(UserMessageStatusLog.status == UserMessageStatus.read) \
        .all()
    read_message_ids = list(map(lambda row: row['message_id'], read_message_id_rows))
    unread_message_ids = set(all_message_ids).difference(read_message_ids)

    if len(unread_message_ids) > 0:
        message_status_logs = []
        for message_id in unread_message_ids:
            log = UserMessageStatusLog(status=UserMessageStatus.read, message_id=message_id, user_id=user_id)
            message_status_logs.append(log)
        db.add_all(message_status_logs)
        db.commit()

    return messages


def add_message_status_log(db: Session, status: MessageStatus, message_id: int):
    message_status = MessageStatusLog(status=status, message_id=message_id)
    db.add(message_status)
    db.commit()


def add_user_message_status_log(db: Session, status: UserMessageStatus, message_id: int, user_id: int):
    user_message_status_log = UserMessageStatusLog(status=status, user_id=user_id, message_id=message_id)
    db.add(user_message_status_log)
    db.commit()
