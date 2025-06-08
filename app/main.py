from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="빵지순례 API",
    description="빵지순례 API",
)

Instrumentator().instrument(app).expose(app)
