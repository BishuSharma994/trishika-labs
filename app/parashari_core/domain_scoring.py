from statistics import mean


class DomainScorer:

    def __init__(self, engine_output: dict):
        self.shadbala = engine_output["shadbala"]
        self.ashtakavarga = engine_output["ashtakavarga"]["sarva"]
        self.bhavesh = engine_output["bhavesh"]
        self.current_dasha = engine_output["current_dasha"]
        self.activated_houses = engine_output["activated_houses"]

    # ---------------- Normalization ----------------

    def _normalize_shadbala(self, planet):
        total = self.shadbala.get(planet, {}).get("total", 0)
        return min(max((total / 6.0) * 100, 0), 100)

    def _normalize_ashtakavarga(self, house):
        points = self.ashtakavarga.get(house, 20)
        score = (points - 20) * 10
        return min(max(score, 0), 100)

    def _house_structural(self, house):
        impact = self.bhavesh.get(house, {}).get("impact_score", 50)
        return min(max(impact, 0), 100)

    def _dasha_score(self, relevant_houses):
        score = 50
        for h in relevant_houses:
            if h in self.activated_houses:
                score += 20
        if any(h in [6, 8, 12] for h in self.activated_houses):
            score -= 15
        return min(max(score, 0), 100)

    def _planet_contribution(self, planet, relevance):
        shadbala = self._normalize_shadbala(planet)
        dasha_bonus = 20 if planet in self.current_dasha.values() else 0
        return (shadbala * 0.4) + (relevance * 0.4) + (dasha_bonus * 0.2)

    def _select_driver_and_risk(self, contributions):
        if not contributions:
            return "None", "None"
        sorted_planets = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_planets[0][0]
        risk = sorted_planets[-1][0] if len(sorted_planets) > 1 else "None"
        return primary, risk

    def _build_response(self, final_score, house_struct, lord_score,
                        ashtakavarga_score, dasha_score, contributions):

        primary, risk = self._select_driver_and_risk(contributions)

        momentum = (
            "Positive" if final_score > 70
            else "Neutral" if final_score >= 45
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
            }
        }

    # ================= FINANCE =================

    def finance(self):
        houses = [2, 11, 5]

        house_struct = mean([self._house_structural(h) for h in houses])

        relevance = {}
        for h in houses:
            lord = self.bhavesh[h]["lord"]
            relevance[lord] = self._normalize_shadbala(lord)

        house_lord_score = mean(relevance.values())
        ashtakavarga_score = mean([self._normalize_ashtakavarga(h) for h in houses])
        dasha_score = self._dasha_score([2, 11, 5, 9])

        final_score = (
            house_struct * 0.30 +
            house_lord_score * 0.25 +
            ashtakavarga_score * 0.15 +
            dasha_score * 0.20 +
            50 * 0.10
        )

        contributions = {p: self._planet_contribution(p, relevance[p]) for p in relevance}

        return self._build_response(
            final_score, house_struct, house_lord_score,
            ashtakavarga_score, dasha_score, contributions
        )

    # ================= MARRIAGE =================

    def marriage(self):
        houses = [7, 2, 11]

        house_struct = mean([self._house_structural(h) for h in houses])

        seventh_lord = self.bhavesh[7]["lord"]
        venus = "Venus"

        relevance = {
            seventh_lord: self._normalize_shadbala(seventh_lord),
            venus: self._normalize_shadbala(venus)
        }

        house_lord_score = mean(relevance.values())
        ashtakavarga_score = self._normalize_ashtakavarga(7)
        dasha_score = self._dasha_score(houses)

        final_score = (
            house_struct * 0.30 +
            house_lord_score * 0.25 +
            ashtakavarga_score * 0.15 +
            dasha_score * 0.20 +
            50 * 0.10
        )

        contributions = {p: self._planet_contribution(p, relevance[p]) for p in relevance}

        return self._build_response(
            final_score, house_struct, house_lord_score,
            ashtakavarga_score, dasha_score, contributions
        )

    # ================= CAREER =================

    def career(self):
        houses = [10, 6]

        house_struct = mean([self._house_structural(h) for h in houses])

        tenth_lord = self.bhavesh[10]["lord"]
        saturn = "Saturn"

        relevance = {
            tenth_lord: self._normalize_shadbala(tenth_lord),
            saturn: self._normalize_shadbala(saturn)
        }

        house_lord_score = mean(relevance.values())
        ashtakavarga_score = self._normalize_ashtakavarga(10)
        dasha_score = self._dasha_score([10, 6, 2, 11])

        final_score = (
            house_struct * 0.30 +
            house_lord_score * 0.25 +
            ashtakavarga_score * 0.15 +
            dasha_score * 0.20 +
            50 * 0.10
        )

        contributions = {p: self._planet_contribution(p, relevance[p]) for p in relevance}

        return self._build_response(
            final_score, house_struct, house_lord_score,
            ashtakavarga_score, dasha_score, contributions
        )

    # ================= HEALTH =================

    def health(self):
        house_struct = mean([
            self._house_structural(1),
            100 - self._house_structural(6),
            100 - self._house_structural(8)
        ])

        lagna_lord = self.bhavesh[1]["lord"]
        sixth_lord = self.bhavesh[6]["lord"]
        eighth_lord = self.bhavesh[8]["lord"]

        relevance = {
            lagna_lord: self._normalize_shadbala(lagna_lord),
            sixth_lord: 100 - self._normalize_shadbala(sixth_lord),
            eighth_lord: 100 - self._normalize_shadbala(eighth_lord)
        }

        house_lord_score = mean(relevance.values())
        ashtakavarga_score = self._normalize_ashtakavarga(1)
        dasha_score = self._dasha_score([1, 6, 8, 12])

        final_score = (
            house_struct * 0.30 +
            house_lord_score * 0.25 +
            ashtakavarga_score * 0.15 +
            dasha_score * 0.20 +
            50 * 0.10
        )

        contributions = {p: self._planet_contribution(p, relevance[p]) for p in relevance}

        return self._build_response(
            final_score, house_struct, house_lord_score,
            ashtakavarga_score, dasha_score, contributions
        )