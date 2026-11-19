
import requests

from decorators import retry, timing


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    pass


class WeatherClient:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: float = 5):
        self.timeout = timeout

    @timing
    @retry(
        times=3,
        delay=1,
        exceptions=(
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ),
    )
    def get_current_weather(self, latitude: float, longitude: float):
        params: dict[str, str | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as error:
            raise WeatherAPIError("Weather API request failed") from error
