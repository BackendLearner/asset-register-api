import requests
import pytest

from weather_client import WeatherClient, WeatherAPIError

def test_get_current_weather_success(mocker):
    mock_response = mocker.Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 25.5,
            "wind_speed_10m": 10.2,
        }
    }

    mock_get = mocker.patch(
        "weather_client.requests.get",
        return_value=mock_response,
    )

    client = WeatherClient()

    result = client.get_current_weather(18.52, 73.85)

    assert result["current"]["temperature_2m"] == 25.5

    mock_get.assert_called_once_with(
        WeatherClient.BASE_URL,
        params={
            "latitude": 18.52,
            "longitude": 73.85,
            "current": "temperature_2m,wind_speed_10m",
        },
        timeout=5,
    )

    mock_response.raise_for_status.assert_called_once()

def test_get_current_weather_http_error(mocker):
        mock_response = mocker.Mock()

        mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("404 Not Found")
    )

        mocker.patch(
        "weather_client.requests.get",
        return_value=mock_response,
    )

        client = WeatherClient()

        with pytest.raises(WeatherAPIError):
          client.get_current_weather(18.52, 73.85)

        mock_response.raise_for_status.assert_called_once()    


def test_get_current_weather_retries_on_timeout(mocker):
    mock_response = mocker.Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 25.5,
            "wind_speed_10m": 10.2,
        }
    }

    mock_get = mocker.patch(
        "weather_client.requests.get",
        side_effect=[
            requests.exceptions.Timeout,
            requests.exceptions.Timeout,
            mock_response,
        ],
    )

    # Prevent actual waiting during the test
    mocker.patch("decorators.sleep")

    client = WeatherClient()

    result = client.get_current_weather(18.52, 73.85)

    assert result["current"]["temperature_2m"] == 25.5
    assert mock_get.call_count == 3


def test_get_current_weather_retries_on_connection_error(mocker):
    mock_response = mocker.Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 26.0,
            "wind_speed_10m": 12.0,
        }
    }

    mock_get = mocker.patch(
        "weather_client.requests.get",
        side_effect=[
            requests.exceptions.ConnectionError,
            mock_response,
        ],
    )

    mocker.patch("decorators.sleep")

    client = WeatherClient()

    result = client.get_current_weather(18.52, 73.85)

    assert result["current"]["temperature_2m"] == 26.0
    assert mock_get.call_count == 2


def test_http_error_is_not_retried(mocker):
    mock_response = mocker.Mock()

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )

    mock_get = mocker.patch(
        "weather_client.requests.get",
        return_value=mock_response,
    )

    client = WeatherClient()

    with pytest.raises(WeatherAPIError):
        client.get_current_weather(18.52, 73.85)

    assert mock_get.call_count == 1  


def test_timing_decorator_prints_execution_time(mocker, capsys):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"current": {"temperature_2m": 25.5}}

    mocker.patch(
        "weather_client.requests.get",
        return_value=mock_response,
    )

    client = WeatherClient()
    client.get_current_weather(18.52, 73.85)

    captured = capsys.readouterr()

    assert "get_current_weather took" in captured.out
    assert "seconds" in captured.out      