import requests
from shapely.geometry import Point


def geocode(q: str) -> Point:
    """
    Geocodes an address from a query
    :param q: String containing an address to geocode
    :return: shapely Point object
    """
    url = "https://loc.geopunt.be/v4/Location"
    params = {
        "q": q
    }
    res = requests.get(url, params=params)
    res_json = res.json()
    x = res_json['LocationResult'][0]['Location']['X_Lambert72']
    y = res_json['LocationResult'][0]['Location']['Y_Lambert72']
    return Point(x, y)

