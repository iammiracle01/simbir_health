import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils import verify_user_token
from app.db.session import get_db
from app.schemas.doctors import DoctorResponse
from app.services.doctors import get_doctors_service, get_doctor_by_id_service

with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)
    
router = APIRouter()

# Получить список докторов
@router.get("/Doctors", response_model=List[DoctorResponse], status_code=200,
             summary=api_docs["get_doctors"]["summary"],
             description=api_docs["get_doctors"]["description"])
@router.get("/Doctors/", include_in_schema=False, response_model=List[DoctorResponse], status_code=200)
async def get_doctors(
    nameFilter: Optional[str] = Query(None, description="Фильтр имени"),
    from_: int = Query(0, ge=0, description="Начало выборки"),
    count: int = Query(10, ge=1, description="Размер выборки"),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token)
):
    doctors = get_doctors_service(db, name_filter=nameFilter, from_=from_, count=count)
    return doctors

# Получить доктора по ID
@router.get("/Doctors/{id}", response_model=DoctorResponse, status_code=200,
             summary=api_docs["get_doctor_by_id"]["summary"],
             description=api_docs["get_doctor_by_id"]["description"])
@router.get("/Doctors/{id}/", include_in_schema=False, response_model=DoctorResponse, status_code=200)
async def get_doctor_by_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_user_token),
):
    doctor = get_doctor_by_id_service(db, doctor_id=id)
    return doctor