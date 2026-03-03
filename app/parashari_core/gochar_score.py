def compute_gochar_score(transit, sarva):

    score = {}

    for planet, house in transit.items():
        strength = sarva.get(house, 0)
        score[planet] = strength

    return score
