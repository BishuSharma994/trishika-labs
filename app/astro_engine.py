from datetime import datetime
from app.parashari_core.natal import compute_natal, sign_index, SIGNS
from app.parashari_core.houses import compute_houses
from app.parashari_core.navamsa import compute_navamsa, compute_d9_strength
from app.parashari_core.dignity import compute_dignity
from app.parashari_core.aspects import compute_aspects
from app.parashari_core.shadbala import compute_shadbala
from app.parashari_core.shadbala_full import compute_full_shadbala
from app.parashari_core.dasha import compute_dasha
from app.parashari_core.transit import compute_transit
from app.parashari_core.bhavesh import compute_bhavesh
from app.parashari_core.yogas import detect_yogas


class ParashariEngine:

    @staticmethod
    def generate_chart(dob, time, lat, lon):

        base = compute_natal(dob, time, lat, lon)
        houses = compute_houses(base)
        navamsa = compute_navamsa(base)
        dignity = compute_dignity(base)
        aspects = compute_aspects(houses)
        shadbala_simple = compute_shadbala(base, houses, dignity)
        shadbala_full = compute_full_shadbala(base, houses, dignity, aspects)
        full_dasha = compute_dasha(base)
        transit = compute_transit(base)
        bhavesh = compute_bhavesh(base, houses)
        yogas = detect_yogas(base, houses, bhavesh)
        d9_strength = compute_d9_strength(base, navamsa)

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
            "lagna": base["lagna_sign"],
            "moon_sign": moon_sign,
            "nakshatra": nakshatra,
            "planetary_longitudes": base["longitudes"],
            "planetary_houses": houses,

            "bhavesh": bhavesh,
            "yogas": yogas,
            "navamsa": navamsa,
            "d9_strength": d9_strength,
            "dignity": dignity,
            "shadbala": shadbala_simple,
            "shadbala_full": shadbala_full,
            "transit": transit,

            "current_dasha": {
                "mahadasha": current_md,
                "antardasha": current_ad,
                "pratyantardasha": current_pd
            }
        }