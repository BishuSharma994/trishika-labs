# app/parashari_core/time_projection.py

import statistics

def project_domain_over_time(domain_score: dict, months: int = 12):
    """
    Deterministic projection model.
    Drift model based on base score.
    No randomness.
    """

    base = domain_score["score"]
    projections = []

    for m in range(1, months + 1):

        drift = m * 0.8
        periodic_drag = (m % 3) * 1.5

        value = base + drift - periodic_drag
        value = max(0, min(100, round(value)))

        projections.append(value)

    return projections


def compute_volatility(projections: list):
    if len(projections) < 2:
        return 0
    return round(statistics.stdev(projections), 2)