from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, Request
from app.models.timetable import Timetable
from app.models.appointment import Appointment
from app.schemas.timetable import TimetableCreate, TimetableUpdate
from app.utils import get_doctor_by_id, get_hospital_by_id
from datetime import datetime, timedelta
from dateutil import parser 
import pytz 

# Создание новой записи в расписании
async def create_timetable(db: Session, timetable: TimetableCreate, request: Request):
    hospital_response = await get_hospital_by_id(timetable.hospital_id, request=request)
    if not hospital_response:
        raise HTTPException(status_code=400, detail="Недействительный ID больницы")
    
    available_rooms = hospital_response.get('rooms', [])
    if timetable.room not in available_rooms:
        raise HTTPException(status_code=400, detail="Неверная комната. Комната не принадлежит указанной больнице")
    
    doctor_response = await get_doctor_by_id(timetable.doctor_id, request=request)
    if not doctor_response:
        raise HTTPException(status_code=400, detail="Недействительный ID доктора")
    
    if timetable.from_time.tzinfo is None:
        timetable.from_time = timetable.from_time.replace(tzinfo=pytz.UTC)
    if timetable.to_time.tzinfo is None:
        timetable.to_time = timetable.to_time.replace(tzinfo=pytz.UTC)

    if timetable.from_time >= timetable.to_time:
        raise HTTPException(status_code=400, detail="Недействительный диапазон времени")
    
    time_difference = (timetable.to_time - timetable.from_time).total_seconds() / 60
    if time_difference > 720 or time_difference % 30 != 0:
        raise HTTPException(status_code=400, detail="Недействительный диапазон времени или продолжительность")
    
    check_if_timetable_exists = (
        db.query(Timetable)
        .filter(
            Timetable.room == timetable.room,
            Timetable.hospital_id == timetable.hospital_id,
            Timetable.from_time < timetable.to_time,
            Timetable.to_time > timetable.from_time
        )
        .first()
    )
    
    if check_if_timetable_exists:
        raise HTTPException(status_code=400, detail="Существует конфликт расписания с этой комнатой в указанный промежуток времени.")
    
    db_timetable = Timetable(**timetable.model_dump())
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    
    return db_timetable


# Обновление записи расписания
async def update_timetable(db: Session, timetable_id: int, timetable: TimetableUpdate, request: Request):
    db_timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    
    if not db_timetable:
        raise HTTPException(status_code=404, detail="Запись расписания не найдена")
    
    if db.query(Appointment).filter(Appointment.timetable_id == timetable_id).count() > 0:
        raise HTTPException(status_code=400, detail="Нельзя изменить, есть записавшиеся на прием")

    # Проверка если ID больницы изменился 
    hospital_changed = timetable.hospital_id and timetable.hospital_id != db_timetable.hospital_id
    
    if hospital_changed or timetable.room:
        # Получение rooms в больнице
        hospital_id = timetable.hospital_id if hospital_changed else db_timetable.hospital_id
        hospital_response = await get_hospital_by_id(hospital_id, request=request)
        
        if not hospital_response or 'rooms' not in hospital_response:
            raise HTTPException(status_code=400, detail="Недействительный ID больницы")

        available_rooms = hospital_response['rooms']
        
        # Проверка существования указанной rooms
        if timetable.room and timetable.room not in available_rooms:
            raise HTTPException(status_code=400, detail="Неверная комната. Комната не принадлежит указанной больнице")

    # Проверка если ID доктора изменился 
    if timetable.doctor_id and timetable.doctor_id != db_timetable.doctor_id:
        if not await get_doctor_by_id(timetable.doctor_id, request=request):
            raise HTTPException(status_code=400, detail="Недействительный ID доктора")

    # Проверка временного диапазона
    from_time, to_time = timetable.from_time, timetable.to_time

    if from_time is not None:
        if from_time.tzinfo is None:
            from_time = from_time.replace(tzinfo=pytz.UTC)

    if to_time is not None:
        if to_time.tzinfo is None:
            to_time = to_time.replace(tzinfo=pytz.UTC)

    if from_time and to_time:
        if from_time >= to_time:
            raise HTTPException(status_code=400, detail="Недействительный диапазон времени")
                
        time_difference = (to_time - from_time).total_seconds() / 60
        if time_difference > 720 or time_difference % 30 != 0:
            raise HTTPException(status_code=400, detail="Недействительный диапазон времени или продолжительность")

    for key, value in timetable.model_dump(exclude_unset=True).items():
        setattr(db_timetable, key, value)

    db.commit()
    db.refresh(db_timetable)

    return db_timetable



# Удаление записи расписания
def delete_timetable(db: Session, timetable_id: int):
    db_timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not db_timetable:
        raise HTTPException(status_code=404, detail="Запись расписания не найдена")
    
    db.delete(db_timetable)
    db.commit()

