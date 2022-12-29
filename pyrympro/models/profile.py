from ..helpers.const import *
from .base import BaseObject


class Profile(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

    @property
    def first_name(self) -> str:
        return self._data.get(ME_FIRST_NAME)

    @property
    def last_name(self) -> str:
        return self._data.get(ME_LAST_NAME)

    @property
    def account_number(self) -> str:
        return self._data.get(ME_ACCOUNT_NUMBER)

    @property
    def _phone_number_section(self) -> dict:
        return self._data.get(ME_PHONE_NUMBER_SECTION, {})

    @property
    def phone_number(self) -> str:
        return self._phone_number_section.get(ME_PHONE_NUMBER)

    @property
    def additional_phone_number(self) -> str:
        return self._phone_number_section.get(ME_ADDITIONAL_PHONE_NUMBER)

    @property
    def municipal_id(self) -> str:
        return self._data.get(ME_MUNICIPAL_ID)

    @staticmethod
    def load(data: dict):
        return Profile(data)

    def as_dict(self) -> dict:
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "account_number": self.account_number,
            "phone_number": self.phone_number,
            "additional_phone_number": self.additional_phone_number,
            "municipal_id": self.municipal_id,
        }

        return data
