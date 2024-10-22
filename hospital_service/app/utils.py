
import httpx
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from app.core.config import settings

ACCOUNT_SERVICE_URL = settings.ACCOUNT_SERVICE_URL
bearer_scheme = HTTPBearer() 

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


async def verify_admin_user(token: str = Depends(verify_user_token)):
    if "Admin" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Не авторизован, только администраторы")
    return token
