import httpx
from datetime import datetime
from pydantic import BaseModel
from . import settings
from typing import Optional

# API endpoints
TOMORROW_IO_API_URL = "https://api.tomorrow.io/v4/weather/forecast"
GOOGLE_WEATHER_API_URL = "https://weather.googleapis.com/v1/weather"
OPEN_METEO_API_URL = "https://archive-api.open-meteo.com/v1/era5"


class WeatherData(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    uv_index: Optional[float] = None
    air_quality: float
    pollen_count: float


def parse_tomorrow_io_data(data: dict) -> WeatherData:
    """
    Parses weather data from the Tomorrow.io API.
    """
    timeline = data["timelines"]["hourly"][0]
    values = timeline["values"]

    return WeatherData(
        temperature=values.get("temperature", 0),
        humidity=values.get("humidity", 0),
        pressure=values.get("pressureSurfaceLevel", 0),
        uv_index=values.get("uvIndex", 0),
        air_quality=values.get("epaIndex", 0),
        pollen_count=values.get("pollenTree", 0),
    )


def parse_google_weather_data(data: dict) -> WeatherData:
    """
    Parses weather data from the Google Weather API.
    """
    hourly = data["hourlyForecasts"][0]

    return WeatherData(
        temperature=hourly.get("temperature", {"value": 0})["value"],
        humidity=hourly.get("humidity", {"value": 0})["value"],
        pressure=hourly.get("pressure", {"value": 0})["value"],
        uv_index=hourly.get("uvIndex", 0),
        air_quality=0, # Google Weather API does not provide a simple AQI
        pollen_count=0, # Google Weather API does not provide pollen count
    )


def parse_open_meteo_data(data: dict) -> WeatherData:
    """
    Parses weather data from the Open-Meteo API.
    """
    hourly = data["hourly"]

    uv_index = hourly.get("uv_index", [None])[0]

    return WeatherData(
        temperature=hourly.get("temperature_2m", [0])[0],
        humidity=hourly.get("relativehumidity_2m", [0])[0],
        pressure=hourly.get("pressure_msl", [0])[0],
        uv_index=uv_index if uv_index is not None else None,
        air_quality=0,
        pollen_count=0,
    )


async def get_tomorrow_io_weather(latitude: float, longitude: float):
    """
    Fetches weather data from the Tomorrow.io API.
    """
    app_settings = settings.get_settings()
    api_key = app_settings.get("tomorrow_io_api_key")

    if not api_key:
        return None

    params = {
        "location": f"{latitude},{longitude}",
        "timesteps": "1h",
        "units": "metric",
        "apikey": api_key,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(TOMORROW_IO_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Tomorrow.io API error: {e}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None


async def get_google_weather(latitude: float, longitude: float):
    """
    Fetches weather data from the Google Weather API.
    """
    app_settings = settings.get_settings()
    api_key = app_settings.get("google_weather_api_key")

    if not api_key:
        return None

    params = {
        "location.latitude": latitude,
        "location.longitude": longitude,
        "hourlyForecast": True,
        "key": api_key,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(GOOGLE_WEATHER_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Google Weather API error: {e}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None


async def get_open_meteo_weather(latitude: float, longitude: float, start_time: datetime, end_time: datetime):
    """
    Fetches historical weather data from the Open-Meteo API.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_time.strftime("%Y-%m-%d"),
        "end_date": end_time.strftime("%Y-%m-%d"),
        "hourly": [
            "temperature_2m",
            "relativehumidity_2m",
            "pressure_msl",
            "uv_index",
        ],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPEN_METEO_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Open-Meteo API error: {e}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None


async def get_weather_data(latitude: float, longitude: float, start_time: datetime, end_time: datetime) -> WeatherData | None:
    """
    Fetches weather data from the best available source and returns it in a
    unified format.
    """
    # Try Tomorrow.io first
    tomorrow_io_data = await get_tomorrow_io_weather(latitude, longitude)
    if tomorrow_io_data:
        return parse_tomorrow_io_data(tomorrow_io_data)

    # Fallback to Google Weather
    print("Falling back to Google Weather for weather data.")
    google_weather_data = await get_google_weather(latitude, longitude)
    if google_weather_data:
        return parse_google_weather_data(google_weather_data)

    # Fallback to Open-Meteo
    print("Falling back to Open-Meteo for weather data.")
    open_meteo_data = await get_open_meteo_weather(latitude, longitude, start_time, end_time)
    if open_meteo_data:
        return parse_open_meteo_data(open_meteo_data)

    return None
