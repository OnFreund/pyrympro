import json


class BaseObject:
    _data: dict | None

    def __init__(self, data: dict):
        self._data = data

    def as_dict(self) -> dict:
        return self._data

    def __repr__(self):
        json_data = json.dumps(self.as_dict(), indent=4)

        return json_data
