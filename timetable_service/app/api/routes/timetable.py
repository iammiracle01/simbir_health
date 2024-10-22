import json
from fastapi import APIRouter, Depends, Request
from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.timetable import TimetableCreate, TimetableUpdate, TimetableResponse
from app.schemas.appointment import AppointmentCreate
from app.services.timetable import (
    create_timetable, 
    update_timetable, 
    delete_timetable, 
    get_timetable_by_hospital, 
    get_timetable_by_doctor, 
    get_room_schedule, 
    get_available_appointments,
    book_appointment,
    delete_doctor_timetables,
    delete_hospital_timetables
)
from app.db.session import get_db
from app.utils import verify_admin_or_manager_or_doctor, verify_user_token, verify_admin_or_manager

with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)

router = APIRouter()


# Создание новой записи в расписании
@router.post("", response_model=TimetableResponse, status_code=201, 
             summary=api_docs["create_timetable"]["summary"],
             description=api_docs["create_timetable"]["description"])
@router.post("/", include_in_schema=False, response_model=TimetableResponse, status_code=201)
async def create_timetable_entry(
    request: Request,  
    timetable: TimetableCreate, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_or_manager)
):
    return await create_timetable(db=db, timetable=timetable, request=request)

# Обновление записи расписания
@router.put("/{id}", response_model=TimetableResponse, 
            summary=api_docs["update_timetable"]["summary"],
            description=api_docs["update_timetable"]["description"])
@router.put("/{id}/", include_in_schema=False, response_model=TimetableResponse)
async def update_timetable_entry(
    request: Request,
    id: int, 
    timetable: TimetableUpdate, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_or_manager)
):
    return await update_timetable(db=db, timetable_id=id, timetable=timetable, request=request)

# Удаление записи расписания
@router.delete("/{id}", status_code=200, 
               summary=api_docs["delete_timetable"]["summary"],
               description=api_docs["delete_timetable"]["description"])
@router.delete("/{id}/", include_in_schema=False, status_code=200)
async def delete_timetable_entry(
    id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_or_manager)
):
    delete_timetable(db=db, timetable_id=id)
    return JSONResponse(content={"message": "Запись расписания успешно удалена"})

# Удаление записей расписания доктора
@router.delete("/Doctor/{doctor_id}", status_code=200, 
               summary=api_docs["delete_doctor_schedule"]["summary"],
               description=api_docs["delete_doctor_schedule"]["description"])
@router.delete("/Doctor/{doctor_id}/", include_in_schema=False, status_code=200)
async def delete_doctor_schedule(
    doctor_id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_or_manager)
):
    delete_doctor_timetables(db=db, doctor_id=doctor_id)
    return JSONResponse(content={"message": "Запись расписания доктора успешно удалена"})

# Удаление записей расписания больницы
@router.delete("/Hospital/{hospital_id}", status_code=200, 
               summary=api_docs["delete_hospital_schedule"]["summary"],
               description=api_docs["delete_hospital_schedule"]["description"])
async def delete_hospital_schedule(
    hospital_id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_or_manager)
):
    delete_hospital_timetables(db=db, hospital_id=hospital_id)
    return JSONResponse(content={"message": "Запись расписания больницы успешно удалена"})

# Получение расписания больницы по Id
@router.get("/Hospital/{hospital_id}", response_model=List[TimetableResponse], 
            summary=api_docs["get_hospital_timetables"]["summary"],
            description=api_docs["get_hospital_timetables"]["description"],
            response_description="Список записей расписания больницы.")
@router.get("/Hospital/{hospital_id}/", include_in_schema=False, response_model=List[TimetableResponse])
async def get_hospital_timetables(
    hospital_id: int,
    from_time: str,  
    to_time: str,    
    request: Request,
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    return await get_timetable_by_hospital(db=db, hospital_id=hospital_id, from_time=from_time, to_time=to_time, request=request)

# Получение расписания врача по Id
@router.get("/Doctor/{doctor_id}", response_model=List[TimetableResponse], 
            summary=api_docs["get_doctor_timetables"]["summary"],
            description=api_docs["get_doctor_timetables"]["description"],
            response_description="Список записей расписания врача.")
@router.get("/Doctor/{doctor_id}/", include_in_schema=False, response_model=List[TimetableResponse])
async def get_doctor_timetables(
    doctor_id: int,
    from_time: str,  
    to_time: str,  
    request: Request, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    return await get_timetable_by_doctor(db=db, doctor_id=doctor_id, from_time=from_time, to_time=to_time, request=request)

# Получение расписания кабинета больницы
@router.get("/Hospital/{hospital_id}/Room/{room}", response_model=List[TimetableResponse], 
            summary=api_docs["get_room_schedule"]["summary"],
            description=api_docs["get_room_schedule"]["description"],
            response_description="Список записей расписания кабинета больницы.")
@router.get("/Hospital/{hospital_id}/Room/{room}/", include_in_schema=False, response_model=List[TimetableResponse])
async def get_room_schedule_route(
    hospital_id: int, 
    room: str, 
    from_time: str,  
    to_time: str,    
    request: Request,
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_admin_or_manager_or_doctor)
):
    return await get_room_schedule(db=db, hospital_id=hospital_id, room=room, from_time=from_time, to_time=to_time, request=request)

# Получение свободных талонов на приём.
@router.get("/{id}/Appointments", response_model=List[str], 
            summary=api_docs["get_available_appointments"]["summary"],
            description=api_docs["get_available_appointments"]["description"],
            response_description="Список свободных талонов на приём.")
@router.get("/{id}/Appointments/", include_in_schema=False, response_model=List[str])
async def get_available_appointments_route(
    id: int, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    return get_available_appointments(db=db, timetable_id=id)

# Записаться на приём
@router.post("/{id}/Appointments", status_code=200, 
             summary=api_docs["book_appointment"]["summary"],
             description=api_docs["book_appointment"]["description"])
@router.post("/{id}/Appointments/", include_in_schema=False, status_code=200)
async def book_appointment_route(
    id: int, 
    appointment: AppointmentCreate, 
    db: Session = Depends(get_db), 
    user: dict = Depends(verify_user_token)
):
    username = user.get('username')
    book_appointment(db=db, timetable_id=id, time=appointment.time, username=username)
    
    return JSONResponse(content={"message": "Запись успешно забронирована"})
