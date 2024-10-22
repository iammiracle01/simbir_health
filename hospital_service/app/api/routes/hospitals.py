import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.schemas.hospitals import HospitalCreate, HospitalUpdate, HospitalResponse
from app.services.hospitals import (
    get_hospitals,
    get_hospital_by_id,
    create_hospital,
    update_hospital,
    delete_hospital,
    get_rooms_by_hospital_id
)
from app.db.session import get_db
from app.utils import verify_user_token, verify_admin_user

with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)

router = APIRouter()

# Получение списка больниц
@router.get("", response_model=List[HospitalResponse], status_code=200,
            summary=api_docs["read_hospitals"]["summary"],
            description=api_docs["read_hospitals"]["description"])
@router.get("/", include_in_schema=False, response_model=List[HospitalResponse], status_code=200)
async def read_hospitals(
    from_: int = Query(0, ge=0, description="Начало выборки"),
    count: int = Query(10, ge=1, description="Размер выборки"),
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    return get_hospitals(db, from_=from_, count=count)

# Получить больницу по ID
@router.get("/{id}", response_model=HospitalResponse, status_code=200,
            summary=api_docs["get_hospital"]["summary"],
            description=api_docs["get_hospital"]["description"])
@router.get("/{id}/", include_in_schema=False, response_model=HospitalResponse, status_code=200)
async def get_hospital(
    id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    hospital = get_hospital_by_id(db, hospital_id=id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Больница не найдена")
    return hospital

# Получение списка кабинетов больницы по ID
@router.get("/{id}/Rooms", response_model=List[str], status_code=200,
            summary=api_docs["get_hospital_rooms"]["summary"],
            description=api_docs["get_hospital_rooms"]["description"])
@router.get("/{id}/Rooms/", include_in_schema=False, response_model=List[str], status_code=200)
async def get_hospital_rooms(
    id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    rooms = get_rooms_by_hospital_id(db=db, hospital_id=id)
    if rooms is None:
        raise HTTPException(status_code=404, detail="Больница не найдена")
    return rooms

# Создание записи о новой больнице
@router.post("", status_code=201,
             summary=api_docs["create_new_hospital"]["summary"],
             description=api_docs["create_new_hospital"]["description"])
@router.post("/", include_in_schema=False, status_code=201)
async def create_new_hospital(
    hospital: HospitalCreate, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_user)
):
    create_hospital(db=db, hospital=hospital)
    return JSONResponse(content={"message": "Больница успешно создана"})

# Изменение информации о больнице по ID
@router.put("/{id}", status_code=200,
            summary=api_docs["update_existing_hospital"]["summary"],
            description=api_docs["update_existing_hospital"]["description"])
@router.put("/{id}/", include_in_schema=False, status_code=200)
async def update_existing_hospital(
    id: int, 
    hospital: HospitalUpdate, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_user)
):
    updated_hospital = update_hospital(db, hospital_id=id, hospital=hospital)
    if updated_hospital is None:
        raise HTTPException(status_code=404, detail="Больница не найдена")
    return JSONResponse(content={"message": "Больница успешно обновлена"})

# Мягкое удаление записи о больнице
@router.delete("/{id}", status_code=200,
               summary=api_docs["delete_existing_hospital"]["summary"],
               description=api_docs["delete_existing_hospital"]["description"])
@router.delete("/{id}/", include_in_schema=False, status_code=200)
async def delete_existing_hospital(
    id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_user)
):
    deleted_hospital = delete_hospital(db, hospital_id=id)
    if deleted_hospital is None:
        raise HTTPException(status_code=404, detail="Больница не найдена")
    return JSONResponse(content={"message": "Больница успешно удалена"})  