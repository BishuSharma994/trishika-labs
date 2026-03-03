from datetime import datetime
from functools import lru_cache

from app.parashari_core.natal import compute_natal, sign_index, SIGNS
from app.parashari_core.houses import compute_houses
from app.parashari_core.navamsa import compute_navamsa, compute_d9_strength
from app.parashari_core.dignity import compute_dignity
from app.parashari_core.aspects import compute_aspects
from app.parashari_core.shadbala_full import compute_full_shadbala
from app.parashari_core.dasha import compute_dasha
from app.parashari_core.transit import compute_transit
from app.parashari_core.bhavesh import compute_bhavesh
from app.parashari_core.yogas import detect_yogas
from app.parashari_core.ashtakavarga import compute_ashtakavarga
from app.parashari_core.vargas import compute_d10, compute_d7, compute_d12
from app.parashari_core.event_timing import compute_house_activation
from app.parashari_core.life_windows import detect_marriage_window, detect_career_window
from app.parashari_core.deterministic_interpretation import generate_deterministic_summary
from app.parashari_core.domain_scoring import DomainScorer


class ParashariEngine:

    @staticmethod
    @lru_cache(maxsize=256)
    def generate_chart(dob, time, lat, lon):

        base = compute_natal(dob, time, lat, lon)
        houses = compute_houses(base)
        navamsa = compute_navamsa(base)
        dignity = compute_dignity(base)
        aspects = compute_aspects(houses)

        shadbala_full = compute_full_shadbala(base, houses, dignity, aspects)
        full_dasha = compute_dasha(base)
        transit = compute_transit(base)

        bhavesh = compute_bhavesh(base, houses)
        yogas = detect_yogas(base, houses, bhavesh)
        ashtakavarga = compute_ashtakavarga(base, houses)

        d9_strength = compute_d9_strength(base, navamsa)
        d10 = compute_d10(base)
        d7 = compute_d7(base)
        d12 = compute_d12(base)

        today = datetime.utcnow().date()

        current_md = current_ad = current_pd = None

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

        current_dasha = {
            "mahadasha": current_md,
            "antardasha": current_ad,
            "pratyantardasha": current_pd
        }

        activated_houses = compute_house_activation(
            current_dasha,
            houses,
            bhavesh
        )

        marriage_window = detect_marriage_window(activated_houses, yogas)
        career_window = detect_career_window(activated_houses, yogas)

        deterministic_summary = generate_deterministic_summary({
            "shadbala": shadbala_full,
            "ashtakavarga": ashtakavarga
        })

        # =========================================================
        # DOMAIN SCORING
        # =========================================================

        scorer = DomainScorer({
            "shadbala": shadbala_full,
            "ashtakavarga": ashtakavarga,
            "bhavesh": bhavesh,
            "current_dasha": current_dasha,
            "activated_houses": activated_houses
        })

        domain_scores = {
            "finance": scorer.finance(),
            "marriage": scorer.marriage(),
            "career": scorer.career(),
            "health": scorer.health()
        }

        # =========================================================
        # B) INTER-DOMAIN CORRELATION
        # =========================================================

        domain_scores["finance"]["score"] = round(
            (domain_scores["finance"]["score"] * 0.85) +
            (domain_scores["career"]["score"] * 0.15)
        )

        domain_scores["marriage"]["score"] = round(
            (domain_scores["marriage"]["score"] * 0.90) +
            (domain_scores["health"]["score"] * 0.10)
        )

        domain_scores["health"]["score"] = round(
            (domain_scores["health"]["score"] * 0.90) +
            (domain_scores["marriage"]["score"] * 0.10)
        )

        moon_deg = base["longitudes"]["Moon"]
        moon_sign = SIGNS[sign_index(moon_deg)]

        return {
            "lagna": base["lagna_sign"],
            "moon_sign": moon_sign,
            "planetary_longitudes": base["longitudes"],
            "planetary_houses": houses,
            "dignity": dignity,
            "bhavesh": bhavesh,
            "yogas": yogas,
            "navamsa": navamsa,
            "d9_strength": d9_strength,
            "d10": d10,
            "d7": d7,
            "d12": d12,
            "shadbala": shadbala_full,
            "ashtakavarga": ashtakavarga,
            "transit": transit,
            "current_dasha": current_dasha,
            "activated_houses": activated_houses,
            "marriage_window_active": marriage_window,
            "career_window_active": career_window,
            "deterministic_summary": deterministic_summary,
            "domain_scores": domain_scores
        }