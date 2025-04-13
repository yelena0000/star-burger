from geolocation.models import Place
import requests
from requests.exceptions import RequestException


def fetch_coordinates(apikey, address):
    place = Place.objects.filter(address=address).first()
    if place:
        return place.longitude, place.latitude

    try:
        response = requests.get(
            "https://geocode-maps.yandex.ru/1.x",
            params={
                "geocode": address,
                "apikey": apikey,
                "format": "json",
            }
        )
        response.raise_for_status()

        found_places = response.json()['response']['GeoObjectCollection']['featureMember']
        if not found_places:
            return None

        most_relevant = found_places[0]
        lon_str, lat_str = most_relevant['GeoObject']['Point']['pos'].split(" ")
        lon, lat = float(lon_str), float(lat_str)

        Place.objects.create(
            address=address,
            longitude=lon,
            latitude=lat
        )
        return lon, lat

    except (RequestException, ValueError) as e:
        return None
