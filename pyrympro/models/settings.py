from ..helpers.const import *
from .base import BaseObject


class Settings(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def alert_type_id(self) -> int:
        return self._data.get(SETTINGS_ALERT_TYPE_ID)

    @property
    def media_type_id(self) -> str:
        return self._data.get(SETTINGS_MEDIA_TYPE_ID)

    @staticmethod
    def load(data: dict) -> list:
        all_settings = []

        for item in data:
            settings = Settings(item)
            all_settings.append(settings)

        return all_settings

    def as_dict(self) -> dict:
        data = {"meter_count": self.alert_type_id, "meter_id": self.media_type_id}

        return data
