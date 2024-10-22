from fastapi import FastAPI
from app.api.routes import hospitals
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine

app = FastAPI(
    title="МИКРОСЕРВИС БОЛЬНИЦ",
    description="""Hospital microservice отвечает за данные о больницах,
                    подключенных к системе. Отправляет запросы в микросервис
                    аккаунтов для интроспекции токена.""",
    version="1.0.0",
)
Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hospitals.router, prefix="/api/Hospitals", tags=["Hospitals"])

@app.get("/")
def read_root():
    return {"message": "Hospital Service"}

