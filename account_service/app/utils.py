from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session
from app.token_blacklist import is_blacklisted
from app.core.config import settings
from app.db.session import get_db

bearer_scheme = HTTPBearer() 

# Создать access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc).timestamp()  
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Создать refresh token
def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)  
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc).timestamp()  
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# Проверить авторизованного пользователя
async def verify_user_token(token: HTTPAuthorizationCredentials = Security(bearer_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не авторизовано",
        headers={"Authorization": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        access_token = token.credentials

        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("username")

        if is_blacklisted(access_token, db):
            raise HTTPException(status_code=401, detail="Token недействителен")

        if username is None:
            raise credentials_exception

        return payload  

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия Token истек")
    except JWTError:
        raise credentials_exception
    
# Проверить роль пользователя
def check_role(roles: List[str], required_roles: List[str]):
    if not any(role in roles for role in required_roles):
        raise HTTPException(status_code=403, detail="Не авторизовано, только администраторы")

# Получить текущего администратора
async def verify_admin_user(
    token: str = Depends(verify_user_token), 
    db: Session = Depends(get_db)
):
    
    if "Admin" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Не авторизован, только администраторы")
    return token
