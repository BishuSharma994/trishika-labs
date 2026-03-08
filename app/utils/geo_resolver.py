import requests


class GeoResolver:

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    DELHI_LAT = 28.6139
    DELHI_LON = 77.2090

    @staticmethod
    def resolve(place):
        query = (place or "").strip()
        if not query:
            return GeoResolver.DELHI_LAT, GeoResolver.DELHI_LON

        try:
            response = requests.get(
                GeoResolver.NOMINATIM_URL,
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1
                },
                headers={
                    "User-Agent": "trishika-labs-bot/1.0"
                },
                timeout=6
            )
            response.raise_for_status()
            payload = response.json()

            if payload:
                lat = float(payload[0]["lat"])
                lon = float(payload[0]["lon"])
                return lat, lon
        except Exception:
            pass

        return GeoResolver.DELHI_LAT, GeoResolver.DELHI_LON
