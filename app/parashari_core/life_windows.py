def detect_marriage_window(activated_houses, yogas):

    score = 0

    if 7 in activated_houses:
        score += 3
    if 5 in activated_houses:
        score += 2
    if 2 in activated_houses:
        score += 1

    for yoga in yogas:
        if "Marriage" in yoga or "Venus" in yoga:
            score += 2

    return score >= 5


def detect_career_window(activated_houses, yogas):

    score = 0

    if 10 in activated_houses:
        score += 3
    if 6 in activated_houses:
        score += 2
    if 11 in activated_houses:
        score += 1

    for yoga in yogas:
        if "Raja" in yoga or "Dhana" in yoga:
            score += 2

    return score >= 5
