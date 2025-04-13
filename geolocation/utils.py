import requests
from requests.exceptions import RequestException

from geolocation.models import Place


def fetch_coordinates_from_api(apikey, address):
    """
    Запрашивает координаты адреса через API Яндекс.Карт.

    Возвращает (долгота, широта) или None, если не удалось получить координаты.
    """
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

        return lon, lat

    except (RequestException, ValueError)  as e:
        return None


def resolve_coordinates(address, apikey, cache=None):
    """
    Получает координаты для указанного адреса.

    Сначала пытается взять координаты из переданного кеша (если указан), затем из базы.
    Если координаты не найдены, запрашивает через API Яндекс.Карт, сохраняет результат в кеш и базу.

    Возвращает (широта, долгота) или None, если координаты не удалось получить.
    """
    if cache is not None and address in cache:
        return cache[address]

    place = Place.objects.filter(address=address).first()
    if place:
        coords = (place.latitude, place.longitude)
        if cache is not None:
            cache[address] = coords
        return coords

    coords = fetch_coordinates_from_api(apikey, address)
    if coords:
        lon, lat = coords
        Place.objects.update_or_create(
            address=address,
            defaults={
                'longitude': lon,
                'latitude': lat,
            }
        )
        coords = (lat, lon)
        if cache is not None:
            cache[address] = coords
        return coords

    if cache is not None:
        cache[address] = None
    return None
