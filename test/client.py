import asyncio
import logging
import os
import sys

from ..pyrympro.helpers.enums import AlertTypes, MediaTypes
from ..pyrympro.rympro import RymPro

DEBUG = str(os.environ.get("DEBUG", False)).lower() == str(True).lower()

log_level = logging.DEBUG if DEBUG else logging.INFO

root = logging.getLogger()
root.setLevel(log_level)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
stream_handler.setFormatter(formatter)
root.addHandler(stream_handler)

_LOGGER = logging.getLogger(__name__)


class Test:
    def __init__(self):
        self._username = os.environ.get("USERNAME")
        self._password = os.environ.get("PASSWORD")

    async def login(self):
        client = RymPro()

        try:
            await client.initialize(self._username, self._password)

            await client.close()

        except Exception as ex:
            _LOGGER.error(f"Failed to login client, Error: {ex}")
            await client.close()

    async def load_data(self):
        client = RymPro()

        try:
            await client.initialize(self._username, self._password)

            await client.update()

            _LOGGER.info(f"profile: {client.profile}")
            _LOGGER.info(f"meters: {client.meters}")
            _LOGGER.info(f"customer_service: {client.customer_service}")
            _LOGGER.info(f"settings: {client.settings}")

            await client.close()

        except Exception as ex:
            _LOGGER.error(f"Failed to load client, Error: {ex}")
            await client.close()

    async def set_leak_alert_all_channels(self):
        client = RymPro()

        try:
            await client.initialize(self._username, self._password)

            await client.update()

            _LOGGER.info(f"settings: {client.settings}")

            await client.set_alert_settings(AlertTypes.LEAK, MediaTypes.ALL, True)

            _LOGGER.info(f"settings: {client.settings}")

            await client.close()

        except Exception as ex:
            _LOGGER.error(f"Failed to load client, Error: {ex}")
            await client.close()


test = Test()
loop = asyncio.new_event_loop()

loop.run_until_complete(test.login())
loop.run_until_complete(test.load_data())
loop.run_until_complete(test.set_leak_alert_all_channels())
