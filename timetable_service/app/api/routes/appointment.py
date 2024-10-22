from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json

from app.services.appointment import cancel_appointment
from app.db.session import get_db
from app.utils import verify_user_token


with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)

router = APIRouter()

# Отменить запись на приём
@router.delete("/{id}", status_code=200, 
               summary=api_docs["cancel_appointment"]["summary"],
               description=api_docs["cancel_appointment"]["description"])
@router.delete("/{id}/", include_in_schema=False, status_code=200)
async def cancel_appointment_route(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(verify_user_token)
):
    username = current_user.get("username")  
    user_roles = current_user.get("roles", [])

    cancel_appointment(db=db, appointment_id=id, username=username, user_roles=user_roles)
    
    return JSONResponse(content={"message": "Запись на приём успешно отменена"})
