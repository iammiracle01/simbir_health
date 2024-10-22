import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.utils import verify_admin_user, verify_user_token
from app.schemas.accounts import AccountResponse, UpdateAccountRequest, AdminAccountResponse, CreateAccountRequest
from app.services.accounts import (
    update_account_service, 
    get_accounts_service, 
    create_account_service, 
    update_account_by_id_service,
    delete_account_service, 
)
from app.db.session import get_db
from app.models.user import User

with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)

router = APIRouter()


# Получить текущего пользователя
@router.get("/Me", response_model=AccountResponse, status_code=200,
            summary=api_docs["get_me"]["summary"],
            description=api_docs["get_me"]["description"])
@router.get("/Me/", include_in_schema=False, response_model=AccountResponse, status_code=200)
async def get_me(user: dict = Depends(verify_user_token), db: Session = Depends(get_db)):
    username = user.get("username") 
    current_user = db.query(User).filter(User.username == username).first()  

    if not current_user:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    
    return current_user


# Обновить аккаунт
@router.put("/Update", status_code=200,
            summary=api_docs["update_account_route"]["summary"],
            description=api_docs["update_account_route"]["description"])
@router.put("/Update/", include_in_schema=False, status_code=200)
async def update_account_route(
    request: UpdateAccountRequest,
    user: dict = Depends(verify_user_token),
    db: Session = Depends(get_db)
):
    username = user.get("username") 
    current_user = db.query(User).filter(User.username == username).first()  

    if not current_user:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")

    update_account_service(request, current_user, db)
    return JSONResponse(content={"message": "Аккаунт успешно обновлен"})


# Получить все аккаунты (только для администраторов)
@router.get("/", response_model=List[AdminAccountResponse], status_code=200,
            summary=api_docs["get_accounts"]["summary"],
            description=api_docs["get_accounts"]["description"])
@router.get("", include_in_schema=False, response_model=List[AdminAccountResponse], status_code=200)
async def get_accounts(
    from_: int = Query(0, ge=0, description="Начало выборки"),
    count: int = Query(10, ge=1, description="Размер выборки"),
    user: dict = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    return get_accounts_service(from_, count, db)


# Создать аккаунт (только для администраторов)
@router.post("/", status_code=200,
             summary=api_docs["create_account"]["summary"],
             description=api_docs["create_account"]["description"])
@router.post("", include_in_schema=False, status_code=200)
async def create_account(
    request: CreateAccountRequest,
    user: dict = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    create_account_service(request, db)
    return JSONResponse(content={"message": "Аккаунт успешно создан"})


# Обновить аккаунт по ID (только для администраторов)
@router.put("/{id}", status_code=200,
            summary=api_docs["update_account_by_id"]["summary"],
            description=api_docs["update_account_by_id"]["description"])
@router.put("/{id}/", include_in_schema=False, status_code=200)
async def update_account_by_id(
    id: int,
    request: CreateAccountRequest,
    user: dict = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    update_account_by_id_service(id, request, db)
    return JSONResponse(content={"message": "Аккаунт успешно обновлен"})


# Удалить аккаунт (только для администраторов)
@router.delete("/{id}", status_code=200,
               summary=api_docs["delete_account"]["summary"],
               description=api_docs["delete_account"]["description"])
@router.delete("/{id}", include_in_schema=False, status_code=200)
async def delete_account(
    id: int,
    user: dict = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    delete_account_service(id, db)
    return JSONResponse(content={"message": "Аккаунт успешно удален"})