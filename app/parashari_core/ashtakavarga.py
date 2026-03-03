from .natal import sign_index

# Classical point allocation reference (simplified structure)
# Each planet gives points to certain houses from itself
ASHTAKAVARGA_RULES = {
    "Sun": [1,2,4,7,8,9,10,11],
    "Moon": [1,3,6,7,10,11],
    "Mars": [1,2,4,7,8,10,11],
    "Mercury": [1,2,4,5,6,8,9,10,11],
    "Jupiter": [1,2,4,5,7,9,10,11],
    "Venus": [1,2,3,4,5,8,9,10,11],
    "Saturn": [1,2,3,4,7,8,10,11],
    "Rahu": [1,2,4,7,8,10,11],
    "Ketu": [1,2,4,7,8,10,11],
}


def compute_binna_ashtakavarga(base, houses):

    binna = {}

    for planet in houses:
        binna[planet] = {i: 0 for i in range(1,13)}

        for relative_house in ASHTAKAVARGA_RULES.get(planet, []):
            target_house = ((houses[planet] + relative_house - 2) % 12) + 1
            binna[planet][target_house] += 1

    return binna


def compute_sarva_ashtakavarga(binna):

    sarva = {i: 0 for i in range(1,13)}

    for planet in binna:
        for house in binna[planet]:
            sarva[house] += binna[planet][house]

    return sarva


def compute_ashtakavarga(base, houses):

    binna = compute_binna_ashtakavarga(base, houses)
    sarva = compute_sarva_ashtakavarga(binna)

    return {
        "binna": binna,
        "sarva": sarva
    }
