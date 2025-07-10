from sqlalchemy.orm.session import Session

from app.repositories.common_repo import CommonRepository


class CommonService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_area_code(self):
        """지역코드 조회하는 서비스 로직."""

        return await CommonRepository(db=self.db).get_commercial_area_code()
