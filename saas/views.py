import os
import requests

from concurrent.futures import ThreadPoolExecutor

from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from django.conf import settings


OPEN_WEATHERMAP_KEY = settings.OPEN_WEATHERMAP_KEY

def get_temperature_from_city(city):
    """Get the current temperature from a place"""
    URL_OPEN_WEATHER_MAP = f'https://api.openweathermap.org/data/2.5/onecall?lat={city["lat"]}&lon={city["lon"]}&exclude=current,minutely,hourly,alerts&appid={OPEN_WEATHERMAP_KEY}&units=metric'
    response = requests.get(URL_OPEN_WEATHER_MAP)
    if response.status_code != 200:
        raise Exception("Error getting the temperature")

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

    MAX_THREADS = min(os.cpu_count(), len(clean_city))
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        cities_with_temp = list(executor.map(get_temperature_from_city, clean_city))

    return Response({"cities": cities_with_temp}, status=status.HTTP_200_OK)

