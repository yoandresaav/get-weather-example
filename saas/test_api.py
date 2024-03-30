import pytest

from unittest.mock import patch

from django.http import HttpRequest

from .views import get_temperature_from_city, get_temperature

@patch("requests.get")
def test_get_temperature_from_city(mock_requests_get):
    mock_response = {
        "daily": [{"temp": {"min": 25.5, "max": 30.5}}],
    }
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = mock_response
    city = {"lat": 40.7128, "lon": -74.0060}

    result = get_temperature_from_city(city)

    assert result["min"] == 25.5


def test_get_temperature_no_city():
    request = HttpRequest()
    request.GET = {}
    request.query_params = request.GET
    request.method = "GET"
    response = get_temperature(request)
    assert response.status_code == 400
    assert "error" in response.data


@patch("saas.views.get_temperature_from_city")
def test_get_temperature_valid_city(mock_get_temperature_from_city):

    mock_get_temperature_from_city.return_value = {
        "city": "New York",
        "lat": 40.7128,
        "lon": -74.0060,
        "min": 25.5,
        "max": 30.5,
    }
    with patch("requests.get") as mock_requests_get:
        mock_requests_get.return_value.status_code = 201
        mock_requests_get.return_value.json.return_value = [
            {"city_name": "New York", "lat": 40.7128, "long": -74.0060}
        ]
        request = HttpRequest()
        request.GET = {"city": "New York"}
        request.query_params = request.GET
        request.method = "GET"
        response = get_temperature(request)
        assert response.status_code == 200
        assert "cities" in response.data
        assert len(response.data["cities"]) == 1
        assert response.data["cities"][0]["min"] == 25.5


def test_get_temperature_invalid_city():
    # Test with an invalid city
    with patch("requests.get") as mock_requests_get:
        mock_requests_get.return_value.status_code = 400
        request = HttpRequest()
        request.GET = {"city": "Invalid City"}
        request.query_params = request.GET
        request.method = "GET"
        response = get_temperature(request)
        assert response.status_code == 400
        assert "error" in response.data
