from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import auth, preferences, test, tour, users
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

from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback

    print("❌ Unhandled Exception:", traceback.format_exc())  # or logger.error
    return JSONResponse(
        status_code=500,
        content={"message": "서버 내부 오류가 발생했습니다."},
    )


# router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(preferences.router)
app.include_router(test.router)
app.include_router(tour.router)

# Exception
app.add_exception_handler(UnknownExceptionError, exception_handler)
app.add_exception_handler(TokenExpiredException, exception_handler)
app.add_exception_handler(RequestDataMissingException, exception_handler)
app.add_exception_handler(InvalidTokenException, exception_handler)
app.add_exception_handler(DuplicateException, exception_handler)

Instrumentator().instrument(app).expose(app)
