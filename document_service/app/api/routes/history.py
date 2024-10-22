from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.history import HistoryCreate, HistoryUpdate, HistoryResponse
from app.services.history import (
    create_history_service,
    get_history_by_account_id_service,
    update_history_service,
    get_history_by_id_service,
)
from app.db.session import get_db
from app.utils import verify_user_token
import json

with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)

router = APIRouter()

# Получение истории посещений и назначений аккаунта
@router.get("/History/Account/{id}", response_model=List[HistoryResponse], status_code=200,
            summary=api_docs["get_history_by_account_id"]["summary"],
            description=api_docs["get_history_by_account_id"]["description"])
@router.get("/History/Account/{id}/", include_in_schema=False, response_model=List[HistoryResponse], status_code=200)
async def get_history_by_account_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token)
):
    return await get_history_by_account_id_service(id, user, db)

# Получение подробной информации о посещении и назначениях
@router.get("/History/{id}", response_model=HistoryResponse, status_code=200,
            summary=api_docs["get_history_by_id"]["summary"],
            description=api_docs["get_history_by_id"]["description"])
@router.get("/History/{id}/", include_in_schema=False, response_model=HistoryResponse, status_code=200)
async def get_history_by_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token)
):
    return await get_history_by_id_service(id, user, db)

# Создание истории посещения и назначения
@router.post("/History", response_model=HistoryResponse, status_code=201,
             summary=api_docs["create_history"]["summary"],
             description=api_docs["create_history"]["description"])
@router.post("/History/", include_in_schema=False, response_model=HistoryResponse, status_code=200)
async def create_history(
    history: HistoryCreate,  
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token), 
):
    return await create_history_service(history, user, db)

# Обновление истории посещения и назначения
@router.put("/History/{id}", response_model=HistoryResponse, status_code=200,
            summary=api_docs["update_history"]["summary"],
            description=api_docs["update_history"]["description"])
@router.put("/History/{id}/", include_in_schema=False, response_model=HistoryResponse, status_code=200)
async def update_history(
    id: int,
    history: HistoryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token)
):
    return await update_history_service(id, user, history, db)
