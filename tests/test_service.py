import pytest
import respx
import httpx

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from src.services.weather_service import WeatherService

@pytest.mark.asyncio
@respx.mock
async def test_get_current_weather_success():
    svc = WeatherService()

    # Mock geocoding
    respx.get(svc.geocoding_url).respond(
        200,
        json={
            "results": [
                {
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "name": "Paris",
                    "country_code": "FR",
                }
            ]
        },
    )

    # Mock current weather
    respx.get(svc.weather_url).respond(
        200,
        json={
            "current": {
                "time": "2026-01-13T10:00:00",
                "temperature_2m": 10.5,
                "relative_humidity_2m": 80,
                "apparent_temperature": 9.8,
                "pressure_msl": 1015.2,
                "wind_speed_10m": 3.4,
                "weather_code": 0,
            }
        },
    )

    out = await svc.get_current_weather("Paris", "FR")
    assert out.city == "Paris"
    assert out.country == "FR"
    assert out.weather.temperature == 10.5
    assert out.weather.description == "Ciel dégagé"
    assert out.weather.icon == "01d"


@pytest.mark.asyncio
@respx.mock
async def test_get_forecast_success_7_days():
    svc = WeatherService()

    respx.get(svc.geocoding_url).respond(
        200,
        json={
            "results": [
                {
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "name": "Paris",
                    "country_code": "FR",
                }
            ]
        },
    )

    respx.get(svc.weather_url).respond(
        200,
        json={
            "daily": {
                "time": [
                    "2026-01-13",
                    "2026-01-14",
                    "2026-01-15",
                    "2026-01-16",
                    "2026-01-17",
                    "2026-01-18",
                    "2026-01-19",
                ],
                "weather_code": [0, 1, 2, 3, 45, 61, 95],
                "temperature_2m_max": [10, 11, 12, 13, 9, 8, 7],
                "temperature_2m_min": [2, 3, 4, 5, 1, 0, -1],
                "apparent_temperature_max": [10, 11, 12, 13, 9, 8, 7],
                "apparent_temperature_min": [2, 3, 4, 5, 1, 0, -1],
                "precipitation_probability_max": [0, 10, 20, 30, 40, 60, 80],
                "wind_speed_10m_max": [3, 4, 5, 6, 7, 8, 9],
            }
        },
    )

    out = await svc.get_forecast("Paris", "FR")
    assert out.city == "Paris"
    assert out.country == "FR"
    assert len(out.forecast) == 7
    assert out.forecast[0].date == "2026-01-13"
    assert out.forecast[0].icon == "01d"
    assert out.forecast[-1].description == "Orage"


@pytest.mark.asyncio
@respx.mock
async def test_get_coordinates_city_not_found_raises_value_error():
    svc = WeatherService()

    respx.get(svc.geocoding_url).respond(200, json={"results": []})

    with pytest.raises(ValueError):
        await svc._get_coordinates("NopeTown", None)


def test_wmo_description_unknown_code():
    svc = WeatherService()
    assert svc._get_weather_description(9999) == "Conditions inconnues"


def test_wmo_icon_unknown_code():
    svc = WeatherService()
    assert svc._wmo_to_icon(9999) == "01d"


@pytest.mark.asyncio
@respx.mock
async def test_get_current_weather_http_error_propagates():
    svc = WeatherService()

    respx.get(svc.geocoding_url).respond(
        200,
        json={
            "results": [
                {
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "name": "Paris",
                    "country_code": "FR",
                }
            ]
        },
    )

    # Simulate Open-Meteo server error
    respx.get(svc.weather_url).respond(500, json={"error": "boom"})

    with pytest.raises(httpx.HTTPStatusError):
        await svc.get_current_weather("Paris", "FR")
