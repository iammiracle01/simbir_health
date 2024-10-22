from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.appointment import Appointment

# Отменить запись на приём
def cancel_appointment(db: Session, appointment_id: int, username: str, user_roles: list):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="запись не найдено")

    if "Admin" in user_roles or "Manager" in user_roles:
        db.delete(appointment)
        db.commit()
        return

    if appointment.username != username:
        raise HTTPException(status_code=403, detail="Не разрешено отменять запись")

    db.delete(appointment)
    db.commit()

