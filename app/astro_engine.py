from app.parashari_core.natal import compute_natal
from app.parashari_core.houses import compute_houses
from app.parashari_core.navamsa import compute_navamsa
from app.parashari_core.dignity import compute_dignity
from app.parashari_core.aspects import compute_aspects
from app.parashari_core.shadbala import compute_shadbala
from app.parashari_core.dasha import compute_dasha
from app.parashari_core.transit import compute_transit

class ParashariEngine:

    @staticmethod
    def generate_chart(dob, time, lat, lon):

        base = compute_natal(dob, time, lat, lon)
        houses = compute_houses(base)
        navamsa = compute_navamsa(base)
        dignity = compute_dignity(base)
        aspects = compute_aspects(houses)
        shadbala = compute_shadbala(base, houses, dignity)
        dasha = compute_dasha(base)
        transit = compute_transit(base)

        return {
            "lagna": base["lagna_sign"],
            "planetary_longitudes": base["longitudes"],
            "houses": houses,
            "navamsa": navamsa,
            "dignity": dignity,
            "aspects": aspects,
            "shadbala": shadbala,
            "dasha": dasha,
            "transit": transit
        }