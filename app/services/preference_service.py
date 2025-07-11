from collections import defaultdict
from typing import List

from sqlalchemy.orm import Session

from app.core.exception import UnknownExceptionError
from app.model.users import Preferences
from app.repositories.preference_repo import PreferenceRepository
from app.schema.preferences import PreferenceType


class PreferenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_preference_options(self):
        """취향항목 전부 조회하는 비즈니스 로직."""

        return await PreferenceRepository(db=self.db).get_preference_options()

    async def get_preference_option(self, option_type: str):
        """취향항목 조회하는 비즈니스 로직."""

        return await PreferenceRepository(db=self.db).get_preference_option(option_type)
