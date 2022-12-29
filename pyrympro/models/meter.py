from ..helpers.const import *
from .base import BaseObject
from .consumption import Consumption


class Meter(BaseObject):
    meter_id: str | None
    last_read: float | None
    forecast: float | None
    daily_consumption: list[Consumption] | None
    monthly_consumption: list[Consumption] | None

    def __init__(self, data: dict):
        super().__init__(data)

        self.meter_id = None
        self.last_read = None
        self.forecast = None
        self.daily_consumption = None
        self.monthly_consumption = None

    @property
    def meter_count(self) -> int:
        return self._data.get(METER_COUNT)

    @property
    def serial_number(self) -> str:
        return self._data.get(METER_SERIAL_NUMBER)

    @property
    def full_address(self) -> str:
        return self._data.get(METER_FULL_ADDRESS)

    @staticmethod
    def load(data: dict) -> list:
        meters = []

        for item in data:
            meter = Meter(item)
            meters.append(meter)

        return meters

    @staticmethod
    def update_last_read(meter, data: dict):
        meter.meter_id = data.get(LAST_READ_METER_ID)
        meter.last_read = data.get(LAST_READ_VALUE)

    @staticmethod
    def update_daily_consumption(meter, data: dict):
        if meter.daily_consumption is None:
            meter.daily_consumption = []

        consumption = Consumption.load(data)

        meter.daily_consumption.append(consumption)

    @staticmethod
    def update_monthly_consumption(meter, data: dict):
        if meter.monthly_consumption is None:
            meter.monthly_consumption = []

        consumption = Consumption.load(data)

        meter.monthly_consumption.append(consumption)

    @staticmethod
    def update_forecast(meter, data: dict):
        meter.forecast = data.get(CONSUMPTION_FORECAST_ESTIMATED_CONSUMPTION)

    def as_dict(self) -> dict:
        data = {
            "meter_count": self.meter_count,
            "meter_id": self.meter_id,
            "serial_number": self.serial_number,
            "full_address": self.full_address,
            "last_read": self.last_read,
            "forecast": self.forecast,
            "daily_consumption": [x.as_dict() for x in self.daily_consumption],
            "monthly_consumption": [x.as_dict() for x in self.monthly_consumption],
        }

        return data
