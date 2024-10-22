from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.hospitals import Hospital
from app.schemas.hospitals import HospitalCreate, HospitalUpdate

# Получение списка больниц
def get_hospitals(db: Session, from_: int = 0, count: int = 10):
    return db.query(Hospital).filter(Hospital.is_active == True).offset(from_).limit(count).all()

# Получить больницу по ID
def get_hospital_by_id(db: Session, hospital_id: int):
    db_hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Больница не найдена")
    return db_hospital

# Получение списка кабинетов больницы по Id
def get_rooms_by_hospital_id(db: Session, hospital_id: int):
    db_hospital = get_hospital_by_id(db, hospital_id)  
    return db_hospital.rooms if db_hospital else None

# Создание записи о новой больнице
def create_hospital(db: Session, hospital: HospitalCreate):
    db_hospital = Hospital(**hospital.model_dump(exclude_unset=True))
    db.add(db_hospital)
    db.commit()
    

# Изменение информации о больнице по Id
def update_hospital(db: Session, hospital_id: int, hospital: HospitalUpdate):
    db_hospital = get_hospital_by_id(db, hospital_id)
    if not db_hospital:
        return None 
    for key, value in hospital.model_dump(exclude_unset=True).items():
        setattr(db_hospital, key, value)
    db.commit()
    db.refresh(db_hospital) 
    return db_hospital


# Мягкое удаление записи о больнице
def delete_hospital(db: Session, hospital_id: int):
    db_hospital = get_hospital_by_id(db, hospital_id)
    if db_hospital is not None:
       db_hospital.is_active = False  
       db.commit() 
       db.refresh(db_hospital)
                
       return db_hospital
    return None 
   
