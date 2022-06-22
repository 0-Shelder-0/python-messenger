from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String)
    hashed_password = Column(String)
    name = Column(String)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_date = Column(DateTime, server_default=func.now())
    type = Column(String)


class UserChat(Base):
    __tablename__ = "users_chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    send_date = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))


class UserMessageStatusLog(Base):
    __tablename__ = "user_message_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    message_id = Column(Integer, ForeignKey('messages.id'))


class MessageStatusLog(Base):
    __tablename__ = "message_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    created_date = Column(DateTime, server_default=func.now())
    message_id = Column(Integer, ForeignKey('messages.id'))
