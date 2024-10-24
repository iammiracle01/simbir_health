import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import Base, engine
from app.api.routes import history
from elasticsearch import AsyncElasticsearch, ConnectionError, NotFoundError

async def wait_for_elasticsearch(es: AsyncElasticsearch, retries: int = 60, delay: int = 5):
    for attempt in range(retries):
        try:
            if await es.ping():
                print(f"Elasticsearch уже доступен после {attempt + 1} попыток.")
                return
        except ConnectionError as e:
            print(f"Попытка {attempt + 1}: Ожидание Elasticsearch...{str(e)}")
        await asyncio.sleep(delay)
    raise RuntimeError("Elasticsearch не стал доступен.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = AsyncElasticsearch(hosts=[{"host": "elasticsearch", "port": 9200, "scheme": "http"}],
                            max_retries=30, retry_on_timeout=True, request_timeout=30)
    try:
        await wait_for_elasticsearch(es)  
        app.state.es = es
        yield
    except ConnectionError as e:
        raise RuntimeError(f"Ошибка подключения к Elasticsearch: {str(e)}")
    finally:
        if es:
            await es.close()

app = FastAPI(
    title="МИКРОСЕРВИС ДОКУМЕНТОВ",
    description="""Document microservice отвечает за историю посещений
                    пользователя. Отправляет запросы в микросервис аккаунтов
                    для интроспекции токена и проверки существования
                    связанных сущностей. Отправляет запросы в микросервис
                    больниц для проверки существования связанных сущностей.""",
    version="1.0.0",
    lifespan=lifespan
)

Base.metadata.create_all(bind=engine)
app.include_router(history.router, prefix="/api", tags=["History"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Document service"}

@app.get("/search/{query}", 
    summary="Поиск документов", 
    description="Поиск документов в Elasticsearch на основе заданного поискового запроса. Ищет совпадения в содержимом документа."
)
async def search_documents(query: str, es: AsyncElasticsearch = Depends(lambda: app.state.es)):
    try:
        response = await es.search(index="histories", body={"query": {"match": {"content": query}}})
        return {"результаты": response["hits"]["hits"]}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Документ не найден: {str(e)}")
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к Elasticsearch: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Неожиданная ошибка: {str(e)}")

@app.post("/index/", 
    summary="Индексирование документа", 
    description="Добавляет новый документ в Elasticsearch с указанными данными."
)
async def index_document(doc: dict, es: AsyncElasticsearch = Depends(lambda: app.state.es)):
    try:
        response = await es.index(index="histories", document=doc)
        return {"результат": "Документ добавлен в индекс", "id": response["_id"]}
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к Elasticsearch: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Неожиданная ошибка: {str(e)}")