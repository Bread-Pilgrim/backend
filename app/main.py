from fastapi import FastAPI
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
