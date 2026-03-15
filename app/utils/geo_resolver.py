import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
DELHI_LAT = 28.6139
DELHI_LON = 77.2090


def resolve_coordinates(city: str):
    """Resolve city/place to coordinates using Nominatim; fallback to Delhi."""
    query = (city or "").strip()

    if not query:
        return DELHI_LAT, DELHI_LON

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "json",
                "limit": 1,
            },
            headers={"User-Agent": "trishika-labs-bot/1.0"},
            timeout=6,
        )
        response.raise_for_status()

        payload = response.json()
        if payload:
            lat = float(payload[0].get("lat"))
            lon = float(payload[0].get("lon"))
            return lat, lon
    except Exception:
        pass

    return DELHI_LAT, DELHI_LON


def search_place_candidates(query: str, limit: int = 5):
    """Return a list of place display names from Nominatim."""
    q = (query or "").strip()
    if not q:
        return []

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": q,
                "format": "json",
                "limit": max(1, min(int(limit or 5), 8)),
            },
            headers={"User-Agent": "trishika-labs-bot/1.0"},
            timeout=6,
        )
        response.raise_for_status()

        payload = response.json()
        results = []
        for item in payload or []:
            name = str(item.get("display_name") or "").strip()
            if name and name not in results:
                results.append(name)
        return results
    except Exception:
        return []


class GeoResolver:
    @staticmethod
    def resolve(place: str):
        return resolve_coordinates(place)
