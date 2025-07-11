from collections import defaultdict
from typing import List

from sqlalchemy.orm.session import Session

from app.core.exception import UnknownExceptionError
from app.model.users import Preferences
from app.schema.preferences import PreferenceResponseModel, PreferenceType


class PreferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def convert_list_to_model(rows) -> PreferenceResponseModel:
        """SQL Row Result PreferenceResponseModel에 맞게 변환하는 메소드."""

        buckets: dict[str, List[PreferenceType]] = defaultdict(list)
        for row in rows:
            buckets[row.type].append(PreferenceType(id=row.id, name=row.name))

        return PreferenceResponseModel(
            atmosphere=buckets.get("atmosphere", []),
            bread_type=buckets.get("bread_type", []),
            flavor=buckets.get("flavor", []),
            c_area=buckets.get("c_area", []),
        )

    async def get_preference_options(self):
        """취향항목 조회하는 메소드."""
        try:
            res = self.db.query(Preferences).all()
            return self.convert_list_to_model(res)
        except Exception as e:
            raise UnknownExceptionError(str(e))
