from datetime import datetime

from ..helpers.const import *
from .base import BaseObject


class Consumption(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def meter_count(self) -> int:
        return self._data.get(CONSUMPTION_METER_COUNT)

    @property
    def date(self) -> datetime:
        date_iso = self._data.get(CONSUMPTION_DATE)
        date = datetime.fromisoformat(date_iso)

        return date

    @property
    def consumption(self) -> str:
        return self._data.get(CONSUMPTION_VALUE)

    @property
    def estimation_type(self) -> str:
        return self._data.get(CONSUMPTION_ESTIMATION_TYPE)

    @property
    def common_consumption(self) -> str:
        return self._data.get(CONSUMPTION_COMMON_DATA)

    @property
    def status_description(self) -> str:
        return self._data.get(CONSUMPTION_METER_STATUS_DESC)

    @staticmethod
    def load(data: dict):
        consumption = Consumption(data)

        return consumption

    def as_dict(self) -> dict:
        data = {
            "meter_count": self.meter_count,
            "date": self.date.isoformat(),
            "consumption": self.consumption,
            "estimation_type": self.estimation_type,
            "common_consumption": self.common_consumption,
            "status_description": self.status_description,
        }

        return data
