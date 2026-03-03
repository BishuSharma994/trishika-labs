from app.parashari_core.natal import compute_natal
from app.parashari_core.houses import compute_houses
from app.parashari_core.navamsa import compute_navamsa
from app.parashari_core.dignity import compute_dignity
from app.parashari_core.aspects import compute_aspects
from app.parashari_core.shadbala import compute_shadbala
from app.parashari_core.dasha import compute_dasha
from app.parashari_core.transit import compute_transit
from app.parashari_core.natal import sign_index, SIGNS

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

        # ---- Backward compatibility ----

        moon_deg = base["longitudes"]["Moon"]
        moon_sign = SIGNS[sign_index(moon_deg)]

        NAKSHATRAS = [
            "Ashwini","Bharani","Krittika","Rohini","Mrigashira",
            "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
            "Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
            "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
            "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
            "Purva Bhadrapada","Uttara Bhadrapada","Revati"
        ]

        nak_index = int(moon_deg / (360 / 27))
        nakshatra = NAKSHATRAS[nak_index]

        return {
            # Required by existing webhook
            "lagna": base["lagna_sign"],
            "moon_sign": moon_sign,
            "nakshatra": nakshatra,
            "planetary_longitudes": base["longitudes"],

            # Modular engine outputs
            "houses": houses,
            "navamsa": navamsa,
            "dignity": dignity,
            "aspects": aspects,
            "shadbala": shadbala,
            "dasha": dasha,
            "transit": transit
        }