from .natal import sign_index

PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]

# Classical reference house offsets (simplified but structured)
CLASSICAL_RULES = {
    "Sun": [1,2,4,7,8,9,10,11],
    "Moon": [1,3,6,7,10,11],
    "Mars": [1,2,4,7,8,10,11],
    "Mercury": [1,2,4,5,6,8,9,10,11],
    "Jupiter": [1,2,4,5,7,9,10,11],
    "Venus": [1,2,3,4,5,8,9,10,11],
    "Saturn": [1,2,3,4,7,8,10,11],
}

def compute_binna_ashtakavarga(base, houses):

    matrix = {}

    for planet in PLANETS:
        matrix[planet] = {i: 0 for i in range(1,13)}

        for contributor in PLANETS:
            rel_house = ((houses[contributor] - houses[planet]) % 12) + 1
            if rel_house in CLASSICAL_RULES.get(planet, []):
                matrix[planet][houses[contributor]] += 1

    return matrix


def compute_sarva_ashtakavarga(matrix):

    sarva = {i: 0 for i in range(1,13)}

    for planet in matrix:
        for house, value in matrix[planet].items():
            sarva[house] += value

    return sarva


def compute_ashtakavarga(base, houses):

    binna = compute_binna_ashtakavarga(base, houses)
    sarva = compute_sarva_ashtakavarga(binna)

    return {
        "binna": binna,
        "sarva": sarva
    }