#  Удаление записей расписания доктора
def delete_doctor_timetables(db: Session, doctor_id: int):
    db_timetables = db.query(Timetable).filter(Timetable.doctor_id == doctor_id).all()
    if not db_timetables:
        raise HTTPException(status_code=404, detail="Нет записей расписания для указанного врача")

    for timetable in db_timetables:
        db.delete(timetable)
    
    db.commit()

# Удаление записей расписания больницы
def delete_hospital_timetables(db: Session, hospital_id: int):
    db_timetables = db.query(Timetable).filter(Timetable.hospital_id == hospital_id).all()
    if not db_timetables:
        raise HTTPException(status_code=404, detail="Нет записей расписания для указанной больницы")

    for timetable in db_timetables:
        db.delete(timetable)
    
    db.commit()

# Получение расписания больницы по Id
async def get_timetable_by_hospital(db: Session, hospital_id: int, from_time: str, to_time: str, request: Request):
    hospital_response = await get_hospital_by_id(hospital_id, request=request)
    if not hospital_response:
        raise HTTPException(status_code=400, detail="Недействительный ID больницы")
    
    try:
        from_time_dt = parser.isoparse(from_time)
        to_time_dt = parser.isoparse(to_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="from_time и to_time должны быть в формате ISO 8601.")


    timetables = db.query(Timetable).options(joinedload(Timetable.appointments)).filter(
        Timetable.hospital_id == hospital_id,
        Timetable.from_time >= from_time_dt,
        Timetable.to_time <= to_time_dt
    ).all()

    return timetables

# Получение расписания врача по Id
async def get_timetable_by_doctor(db: Session, doctor_id: int, from_time: str, to_time: str, request: Request):
    doctor_response = await get_doctor_by_id(doctor_id, request=request)
    if not doctor_response:
        raise HTTPException(status_code=400, detail="Недействительный ID врача")
    
    try:
        from_time_dt = parser.isoparse(from_time)
        to_time_dt = parser.isoparse(to_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="from_time и to_time должны быть в формате ISO 8601.")

    timetables = db.query(Timetable).options(joinedload(Timetable.appointments)).filter(
        Timetable.doctor_id == doctor_id,
        Timetable.from_time >= from_time_dt,
        Timetable.to_time <= to_time_dt
    ).all()
    
    return timetables

# Получение расписания кабинета больницы
async def get_room_schedule(db: Session, hospital_id: int, room: str, from_time: str, to_time: str, request: Request):
    try:
        from_time_dt = parser.isoparse(from_time)
        to_time_dt = parser.isoparse(to_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="from_time и to_time должны быть в формате ISO 8601.")
    
    hospital_response = await get_hospital_by_id(hospital_id, request=request)
    if not hospital_response:
        raise HTTPException(status_code=400, detail="Недействительный ID больницы")
    
    available_rooms = hospital_response.get('rooms', [])
    if room not in available_rooms:
        raise HTTPException(status_code=400, detail="Неверная комната. Комната не принадлежит указанной больнице")

    timetables = db.query(Timetable).options(joinedload(Timetable.appointments)).filter(
        Timetable.hospital_id == hospital_id,
        Timetable.room == room,
        Timetable.from_time >= from_time_dt,
        Timetable.to_time <= to_time_dt
    ).all()

    if not timetables:
        raise HTTPException(status_code=404, detail="Расписания для этой комнаты не найдены")

    return timetables

# Получение свободных талонов на приём.
def get_available_appointments(db: Session, timetable_id: int):
    db_timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not db_timetable:
        raise HTTPException(status_code=404, detail="Запись расписания не найдена")

    available_slots = []
    current_time = db_timetable.from_time

    while current_time < db_timetable.to_time:
        if not db.query(Appointment).filter(
            Appointment.timetable_id == timetable_id,
            Appointment.time == current_time
        ).first():
            available_slots.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))
        
        current_time += timedelta(minutes=30)

    return available_slots

# Записаться на приём
def book_appointment(db: Session, timetable_id: int, time: datetime, username: str):
    db_timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not db_timetable:
        raise HTTPException(status_code=404, detail="Запись расписания не найдена")
    
    if db_timetable.from_time.tzinfo is None:
        db_timetable.from_time = db_timetable.from_time.replace(tzinfo=pytz.UTC)
    if db_timetable.to_time.tzinfo is None:
        db_timetable.to_time = db_timetable.to_time.replace(tzinfo=pytz.UTC)
    
    time = time.astimezone(pytz.UTC)

    available_slots = get_available_appointments(db, timetable_id)
    
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')

    if time_str not in available_slots:
        raise HTTPException(status_code=400, detail="Время записи не доступно")

    if db.query(Appointment).filter(Appointment.timetable_id == timetable_id, Appointment.time == time).first():
        raise HTTPException(status_code=400, detail="Слот для записи уже забронирован")

    appointment = Appointment(timetable_id=timetable_id, time=time, username=username)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)





  

