import pytest
import httpx
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient


import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


from src.resources.weather_resource import router
from src.models.Weather import WeatherResponse, CurrentWeatherData, ForecastResponse, DailyForecastData


@pytest.fixture
def app():
    a = FastAPI()
    a.include_router(router)
    return a


@pytest.fixture
def client(app):
    return TestClient(app)


def test_current_weather_success(client, monkeypatch):
    async def fake_get_current_weather(city, country_code=None):
        return WeatherResponse(
            city="Paris",
            country="FR",
            timestamp=datetime.fromisoformat("2026-01-13T10:00:00"),
            weather=CurrentWeatherData(
                temperature=10.0,
                feels_like=9.0,
                humidity=80.0,
                pressure=1015.0,
                wind_speed=3.0,
                description="Ciel dégagé",
                icon="01d",
            ),
        )

    monkeypatch.setattr(
        "src.resources.weather_resource.weather_service.get_current_weather",
        fake_get_current_weather,
    )

    r = client.get("/weather/current?city=Paris&country_code=FR")
    assert r.status_code == 200
    body = r.json()
    assert body["city"] == "Paris"
    assert body["weather"]["icon"] == "01d"


def test_current_weather_404_http_status_error_maps_to_404(client, monkeypatch):
    async def fake_get_current_weather(city, country_code=None):
        req = httpx.Request("GET", "http://test")
        resp = httpx.Response(404, request=req)
        raise httpx.HTTPStatusError("not found", request=req, response=resp)

    monkeypatch.setattr(
        "src.resources.weather_resource.weather_service.get_current_weather",
        fake_get_current_weather,
    )

    r = client.get("/weather/current?city=Nope")
    assert r.status_code == 404
    assert "non trouvée" in r.json()["detail"]


def test_current_weather_http_error_maps_to_500(client, monkeypatch):
    async def fake_get_current_weather(city, country_code=None):
        raise httpx.HTTPError("network down")

    monkeypatch.setattr(
        "src.resources.weather_resource.weather_service.get_current_weather",
        fake_get_current_weather,
    )

    r = client.get("/weather/current?city=Paris")
    assert r.status_code == 500
    assert "connexion" in r.json()["detail"]


def test_forecast_success(client, monkeypatch):
    async def fake_get_forecast(city, country_code=None):
        return ForecastResponse(
            city="Paris",
            country="FR",
            forecast=[
                DailyForecastData(
                    date="2026-01-13",
                    temp_min=2.0,
                    temp_max=10.0,
                    temp_day=7.0,
                    temp_night=3.0,
                    humidity=50.0,
                    wind_speed=3.0,
                    description="Ciel dégagé",
                    icon="01d",
                    precipitation_probability=0.0,
                )
            ],
        )

    monkeypatch.setattr(
        "src.resources.weather_resource.weather_service.get_forecast",
        fake_get_forecast,
    )

    r = client.get("/weather/forecast?city=Paris&country_code=FR")
    assert r.status_code == 200
    body = r.json()
    assert body["city"] == "Paris"
    assert len(body["forecast"]) == 1


def test_forecast_404_http_status_error_maps_to_404(client, monkeypatch):
    async def fake_get_forecast(city, country_code=None):
        req = httpx.Request("GET", "http://test")
        resp = httpx.Response(404, request=req)
        raise httpx.HTTPStatusError("not found", request=req, response=resp)

    monkeypatch.setattr(
        "src.resources.weather_resource.weather_service.get_forecast",
        fake_get_forecast,
    )

    r = client.get("/weather/forecast?city=Nope")
    assert r.status_code == 404
    assert "non trouvée" in r.json()["detail"]
