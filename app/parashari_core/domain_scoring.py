import math
from statistics import mean


class DomainScorer:

    def __init__(self, engine_output: dict):
        self.shadbala = engine_output["shadbala"]
        self.ashtakavarga = engine_output["ashtakavarga"]["sarva"]
        self.bhavesh = engine_output["bhavesh"]
        self.current_dasha = engine_output["current_dasha"]
        self.activated_houses = engine_output["activated_houses"]

    # =========================================================
    # A) MATHEMATICAL SMOOTHING
    # =========================================================

    def _normalize_shadbala(self, planet):
        total = self.shadbala.get(planet, {}).get("total", 5.5)
        score = 100 / (1 + math.exp(-2 * (total - 5.5)))
        return min(max(score, 20), 90)

    def _normalize_ashtakavarga(self, house):
        points = self.ashtakavarga.get(house, 20)
        scaled = (points - 18) / (35 - 18)
        score = 30 + (scaled * 50)
        return min(max(score, 30), 80)

    def _house_structural(self, house):
        impact = self.bhavesh.get(house, {}).get("impact_score", 50)
        return min(max(impact, 30), 85)

    def _dasha_score(self, relevant_houses):
        score = 50
        for h in relevant_houses:
            if h in self.activated_houses:
                score += 15
        if any(h in [6, 8, 12] for h in self.activated_houses):
            score -= 10
        return min(max(score, 35), 80)

    # =========================================================

    def _planet_contribution(self, planet, relevance):
        shadbala = self._normalize_shadbala(planet)
        dasha_bonus = 15 if planet in self.current_dasha.values() else 0
        return (shadbala * 0.4) + (relevance * 0.4) + (dasha_bonus * 0.2)

    def _select_driver_and_risk(self, contributions):
        if not contributions:
            return "None", "None"
        sorted_planets = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_planets[0][0]
        risk = sorted_planets[-1][0] if len(sorted_planets) > 1 else "None"
        return primary, risk

    def _build(self, final_score, house_struct, lord_score,
               ashtakavarga_score, dasha_score, contributions):

        primary, risk = self._select_driver_and_risk(contributions)

        momentum = (
            "Positive" if final_score > 70
            else "Neutral" if final_score >= 50
            else "Challenging"
        )

        return {
            "score": round(final_score),
            "primary_driver": primary,
            "risk_factor": risk,
            "momentum": momentum,
            "components": {
                "house_structural": round(house_struct),
                "house_lord_strength": round(lord_score),
                "ashtakavarga": round(ashtakavarga_score),
                "dasha_activation": round(dasha_score)
            },
            "projection_next_year": min(round(final_score + 5), 85)
        }

    # =========================================================

    def _generic_domain(self, houses):

        house_struct = mean([self._house_structural(h) for h in houses])

        relevance = {}
        for h in houses:
            lord = self.bhavesh[h]["lord"]
            relevance[lord] = self._normalize_shadbala(lord)

        lord_score = mean(relevance.values())
        ashtakavarga_score = mean([self._normalize_ashtakavarga(h) for h in houses])
        dasha_score = self._dasha_score(houses)

        final_score = (
            house_struct * 0.25 +
            lord_score * 0.25 +
            ashtakavarga_score * 0.20 +
            dasha_score * 0.20 +
            50 * 0.10
        )

        contributions = {
            p: self._planet_contribution(p, relevance[p])
            for p in relevance
        }

        return self._build(
            final_score,
            house_struct,
            lord_score,
            ashtakavarga_score,
            dasha_score,
            contributions
        )

    def finance(self):
        return self._generic_domain([2, 11, 5])

    def marriage(self):
        return self._generic_domain([7, 2, 11])

    def career(self):
        return self._generic_domain([10, 6])

    def health(self):
        return self._generic_domain([1, 6, 8])