from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from fastapi import Depends, HTTPException, Request, Security
from app.core.config import settings

ACCOUNT_SERVICE_URL = settings.ACCOUNT_SERVICE_URL
HOSPITAL_SERVICE_URL = settings.HOSPITAL_SERVICE_URL

bearer_scheme = HTTPBearer() 

# получить_токен_доступа
async def get_access_token(request: Request, access_token: str = Security(bearer_scheme)):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Не авторизовано")
    
    try:
        token_type, access_token = authorization.split()
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Недействительный токен")
        return access_token
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный формат авторизации")

# проверить_токен_пользователя
async def verify_user_token(
    token: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не авторизовано",
        headers={"Authorization": "Bearer"},
    )

    if not token:
        raise credentials_exception
    
    access_token = token.credentials 

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/api/Authentication/Validate",
                params={"accessToken": access_token},
                follow_redirects=True  
            )
            response.raise_for_status()  
            return response.json() 
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Недействительный или просроченный токен")
        except Exception:
            raise HTTPException(status_code=500, detail="Ошибка при проверке токена")

# Получить информацию о докторе
async def get_doctor_by_id(doctor_id: int, request: Request, access_token: str = Security(bearer_scheme)) -> dict:
    access_token = await get_access_token(request, access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/api/Doctors/{doctor_id}",
                headers=headers,
                follow_redirects=True
            )
            response.raise_for_status() 
            return response.json() 
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Доктор не найден")
            else:
                raise HTTPException(status_code=e.response.status_code, detail="Ошибка доступа к службе доктора или недействительный ID доктора")
        except Exception:
            raise HTTPException(status_code=500, detail="Ошибка при запросе к службе доктора")

# Получите информацию о больнице с проверкой токена
async def get_hospital_by_id(hospital_id: int, request: Request, access_token: str = Security(bearer_scheme)):
    access_token = await get_access_token(request, access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{HOSPITAL_SERVICE_URL}/api/Hospitals/{hospital_id}", 
                headers=headers, 
                follow_redirects=True  
            )
            response.raise_for_status() 
            return response.json()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Ошибка доступа к службе больницы или недействительный ID больницы")
        except Exception:
            raise HTTPException(status_code=500, detail="Ошибка при запросе к службе больницы")


# проверить_администратора_или_менеджера
async def verify_admin_or_manager(token: str = Depends(verify_user_token)):
    if "Admin" not in token.get("roles", []) and "Manager" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Не авторизован, только администраторы или менеджеры")
    return token

# проверить_администратора_или_менеджера_или_доктора
async def verify_admin_or_manager_or_doctor(request: Request, token: str = Depends(verify_user_token)):
    if "Admin" not in token.get("roles", []) and "Manager" not in token.get("roles", []) and "Doctor" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Не авторизован, только администраторы, менеджеры или врачи")
    return token