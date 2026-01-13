import pytest
from pydantic import ValidationError
from datetime import datetime


import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))
    
from src.models.Weather import WeatherRequest, CurrentWeatherData, WeatherResponse


def test_weather_request_valid():
    req = WeatherRequest(city="Paris", country_code="FR")
    assert req.city == "Paris"
    assert req.country_code == "FR"


def test_weather_request_city_required():
    with pytest.raises(ValidationError):
        WeatherRequest(city="")


def test_current_weather_data_valid():
    data = CurrentWeatherData(
        temperature=10.0,
        feels_like=9.0,
        humidity=80.0,
        pressure=1015.0,
        wind_speed=3.2,
        description="Ciel dégagé",
        icon="01d",
    )
    assert data.temperature == 10.0
    assert data.icon == "01d"


def test_weather_response_valid():
    w = CurrentWeatherData(
        temperature=12.3,
        feels_like=11.0,
        humidity=70.0,
        pressure=1012.0,
        wind_speed=4.0,
        description="Couvert",
        icon="04d",
    )
    resp = WeatherResponse(
        city="Paris",
        country="FR",
        timestamp=datetime.fromisoformat("2026-01-13T10:00:00"),
        weather=w,
    )
    assert resp.city == "Paris"
    assert resp.weather.description == "Couvert"
