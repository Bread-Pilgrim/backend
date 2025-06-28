from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import auth, test
from app.core.exception import (
    TokenExpiredException,
    UnknowExceptionError,
    exception_handler,
)

origins = [
    "http://localhost:3000",
]

app = FastAPI(
    title="빵지순례 API",
    description="빵지순례 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router
app.include_router(auth.router)
app.include_router(test.router)
# app.include_router(tour.router)
# app.include_router(receipt.router)

# Exception
app.add_exception_handler(UnknowExceptionError, exception_handler)
app.add_exception_handler(TokenExpiredException, exception_handler)

Instrumentator().instrument(app).expose(app)
