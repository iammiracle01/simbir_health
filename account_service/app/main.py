from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.api.routes import auth, accounts, doctors
from app.db.database import Base, engine
from app.db.session import get_db
from app.models.user import User
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

app = FastAPI(
    title="МИКРОСЕРВИС АККАУНТОВ",
    description="""Account microservice отвечает за авторизацию и данные о
                    пользователях. Все остальные сервисы зависят от него, ведь
                    именно он выпускает JWT токен и проводит интроспекцию.""",
    version="1.0.0",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/Authentication", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/Accounts", tags=["Accounts"])
app.include_router(doctors.router, prefix="/api", tags=["Doctors"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

default_accounts = [
    {"lastName": "Admin", "firstName": "Admin", "username": "admin", "password": "admin", "roles": ["Admin"]},
    {"lastName": "Manager", "firstName": "Manager", "username": "manager", "password": "manager", "roles": ["Manager"]},
    {"lastName": "Doctor", "firstName": "Doctor", "username": "doctor", "password": "doctor", "roles": ["Doctor"]},
    {"lastName": "User", "firstName": "User", "username": "user", "password": "user", "roles": ["User"]},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = next(get_db())
    for account in default_accounts:
        existing_user = db.query(User).filter(User.username == account["username"]).first()
        if existing_user is None:
            hashed_password = pwd_context.hash(account["password"])
            user = User(
                lastName=account["lastName"],
                firstName=account["firstName"],
                username=account["username"],
                password=hashed_password,
                roles=account["roles"],
            )
            db.add(user)
    db.commit()
    db.close()

    yield  

@app.get("/")
def read_root():
    return {"message": "Account Service"}

