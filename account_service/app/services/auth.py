from datetime import datetime, timezone
import time
from sqlalchemy.orm import Session
from fastapi import HTTPException, Response
from jose import ExpiredSignatureError, jwt, JWTError
from passlib.context import CryptContext
from app.token_blacklist import add_to_blacklist, is_blacklisted
from app.models.user import User
from app.schemas.auth import SignInRequest, SignUpRequest
from app.utils import create_access_token, create_refresh_token
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Зарегистрироваться
def sign_up_service(request: SignUpRequest, db: Session):
    user_exists = db.query(User).filter(User.username == request.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")

    hashed_password = pwd_context.hash(request.password)

    new_user = User(
        **request.model_dump(exclude={"password"}),  
        password=hashed_password,
        roles=["User"],
    )

    db.add(new_user)
    db.commit()



# Войти
def sign_in_service(request: SignInRequest, response: Response, db: Session):
    user = db.query(User).filter(User.username == request.username, User.is_active == True).first()

    if not user:
        raise HTTPException(status_code=404, detail="Имя пользователя не найдено")

    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Неверный пароль")

    access_token = create_access_token(data={"username": user.username, "roles": user.roles, "user_id": user.id})
    refresh_token = create_refresh_token(data={"username": user.username, "roles": user.roles, "user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

# Выйти
def sign_out_service(access_token: str, db: Session):
    try:
        token_info = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        expiration = token_info.get("exp")

        if expiration is None:
            raise HTTPException(status_code=400, detail="Невозможно определить срок действия токена")
        
        add_to_blacklist(access_token, datetime.fromtimestamp(expiration, tz=timezone.utc), db)
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен уже истек")
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен")



# Проверка Token (интроспекция токена)
def validate_token_service(access_token: str, db: Session):
    if access_token is None:
        raise HTTPException(status_code=401, detail="access token не найден")

    try:
        token_info = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if is_blacklisted(access_token, db):
            raise HTTPException(status_code=401, detail="Недействительный Token доступа")

        if token_info.get("exp") and token_info["exp"] < int(time.time()):
            raise HTTPException(status_code=401, detail="Срок действия Token истек")

        return token_info

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия Token истек")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный Token доступа")

# Обновить Token
async def refresh_token_service(refresh_token: str):
    credentials_exception = HTTPException(
    status_code=401,
    detail={"message": "Не авторизовано"}
    )

    if refresh_token is None:
        raise HTTPException(status_code=400, detail="refresh_token не предоставлен")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("username")
        roles: list = payload.get("roles", [])
        
        if username is None:
            raise credentials_exception
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия refresh_token истек")
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Неверный refresh_token"
        )


    access_token = create_access_token(data={"username": username, "roles": roles})
    new_refresh_token = create_refresh_token(data={"username": username, "roles": roles})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
    }