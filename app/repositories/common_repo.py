from sqlalchemy.orm.session import Session

from app.model.area import CommercialAreas
from app.schema.common import AreaCode


class CommonRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_commercial_area_code(self):
        """지역코드 조회하는 쿼리."""
        res = self.db.query(CommercialAreas).order_by(CommercialAreas.ordering).all()

        return [AreaCode(area_code=r.id, area_name=r.name) for r in res] if res else []
