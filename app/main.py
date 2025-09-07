import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import (
    auth,
    badge,
    bakery,
    common,
    notice,
    preferences,
    review,
    search,
    test,
    tour,
    users,
)
from app.core.exception import (
    AlreadyDislikedException,
    AlreadyLikedException,
    ConvertImageException,
    DailyReviewLimitExceededExecption,
    DuplicateException,
    InvalidAreaCodeException,
    InvalidImageFileException,
    InvalidSortParameterException,
    InvalidTokenException,
    NotFoundException,
    RequestDataMissingException,
    TokenExpiredException,
    UnknownException,
    UploadImageException,
    WithdrawnMemberException,
    exception_handler,
)

# -------------------- 로깅 설정 --------------------
logging.basicConfig(
    level=logging.DEBUG,  # 필요 시 INFO로 낮출 수 있음
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("bread-api")
# --------------------------------------------------

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


# -------------------- 요청/응답 로깅 --------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"➡️ Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"⬅️ Response: {response.status_code}")
        return response
    except Exception:
        logger.exception("🔥 Unhandled exception")
        raise


# -------------------------------------------------------

# router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(preferences.router)
# app.include_router(test.router)
app.include_router(bakery.router)
app.include_router(tour.router)
app.include_router(common.router)
app.include_router(review.router)
app.include_router(search.router)
app.include_router(badge.router)
app.include_router(notice.router)

# Exception
app.add_exception_handler(UnknownException, exception_handler)
app.add_exception_handler(TokenExpiredException, exception_handler)
app.add_exception_handler(RequestDataMissingException, exception_handler)
app.add_exception_handler(InvalidTokenException, exception_handler)
app.add_exception_handler(DuplicateException, exception_handler)
app.add_exception_handler(NotFoundException, exception_handler)
app.add_exception_handler(InvalidAreaCodeException, exception_handler)
app.add_exception_handler(InvalidSortParameterException, exception_handler)
app.add_exception_handler(InvalidImageFileException, exception_handler)
app.add_exception_handler(ConvertImageException, exception_handler)
app.add_exception_handler(UploadImageException, exception_handler)
app.add_exception_handler(DailyReviewLimitExceededExecption, exception_handler)
app.add_exception_handler(AlreadyLikedException, exception_handler)
app.add_exception_handler(AlreadyDislikedException, exception_handler)
app.add_exception_handler(WithdrawnMemberException, exception_handler)

Instrumentator().instrument(app).expose(app)
