from ..helpers.const import *
from .base import BaseObject


class CustomerService(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def phone_number(self) -> str:
        return self._data.get(CUSTOMER_SERVICE_PHONE_NUMBER)

    @property
    def description(self) -> str:
        return self._data.get(CUSTOMER_SERVICE_DESCRIPTION)

    @property
    def municipal_id(self) -> str:
        return self._data.get(CUSTOMER_SERVICE_PHONE_MUNICIPAL_ID)

    @property
    def email(self) -> str:
        return self._data.get(CUSTOMER_SERVICE_EMAIL)

    @staticmethod
    def load(data: dict):
        return CustomerService(data)

    def as_dict(self) -> dict:
        data = {
            "phone_number": self.phone_number,
            "description": self.description,
            "municipal_id": self.municipal_id,
            "email": self.email,
        }

        return data
