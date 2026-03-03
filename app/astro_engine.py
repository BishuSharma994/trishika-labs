from app.parashari_core.natal import compute_natal
from app.parashari_core.houses import compute_houses
from app.parashari_core.navamsa import compute_navamsa
from app.parashari_core.dignity import compute_dignity
from app.parashari_core.aspects import compute_aspects
from app.parashari_core.shadbala import compute_shadbala
from app.parashari_core.dasha import compute_dasha
from app.parashari_core.transit import compute_transit
from app.parashari_core.natal import sign_index, SIGNS
from datetime import datetime

class ParashariEngine:

    @staticmethod
    def generate_chart(dob, time, lat, lon):

        base = compute_natal(dob, time, lat, lon)
        houses = compute_houses(base)
        navamsa = compute_navamsa(base)
        dignity = compute_dignity(base)
        aspects = compute_aspects(houses)
        shadbala = compute_shadbala(base, houses, dignity)
        full_dasha = compute_dasha(base)
        transit = compute_transit(base)

        # ---- Moon Sign ----
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

        # ---- Extract Current Dasha ----
        today = datetime.utcnow().date()

        current_md = None
        current_ad = None
        current_pd = None

        for md in full_dasha:
            if md["start"] <= str(today) <= md["end"]:
                current_md = md["mahadasha"]
                for ad in md["antardashas"]:
                    if ad["start"] <= str(today) <= ad["end"]:
                        current_ad = ad["antardasha"]
                        for pd in ad["pratyantardashas"]:
                            if pd["start"] <= str(today) <= pd["end"]:
                                current_pd = pd["pratyantardasha"]
                                break
                        break
                break

        return {
            # Required legacy keys
            "lagna": base["lagna_sign"],
            "moon_sign": moon_sign,
            "nakshatra": nakshatra,
            "planetary_longitudes": base["longitudes"],
            "planetary_houses": houses,

            # Deterministic engine data
            "houses": houses,
            "navamsa": navamsa,
            "dignity": dignity,
            "shadbala": shadbala,
            "transit": transit,

            # Current Dasha focus
            "current_dasha": {
                "mahadasha": current_md,
                "antardasha": current_ad,
                "pratyantardasha": current_pd
            }
        }

