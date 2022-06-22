from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

import crud.message as crud
from deps import get_db, get_current_user
from schemas.message import Message, MessageInDB, UpdateMessage

router = APIRouter(prefix="/message")


@router.get("/", response_model=List[MessageInDB])
async def get_messages(chat_id: int, count: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Получить последние N сообщений текущего пользователя по заданному chat_id"""

    messages = crud.get_last_messages_in_chat(db=db, chat_id=chat_id, user_id=user_id, count=count)
    if messages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return messages


@router.post("/", response_model=MessageInDB)
async def create_message(message: Message, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Создать сообщение"""

    result = crud.create_message(db=db, message=message, current_user_id=user_id)
    return result


@router.put("/", response_model=MessageInDB)
async def update_message(message: UpdateMessage, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Изменить сообщение"""

    result = crud.update_message(db=db, user_id=user_id, message=message)
    return result


@router.delete("/")
async def delete_message(message_id: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Удалить сообщение"""
    crud.delete_message(db=db, message_id=message_id, user_id=user_id)
