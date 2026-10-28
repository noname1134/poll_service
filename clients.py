import os

import httpx
from dotenv import load_dotenv

from exceptions import UserServiceUnavailableError

load_dotenv()


class UserClient:
    def __init__(self):
        self.base_url = os.environ["USER_SERVICE_URL"].rstrip("/")

    def get_user(self, user_id: int):
        try:
            response = httpx.get(f"{self.base_url}/users/{user_id}",timeout=5.0,)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise UserServiceUnavailableError("Could not reach the User service") from exc
        except httpx.HTTPStatusError as exc:
            raise UserServiceUnavailableError("User service returned an unexpected HTTP status") from exc