from typing import List
from sqlalchemy.orm import Session
from app.models.history import History
from app.schemas.history import HistoryCreate, HistoryUpdate, HistoryResponse
from app.utils import get_doctor_by_id, get_hospital_by_id
from fastapi import HTTPException, Request

# Получение истории посещений и назначений аккаунта
async def get_history_by_account_id_service(id: int, user: dict, db: Session) -> List[HistoryResponse]:

    user_roles = user.get("roles", [])
    user_id = user.get("user_id")

    if id != user_id and "Doctor" not in user_roles:
        raise HTTPException(status_code=403, detail="Не авторизован: только врач или пациент могут просматривать эту историю")
    
    histories = db.query(History).filter(History.patient_id == id).all()
    
    if not histories:
        raise HTTPException(status_code=404, detail="История не найдена")
    
    return histories

# Получение подробной информации о посещении и назначениях
async def get_history_by_id_service(id: int, user: dict, db: Session) -> HistoryResponse:
    user_roles = user.get("roles", [])
    user_id = user.get("user_id")

    history = db.query(History).filter(History.id == id).first()
    if not history:
        raise HTTPException(status_code=404, detail="История не найдена")

    if history.patient_id != user_id and "Doctor" not in user_roles:
        raise HTTPException(status_code=403, detail="Не авторизован: только врач или пациент могут просматривать эту историю")

    return history


# Создание истории посещения и назначения
async def create_history_service(history: HistoryCreate, user: dict, db: Session, request: Request) -> HistoryResponse:
    doctor_info = await get_doctor_by_id(history.doctor_id, request)
    if not doctor_info:
        raise HTTPException(status_code=400, detail="Недействительный ID врача")

    hospital_info = await get_hospital_by_id(history.hospital_id, request)
    if not hospital_info:
        raise HTTPException(status_code=400, detail="Недействительный ID больницы")

    available_rooms = hospital_info.get('rooms', [])
    if history.room not in available_rooms:
        raise HTTPException(status_code=400, detail="Неверная комната. Комната не принадлежит указанной больнице")

    user_roles = user.get("roles", [])
    user_id = user.get("user_id")

    if any(role in user_roles for role in ["Admin", "Manager", "Doctor"]):
        pass  

    elif "User" in user_roles:
        if history.patient_id != user_id:
            raise HTTPException(status_code=403, detail="Не авторизован: пациент должен соответствовать текущему пользователю")
    
    else:
        raise HTTPException(status_code=403, detail="Не авторизован, только администраторы, менеджеры или врачи могут создавать истории")

    new_history = History(
        date=history.date,
        patient_id=history.patient_id,
        hospital_id=history.hospital_id,
        doctor_id=history.doctor_id,
        room=history.room,
        data=history.data
    )

    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return new_history


# Обновление истории посещения и назначения
async def update_history_service(id: int, history: HistoryUpdate, user:dict, db: Session, request: Request) -> HistoryResponse:
    existing_history = db.query(History).filter(History.id == id).first()
    if not existing_history:
        raise HTTPException(status_code=404, detail="История не найдена")
    
    if history.doctor_id:
        doctor_info = await get_doctor_by_id(history.doctor_id, request)
        if not doctor_info:
            raise HTTPException(status_code=400, detail="Недействительный ID врача")
    
    if history.hospital_id:
        hospital_info = await get_hospital_by_id(history.hospital_id, request)
        if not hospital_info:
            raise HTTPException(status_code=400, detail="Недействительный ID больницы")
        
        available_rooms = hospital_info.get('rooms', [])
        if history.room and history.room not in available_rooms:
            raise HTTPException(status_code=400, detail="Неверная комната. Комната не принадлежит указанной больнице")
        
    user_roles = user.get("roles", [])
    user_id = user.get("user_id") 
    
    if any(role in user_roles for role in ["Admin", "Manager", "Doctor"]):
        pass  

    elif "User" in user_roles:
        if history.patient_id != user_id:
            raise HTTPException(status_code=403, detail="Не авторизован: пациент должен соответствовать текущему пользователю")
    
    else:
        raise HTTPException(status_code=403, detail="Не авторизован, только администраторы, менеджеры или врачи могут создавать истории")


    existing_history.date = history.date
    existing_history.patient_id = history.patient_id
    existing_history.hospital_id = history.hospital_id
    existing_history.doctor_id = history.doctor_id
    existing_history.room = history.room
    existing_history.data = history.data

    db.commit()
    db.refresh(existing_history)

    return existing_history


