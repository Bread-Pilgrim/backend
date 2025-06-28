from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/test", tags=["test"])


@router.get("")
async def test_api():
    return {"test": "정상적으로 됩니다."}


@router.get("/ping-db")
async def ping_db(db=Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"db_connected": result.scalar() == 1}
