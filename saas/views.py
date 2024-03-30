import os
import requests

from concurrent.futures import ThreadPoolExecutor

from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from django.conf import settings


OPEN_WEATHERMAP_KEY = settings.OPEN_WEATHERMAP_KEY
BASE_URL_OPEN_WEATHER = "https://api.openweathermap.org/data/2.5/onecall"
URL_PART = "&exclude=current,minutely,hourly,alerts&units=metric"


class OpenWeatherException(Exception):
    value = "Error getting the temperature"

class OpenWeatherLimitException(Exception):
    value = "Error getting the temperature, limit reached"


def get_temperature_from_city(city):
    """Get the current temperature from a place"""
    URL_OPEN_WEATHER_MAP = f'{BASE_URL_OPEN_WEATHER}?lat={city["lat"]}&lon={city["lon"]}&appid={OPEN_WEATHERMAP_KEY}{URL_PART}'
    response = requests.get(URL_OPEN_WEATHER_MAP)

    if response.status_code != 200:
        if response.status_code == 429:
            raise OpenWeatherLimitException()
        raise OpenWeatherException()

    temperature_min = response.json()["daily"][0]["temp"]["min"]
    temperature_max = response.json()["daily"][0]["temp"]["max"]
    city["min"] = temperature_min
    city["max"] = temperature_max
    return city


@api_view(["GET"])
@action(detail=False, methods=["get"])
def get_temperature(request):
    """Get the current temperature from a place"""
    city = request.query_params.get("city")
    if not city:
        return Response(
            {"error": "Please provide a city name"}, status=status.HTTP_400_BAD_REQUEST
        )
    URL_API_RESERVAMOS = f'https://search.reservamos.mx/api/v2/places?q={city}'
    response = requests.get(URL_API_RESERVAMOS)

    if response.status_code != 201:
        return Response(
            {"error": "Error getting the city"}, status=status.HTTP_400_BAD_REQUEST
        )

    get_city = response.json()

    clean_city = [
            {"city": city["city_name"], "lat": city["lat"], "lon": city["long"]}
            for city in get_city
            if city["lat"] and city["long"]
    ]

    # In this case I will use thread to make many request at the same time
    # Other solution could be using async, but need use a different library to run Django with async
    # like Daphne or Uvicorn
    MAX_THREADS = min(os.cpu_count(), len(clean_city))
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        try:
            cities_with_temp = list(executor.map(get_temperature_from_city, clean_city))
        except OpenWeatherLimitException:
            return Response(
                {"error": "Error getting the temperature in Openwather, limit reached."}, status=status.HTTP_400_BAD_REQUEST
            )
        except OpenWeatherException:
            return Response(
                {"error": "Error getting the temperature in Openwather."}, status=status.HTTP_400_BAD_REQUEST
            )


    return Response({"cities": cities_with_temp}, status=status.HTTP_200_OK)

