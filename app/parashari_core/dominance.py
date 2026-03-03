# app/parashari_core/dominance.py

def compute_planet_dominance(domain_scores: dict):

    counter = {}

    for domain in domain_scores.values():
        planet = domain["primary_driver"]
        counter[planet] = counter.get(planet, 0) + 1

    dominant = max(counter, key=counter.get)

    return {
        "dominant_planet": dominant,
        "count": counter[dominant],
        "distribution": counter
    }