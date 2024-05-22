from enum import Enum

BASE_URL = "https://eu-customerportal-api.harmonyencoremdm.com"

CONSUMER_URL = f"{BASE_URL}/consumer"

CONSUMPTION_URL = f"{BASE_URL}/consumption"

class Endpoint(Enum):
  LOGIN = f"{CONSUMER_URL}/login"
  ACCOUNT_INFO = f"{CONSUMER_URL}/me"
  LAST_READ = f"{CONSUMPTION_URL}/last-read"
  CONSUMPTION_FORECAST = f"{CONSUMPTION_URL}/forecast/{{meter_id}}"
  DAILY_CONSUMPTION = f"{CONSUMPTION_URL}/daily/{{meter_id}}/{{start_date}}/{{end_date}}"
  MONTHLY_CONSUMPTION = f"{CONSUMPTION_URL}/monthly/{{meter_id}}/{{start_date}}/{{end_date}}"
