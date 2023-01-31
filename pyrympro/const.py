from enum import Enum

BASE_URL_OLD = "https://api.city-mind.com"
BASE_URL_NEW = "https://api-ctm.city-mind.com"

CONSUMER_URL_OLD = f"{BASE_URL_OLD}/consumer"
CONSUMER_URL_NEW = f"{BASE_URL_NEW}/consumer"

CONSUMPTION_URL = f"{BASE_URL_NEW}/consumption"

class Endpoint(Enum):
  LOGIN = f"{CONSUMER_URL_OLD}/login"
  ACCOUNT_INFO = f"{CONSUMER_URL_OLD}/me"
  LAST_READ = f"{CONSUMPTION_URL}/last-read"
  CONSUMPTION_FORECAST = f"{CONSUMPTION_URL}/forecast/{{meter_id}}"