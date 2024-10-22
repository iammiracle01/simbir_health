from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import HTTPException
from typing import Optional
from sqlalchemy import or_

# Получить всех докторы
def get_doctors_service(db: Session, name_filter: Optional[str] = None, from_: int = 0, count: int = 10):
    query = db.query(User).filter(User.roles.any('Doctor'), User.is_active == True)
    if name_filter:
        query = query.filter(
            or_(User.firstName.ilike(f"%{name_filter}%"), User.lastName.ilike(f"%{name_filter}%"))
        )
    return query.offset(from_).limit(count).all()

# Получить доктор по ID
def get_doctor_by_id_service(db: Session, doctor_id: int):
    doctor = db.query(User).filter(User.id == doctor_id, User.roles.any('Doctor'), User.is_active == True).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Доктор не найден")
    return doctor