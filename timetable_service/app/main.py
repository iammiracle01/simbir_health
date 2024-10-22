from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import timetable, appointment
from app.db.database import Base, engine

app = FastAPI(
    title="МИКРОСЕРВИС РАСПИСАНИЯ",
    description="""Timetable microservice отвечает за расписание врачей и 
                    больниц, а также за запись на приём пользователем. 
                    Отправляет запросы в микросервис аккаунтов для 
                    интроспекции токена и проверки существования связанных 
                    сущностей. Отправляет запросы в микросервис больниц для 
                    проверки существования связанных сущностей""",
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

app.include_router(timetable.router, prefix="/api/Timetable", tags=["Timetable"])
app.include_router(appointment.router, prefix="/api/Appointment", tags=["Appointment"])

@app.get("/")
def read_root():
    return {"message": "Timetable Service"}

