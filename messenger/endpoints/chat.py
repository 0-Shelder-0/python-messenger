from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud.chat as crud
import crud.user as crud_user
from deps import get_db, get_current_user
from schemas.chat import ChatInDB, CreateChat, UpdateChat

router = APIRouter(prefix="/chat")


@router.get("/", response_model=List[ChatInDB])
async def get_chats(count: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Получить чаты текущего пользователя"""

    chats = crud.get_chats_with_latest_activity(db=db, user_id=user_id, count=count)
    if chats is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return chats

@router.get("/{chat_id}", response_model=ChatInDB)
async def get_chat(chat_id: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Получить чат текущего пользователя по заданному chat_id"""

    chat = crud.get_chat_by_id(db=db, chat_id=chat_id, user_id=user_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return chat


@router.post("/", response_model=ChatInDB)
async def create_chat(chat: CreateChat, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Создать чат"""

    chat.user_ids = await get_existed_user_ids_in_chat(db=db, current_user_id=user_id, user_ids=chat.user_ids)
    result = crud.create_chat(db=db, chat=chat)
    return result


@router.put("/", response_model=ChatInDB)
async def update_chat(chat: UpdateChat, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Изменить чат"""

    chat.user_ids = await get_existed_user_ids_in_chat(db=db, current_user_id=user_id, user_ids=chat.user_ids)
    result = crud.update_chat(db=db, user_id=user_id, chat=chat)
    return result


@router.delete("/")
async def delete_chat(chat_id: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Удалить чат"""
    crud.delete_chat(db=db, chat_id=chat_id, user_id=user_id)


async def get_existed_user_ids_in_chat(db: Session, current_user_id: int, user_ids: List[int]):
    if not user_ids.__contains__(current_user_id):
        user_ids.append(current_user_id)

    exist_users = crud_user.get_user_list_by_ids(db=db, user_ids=user_ids)
    exist_users_ids = list(map(lambda row: row['id'], exist_users))
    return exist_users_ids
