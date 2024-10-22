from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.accounts import UpdateAccountRequest, CreateAccountRequest
from passlib.context import CryptContext
from fastapi import  HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Обновить аккаунт
def update_account_service(request: UpdateAccountRequest, current_user: User, db: Session):
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            value = pwd_context.hash(value)
        setattr(current_user, key, value)
    db.commit()
    
   

# Получить все аккаунты (только для администраторов)
def get_accounts_service(from_: int, count: int, db: Session):
    users = db.query(User).filter(User.is_active == True).offset(from_).limit(count).all()
    return users

# Создать аккаунт (только для администраторов)
def create_account_service(request: CreateAccountRequest, db: Session):
    hashed_password = pwd_context.hash(request.password)
    user = User(
        **request.model_dump(exclude={"password"}),  
        password=hashed_password
    )
    db.add(user)
    db.commit()
   

# Обновить аккаунт по ID (только для администраторов)
def update_account_by_id_service(id: int, request: UpdateAccountRequest, db: Session):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            value = pwd_context.hash(value)
        setattr(user, key, value)
    
    db.commit()
    
    

# Удалить аккаунт (только для администраторов)
def delete_account_service(id: int, db: Session):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_active = False  
    db.commit()
    
    
