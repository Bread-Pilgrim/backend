from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import auth, bakery, common, preferences, test, tour, users
from app.core.exception import (
    DuplicateException,
    InvalidTokenException,
    RequestDataMissingException,
    TokenExpiredException,
    UnknownExceptionError,
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
app.include_router(users.router)
app.include_router(preferences.router)
# app.include_router(test.router)
app.include_router(bakery.router)
app.include_router(tour.router)
app.include_router(common.router)

# Exception
app.add_exception_handler(UnknownExceptionError, exception_handler)
app.add_exception_handler(TokenExpiredException, exception_handler)
app.add_exception_handler(RequestDataMissingException, exception_handler)
app.add_exception_handler(InvalidTokenException, exception_handler)
app.add_exception_handler(DuplicateException, exception_handler)

Instrumentator().instrument(app).expose(app)
