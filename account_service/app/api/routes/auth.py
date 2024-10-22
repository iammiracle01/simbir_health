from datetime import datetime, timezone
import json
from fastapi import APIRouter, Depends, Response, Security
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.auth import RefreshTokenRequest, SignInRequest, TokenResponse, SignUpRequest
from app.services.auth import sign_in_service, refresh_token_service, sign_out_service, validate_token_service, sign_up_service
from app.db.session import get_db
from app.core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

with open("app/docs/api_docs.json", "r", encoding="utf-8") as f:
    api_docs = json.load(f)
    
router = APIRouter()
bearer_scheme = HTTPBearer() 

# Зарегистрироваться
@router.post("/SignUp", status_code=200,
             summary=api_docs["sign_up"]["summary"],
             description=api_docs["sign_up"]["description"])
@router.post("/SignUp/", include_in_schema=False, status_code=200)
async def sign_up(request: SignUpRequest, db: Session = Depends(get_db)):
    sign_up_service(request, db)
    return JSONResponse(content={"message": "Аккаунт успешно создан"})

# Войти
@router.post("/SignIn", response_model=TokenResponse, status_code=200,
             summary=api_docs["sign_in"]["summary"],
             description=api_docs["sign_in"]["description"])
@router.post("/SignIn/", include_in_schema=False, response_model=TokenResponse, status_code=200)
async def sign_in(response: Response, request: SignInRequest, db: Session = Depends(get_db)):
    return sign_in_service(request, response, db)

# Выйти
@router.post("/SignOut", status_code=200,
             summary=api_docs["sign_out"]["summary"],
             description=api_docs["sign_out"]["description"])
@router.post("/SignOut/", include_in_schema=False, status_code=200)
async def sign_out(token: HTTPAuthorizationCredentials = Security(bearer_scheme), db: Session = Depends(get_db)):
    access_token = token.credentials
    sign_out_service(access_token, db)
    return JSONResponse(content={"message": "Выход успешен"})

# Проверка Token (интроспекция токена)
@router.get("/Validate", status_code=200,
            summary=api_docs["validate_token"]["summary"],
            description=api_docs["validate_token"]["description"])
@router.get("/Validate/", include_in_schema=False, status_code=200)
async def validate_token(accessToken: str, db: Session = Depends(get_db)):
    token_info = validate_token_service(accessToken, db)
    return JSONResponse(content={
        "username": token_info.get("username"),
        "user_id": token_info.get("user_id"),
        "roles": token_info.get("roles", []),
        "issued_at": datetime.fromtimestamp(token_info.get("iat", 0), tz=timezone.utc).isoformat() + "Z",
        "expires_at": datetime.fromtimestamp(token_info.get("exp", 0), tz=timezone.utc).isoformat() + "Z",
        "token_is_valid": True
    })

# Обновить Token
@router.post("/Refresh", response_model=TokenResponse, status_code=200,
             summary=api_docs["refresh_token"]["summary"],
             description=api_docs["refresh_token"]["description"])
@router.post("/Refresh/", include_in_schema=False, response_model=TokenResponse, status_code=200)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    return await refresh_token_service(request.refreshToken)