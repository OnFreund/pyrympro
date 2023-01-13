"""Implementation of a RymPro inteface."""
import aiohttp
import asyncio

from .const import Endpoint

class RymPro:
  """A connection to RYM Pro."""

  def __init__(self, session=None):
    """Initialize the object."""
    self._created_session = False
    self._session = session
    self._access_token = None

  async def close(self):
    """Close the connection."""
    if self._created_session and self._session is not None:
      await self._session.close()
      self._session = None
      self._created_session = False

  async def login(self, email, password, device_id):
    """Login to RYM Pro."""
    if self._session == None:
      self._session = aiohttp.ClientSession()
      self._created_session = True
    headers = {"Content-Type": "application/json"}
    body = {"email": email, "pw": password, "deviceId": device_id}
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

  async def account_info(self):
    """Get the account information."""
    return await self._get(Endpoint.ACCOUNT_INFO)

  async def last_read(self):
    """Get the latest meter reads."""
    return await self._get(Endpoint.LAST_READ)

  async def _get(self, endpoint, params=None):
    if not self._access_token:
      raise OperationError("Please login")
    headers = {"Content-Type": "application/json", "x-access-token": self._access_token}
    try:
      async with self._session.get(endpoint.value, headers=headers) as response:
        if response.status == 200:
          return await response.json()
        else:
          raise OperationError(response)
    except (asyncio.TimeoutError, aiohttp.ClientError) as error:
      raise OperationError() from error

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
