from typing import List
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, Request
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

async def get_es(request: Request) -> AsyncElasticsearch:
    return request.app.state.es 

def history_to_dict(history):
    return {
        "id": history.id,
        "date": history.date,
        "patient_id": history.patient_id,
        "hospital_id": history.hospital_id,
        "doctor_id": history.doctor_id,
        "room": history.room,
        "data": history.data
    }


# Получение истории посещений и назначений аккаунта
@router.get("/History/Account/{id}", response_model=List[HistoryResponse], status_code=200,
            summary=api_docs["get_history_by_account_id"]["summary"],
            description=api_docs["get_history_by_account_id"]["description"])
@router.get("/History/Account/{id}/", include_in_schema=False, response_model=List[HistoryResponse], status_code=200)
async def get_history_by_account_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token),
    es: AsyncElasticsearch = Depends(get_es)
):
    history_data = await get_history_by_account_id_service(id, user, db)
    
    es_results = await es.search(index="histories", body={"query": {"match": {"account_id": id}}})

    related_data = es_results["hits"]["hits"]

    return {"history": history_data, "related_histories": related_data}

# Получение подробной информации о посещении и назначениях
@router.get("/History/{id}", response_model=HistoryResponse, status_code=200,
            summary=api_docs["get_history_by_id"]["summary"],
            description=api_docs["get_history_by_id"]["description"])
@router.get("/History/{id}/", include_in_schema=False, response_model=HistoryResponse, status_code=200)
async def get_history_by_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token),
    es: AsyncElasticsearch = Depends(get_es)
):
    history_data = await get_history_by_id_service(id, user, db)

    es_results = await es.search(index="histories", body={"query": {"term": {"id": id}}})

    related_data = es_results["hits"]["hits"]

    return {"history": history_data, "related_histories": related_data}

# Создание истории посещения и назначения
@router.post("/History", response_model=HistoryResponse, status_code=201,
             summary=api_docs["create_history"]["summary"],
             description=api_docs["create_history"]["description"])
@router.post("/History/", include_in_schema=False, response_model=HistoryResponse, status_code=200)
async def create_history(
    request: Request,
    history: HistoryCreate,  
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token),
    es: AsyncElasticsearch = Depends(get_es)
):
    history_data = await create_history_service(history, user, db, request)
    
    await es.index(index="histories", id=history_data.id,  document=history_to_dict(history_data))

    return history_data

# Обновление истории посещения и назначения
@router.put("/History/{id}", response_model=HistoryResponse, status_code=200,
            summary=api_docs["update_history"]["summary"],
            description=api_docs["update_history"]["description"])
@router.put("/History/{id}/", include_in_schema=False, response_model=HistoryResponse, status_code=200)
async def update_history(
    request: Request,
    id: int,
    history: HistoryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token),
    es: AsyncElasticsearch = Depends(get_es)
):
    updated_history = await update_history_service(id, user, history, db, request)
    
    await es.update(index="histories", id=id, doc={"doc": history_to_dict(updated_history)})

    return updated_history
