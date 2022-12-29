"""Implementation of a RymPro interface."""
import logging
import sys
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

from aiohttp import ClientResponseError, ClientSession

from .helpers.const import *
from .helpers.enums import AlertTypes, MediaTypes
from .helpers.exceptions import CannotConnectError, UnauthorizedError
from .models.customer_service import CustomerService
from .models.meter import Meter
from .models.profile import Profile
from .models.settings import Settings

_LOGGER = logging.getLogger(__name__)


class RymPro:
    """A connection to RYM Pro."""

    _data: dict
    _alert_settings_actions: dict[
        bool, Callable[[str, AlertTypes, list[int]], Awaitable[dict]]
    ]
    _session: ClientSession | None

    _username: str | None
    _password: str | None
    _device_id: str | None
    _token: str | None

    _today: str | None
    _yesterday: str | None
    _last_day_of_current_month: str | None
    _current_month: str | None

    _profile: Profile | None

    def __init__(self, session: ClientSession | None = None):
        """Initialize the object."""
        self._session = ClientSession() if session is None else session
        self._username = None
        self._password = None
        self._device_id = None
        self._token = None

        self._today = None
        self._yesterday = None
        self._last_day_of_current_month = None
        self._current_month = None

        self._data = {}
        self._alert_settings_actions = {
            True: self._put,
            False: self._delete,
        }

        self._profile = None

        self._data_mapper = {
            API_DATA_SECTION_ME: Profile.load,
            API_DATA_SECTION_METERS: Meter.load,
            API_DATA_SECTION_CUSTOMER_SERVICE: CustomerService.load,
            API_DATA_SECTION_SETTINGS: Settings.load,
        }

        self._meter_data_mapper = {
            API_DATA_SECTION_LAST_READ: Meter.update_last_read,
            API_DATA_SECTION_CONSUMPTION_DAILY: Meter.update_daily_consumption,
            API_DATA_SECTION_CONSUMPTION_MONTHLY: Meter.update_monthly_consumption,
            API_DATA_SECTION_CONSUMPTION_FORECAST: Meter.update_forecast,
        }

    @property
    def _headers(self):
        headers = {API_HEADER_TOKEN: self.token}

        return headers

    @property
    def _municipal_id(self) -> str | None:
        return None if self.profile is None else self.profile.municipal_id

    @property
    def token(self):
        return self._token

    @property
    def profile(self) -> Profile:
        """Holds details of customer account details."""
        profile = self._data.get(API_DATA_SECTION_ME)

        return profile

    @property
    def meters(self) -> list[Meter]:
        """Holds details of all meters, including their consumption, last read and forecast."""
        meters = self._data.get(API_DATA_SECTION_METERS)

        return meters

    @property
    def customer_service(self) -> dict | None:
        """Holds details of customer service."""
        customer_service = self._data.get(API_DATA_SECTION_CUSTOMER_SERVICE)

        return customer_service

    @property
    def vacations(self) -> dict | None:
        """Holds details of vacations."""
        vacations = self._data.get(API_DATA_SECTION_VACATIONS)

        return vacations

    @property
    def my_alerts(self) -> dict | None:
        """Holds details of alerts."""
        my_alerts = self._data.get(API_DATA_SECTION_MY_ALERTS)

        return my_alerts

    @property
    def my_messages(self) -> dict | None:
        """Holds details of messages."""
        my_messages = self._data.get(API_DATA_SECTION_MY_MESSAGES)

        return my_messages

    @property
    def settings(self) -> dict | None:
        """Holds the communication settings."""
        settings = self._data.get(API_DATA_SECTION_SETTINGS)

        return settings

    async def close(self):
        """Close the connection."""
        if self._session is not None:
            await self._session.close()

            self._session = None

    async def initialize(
        self, username: str, password: str, device_id: str | None = DEFAULT_DEVICE_ID
    ):
        self._username = username
        self._password = password
        self._device_id = device_id

        await self._login()

    async def update(self):
        _LOGGER.debug(f"Updating data for user {self._username}")

        if self.token is None:
            await self._login()

        else:
            self._set_date()

            if self._municipal_id is None:
                await self._load_data(ENDPOINT_DATA_INITIALIZE)

            await self._load_data(ENDPOINT_DATA_UPDATE)

            for meter in self.meters:
                meter_count = str(meter.meter_count)

                await self._load_data(ENDPOINT_DATA_UPDATE_PER_METER, meter_count)

    async def set_alert_settings(
        self, alert_type: AlertTypes, media_type: MediaTypes, enabled: bool
    ):
        _LOGGER.info(f"Updating alert {alert_type} on media {media_type} to {enabled}")

        action = self._alert_settings_actions[enabled]
        data = [int(media_type.value)]

        await action(ENDPOINT_MY_ALERTS_SETTINGS_UPDATE, alert_type, data)

        await self._load_data(ENDPOINT_DATA_RELOAD)

    def _set_date(self):
        today = datetime.now()
        today_iso = today.strftime(FORMAT_DATE_ISO)

        if self._today != today_iso:
            yesterday = today - timedelta(days=1)

            year = today.year if today.month <= 11 else today.year + 1
            month = today.month + 1 if today.month <= 11 else 1

            next_month_date = datetime(year=year, month=month, day=1)
            last_day_of_current_month = next_month_date - timedelta(days=1)

            self._today = today_iso
            self._yesterday = yesterday.strftime(FORMAT_DATE_ISO)
            self._current_month = today.strftime(FORMAT_DATE_YEAR_MONTH)
            self._last_day_of_current_month = last_day_of_current_month.strftime(
                FORMAT_DATE_ISO
            )

    async def _login(self):
        """Login to RYM Pro."""
        _LOGGER.debug(f"Updating data for user {self._username}")

        self._token = None

        login_data = {
            LOGIN_EMAIL: self._username,
            LOGIN_PASSWORD: self._password,
            LOGIN_DEVICE_ID: self._device_id,
        }

        result = await self._post(ENDPOINT_LOGIN, login_data)

        if result is not None:
            token = result.get(API_DATA_TOKEN)
            error_code = result.get(API_DATA_ERROR_CODE)
            error = result.get(API_DATA_ERROR_REASON)

            if error_code == 5060:
                raise UnauthorizedError(error)

            elif token is None or error_code:
                raise CannotConnectError(f"code: {error_code}, error: {error}")

            self._token = token

    async def _load_data(self, endpoints: dict, meter_count: str | None = None):
        for endpoint_key in endpoints:
            if self.token is not None:
                _LOGGER.debug(f"Reloading data for {endpoint_key}")

                endpoint = endpoints.get(endpoint_key)

                data = await self._get(endpoint, meter_count)

                if data is not None:
                    if endpoint_key in self._data_mapper:
                        self._handle_generic_data_mapper(endpoint_key, data)

                    elif endpoint_key in self._meter_data_mapper:
                        self._handle_meter_data_mapper(endpoint_key, meter_count, data)

                    else:
                        _LOGGER.debug(f"Ignoring: {endpoint_key}")

    def _handle_generic_data_mapper(self, endpoint_key, data):
        mapper = self._data_mapper[endpoint_key]

        mapper_value = mapper(data)

        self._data[endpoint_key] = mapper_value

    def _handle_meter_data_mapper(
        self, endpoint_key: str, meter_count: str, data: dict | list
    ):
        current_meter: Meter | None = None
        for meter in self.meters:

            if meter_count == str(meter.meter_count):
                current_meter = meter
                break

        mapper = self._meter_data_mapper[endpoint_key]

        if isinstance(data, list):
            for data_item in data:
                data_item_meter = str(data_item.get(METER_COUNT))

                if data_item_meter == meter_count:
                    mapper(current_meter, data_item)

        else:
            mapper(current_meter, data)

    async def _get(self, endpoint: str, meter_count: str | None = None) -> dict | None:
        result = None

        try:
            url = self._build_endpoint(endpoint, meter_count)

            async with self._session.get(url, headers=self._headers) as response:
                response.raise_for_status()

                result = await response.json()

        except ClientResponseError as crex:
            self._handle_client_error(crex, endpoint)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to get JSON from {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _post(self, endpoint: str, request_data: dict) -> dict | None:
        result = None

        try:
            url = self._build_endpoint(endpoint)

            _LOGGER.debug(f"POST {url}")

            async with self._session.post(
                url, json=request_data, ssl=False
            ) as response:
                result = await response.json()

                response.raise_for_status()

        except ClientResponseError as crex:
            self._handle_client_error(crex, endpoint)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to post JSON to {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _put(self, endpoint: str, alert_type: AlertTypes, data: list[int]):
        result = None

        try:
            url = self._build_endpoint(endpoint, alert_type=alert_type)

            async with self._session.put(
                url, headers=self._headers, json=data
            ) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

        except ClientResponseError as crex:
            self._handle_client_error(crex, endpoint)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to put data to {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _delete(self, endpoint: str, alert_type: AlertTypes, data: list[int]):
        result = None

        try:
            url = self._build_endpoint(endpoint, alert_type=alert_type)

            async with self._session.delete(
                url, headers=self._headers, json=data, ssl=False
            ) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

        except ClientResponseError as crex:
            self._handle_client_error(crex, endpoint)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to delete data from {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    def _handle_client_error(self, crex: ClientResponseError, endpoint: str):
        if crex.status == 401:
            _LOGGER.error("Token expired, please try to re-login")
            self._data = {}

        else:
            _LOGGER.error(
                f"Failed to delete data from {endpoint}, HTTP Status: {crex.message} ({crex.status})"
            )

    def _build_endpoint(
        self,
        endpoint: str,
        meter_count: str | None = None,
        alert_type: AlertTypes | None = None,
    ):

        data = {
            ENDPOINT_PARAMETER_METER_ID: meter_count,
            ENDPOINT_PARAMETER_YESTERDAY: self._yesterday,
            ENDPOINT_PARAMETER_TODAY: self._today,
            ENDPOINT_PARAMETER_LAST_DAY_MONTH: self._last_day_of_current_month,
            ENDPOINT_PARAMETER_MUNICIPALITY_ID: self._municipal_id,
            ENDPOINT_PARAMETER_CURRENT_MONTH: self._current_month,
            ENDPOINT_PARAMETER_ALERT_TYPE: alert_type.value,
        }

        url = endpoint.format(**data)

        return url
