"""Implementation of a RymPro inteface."""
import aiohttp
import asyncio
from typing import Any, Optional
from .const import Endpoint

class RymPro:
  """A connection to RYM Pro."""

  def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
    """Initialize the object."""
    self._created_session = False
    self._session = session
    self._access_token: Optional[str] = None

  async def close(self) -> None:
    """Close the connection."""
    if self._created_session and self._session is not None:
      await self._session.close()
      self._session = None
      self._created_session = False

  def set_token(self, token: str) -> None:
    """Use a pre-existing token instead of logging in."""
    self._init_session()
    self._access_token = token

  async def login(self, email: str, password: str, device_id: str) -> str:
    """Login to RYM Pro and return a token."""
    self._init_session()
    headers = {"Content-Type": "application/json"}
    body = {"email": email, "pw": password, "deviceId": device_id}
    assert self._session
    try:
      async with self._session.post(
        Endpoint.LOGIN.value, headers=headers, json=body
      ) as response:
        json = await response.json()
        token = json.get("token")
        error_code = json.get("code")
        error = json.get("error")

        if error_code == 5060:
          raise UnauthorizedError(error)
        elif token is None or error_code:
          raise CannotConnectError(f"code: {error_code}, error: {error}")
        else:
          self._access_token = token
          return token
    except aiohttp.client_exceptions.ClientConnectorError as e:
      raise CannotConnectError from e

  async def account_info(self) -> dict[str, Any]:
    """Get the account information."""
    return await self._get(Endpoint.ACCOUNT_INFO)

  async def last_read(self) -> dict[int, dict[str, Any]]:
    """Get the latest meter reads."""
    raw: list[dict[str, Any]] = await self._get(Endpoint.LAST_READ)
    return { meter["meterCount"]: meter for meter in raw }

  async def consumption_forecast(self, meter_id: int) -> float:
    """Get the consumption forecast for this month."""
    return (await self._get(Endpoint.CONSUMPTION_FORECAST, meter_id=meter_id))["estimatedConsumption"]

  async def _get(self, endpoint: Endpoint, **kwargs: Any) -> Any:
    if not self._access_token:
      raise OperationError("Please login")
    headers = {"Content-Type": "application/json", "x-access-token": self._access_token}
    assert self._session
    try:
      async with self._session.get(endpoint.value.format(**kwargs), headers=headers) as response:
        if response.status == 200:
          return await response.json()
        elif response.status == 401:
          raise UnauthorizedError(response)
        else:
          raise OperationError(response)
    except (asyncio.TimeoutError, aiohttp.ClientError) as error:
      raise OperationError() from error

  def _init_session(self) -> None:
    if self._session == None:
      self._session = aiohttp.ClientSession()
      self._created_session = True

  # async def _post(self, endpoint, json_payload=None):
  #   if not self._access_token:
  #     raise OperationError("Please login")
  #   headers = {"Content-Type": "application/json", "x-access-token": self._access_token}
  #   try:
  #     async with self._session.post(endpoint.value, headers=headers, json=json_payload) as response:
  #       if response.status == 200:
  #         return await response.json()
  #       else:
  #         raise OperationError(response)
  #   except (asyncio.TimeoutError, aiohttp.ClientError) as error:
  #     raise OperationError() from error


class CannotConnectError(Exception):
  """Exception to indicate an error in connection."""

class UnauthorizedError(Exception):
  """Exception to indicate an error in authorization."""

class OperationError(Exception):
  """Exception to indicate an error in operation."""
