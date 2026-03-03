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
from app.parashari_core.ashtakavarga import compute_ashtakavarga
from app.parashari_core.vargas import compute_d10, compute_d7, compute_d12
from app.parashari_core.gochar_score import compute_gochar_score
from app.parashari_core.prediction_engine import compute_prediction_score


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

        ashtakavarga = compute_ashtakavarga(base, houses)

        d10 = compute_d10(base)
        d7 = compute_d7(base)
        d12 = compute_d12(base)

        d9_strength = compute_d9_strength(base, navamsa)

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

        gochar_score = compute_gochar_score(transit, ashtakavarga["sarva"])

        prediction_score = compute_prediction_score(
            {
                "mahadasha": current_md,
                "antardasha": current_ad
            },
            shadbala_full,
            gochar_score,
            yogas
        )

        moon_deg = base["longitudes"]["Moon"]
        moon_sign = SIGNS[sign_index(moon_deg)]

        return {
            "lagna": base["lagna_sign"],
            "moon_sign": moon_sign,
            "planetary_houses": houses,
            "planetary_longitudes": base["longitudes"],

            "bhavesh": bhavesh,
            "yogas": yogas,
            "navamsa": navamsa,
            "d9_strength": d9_strength,
            "d10": d10,
            "d7": d7,
            "d12": d12,
            "dignity": dignity,
            "shadbala": shadbala_full,
            "ashtakavarga": ashtakavarga,
            "transit": transit,

            "current_dasha": {
                "mahadasha": current_md,
                "antardasha": current_ad,
                "pratyantardasha": current_pd
            },

            "prediction_score": prediction_score
        }