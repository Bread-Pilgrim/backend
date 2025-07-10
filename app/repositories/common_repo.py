from sqlalchemy.orm.session import Session

from app.model.area import CommercialAreas
from app.schema.common import AreaCodeModel


class CommonRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_commercial_area_code(self):
        """지역코드 조회하는 쿼리."""
        res = self.db.query(CommercialAreas).all()
        return (
            [AreaCodeModel(area_code=r.id, area_name=r.name) for r in res]
            if res
            else []
        )
