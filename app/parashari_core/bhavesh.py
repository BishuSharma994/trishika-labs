from .natal import SIGNS

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter"
}

def compute_bhavesh(base, houses):

    lagna_index = base["lagna_index"]
    result = {}

    for house in range(1, 13):

        sign_index_house = (lagna_index + house - 1) % 12
        sign = SIGNS[sign_index_house]

        lord = SIGN_LORDS[sign]
        lord_house = houses[lord]

        score = 0

        if lord_house in [1, 5, 9]:
            score += 3

        if lord_house in [1, 4, 7, 10]:
            score += 2

        if lord_house in [6, 8, 12]:
            score -= 2

        result[house] = {
            "sign": sign,
            "lord": lord,
            "lord_house": lord_house,
            "impact_score": score
        }

    return result