def compute_prediction_score(current_dasha, shadbala, gochar_score, yogas):

    score = 0

    md = current_dasha.get("mahadasha")
    ad = current_dasha.get("antardasha")

    if md and md in shadbala:
        score += shadbala[md]["total"] * 0.4

    if ad and ad in shadbala:
        score += shadbala[ad]["total"] * 0.3

    score += sum(gochar_score.values()) * 0.1

    score += len(yogas) * 5

    return round(score, 2)
