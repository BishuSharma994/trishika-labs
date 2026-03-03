# app/parashari_core/correlation.py

def apply_dynamic_correlation(domain_scores: dict):

    order = ["finance", "marriage", "career", "health"]

    vector = [domain_scores[d]["score"] for d in order]

    M = [
        [0.75, 0.00, 0.20, 0.05],
        [0.00, 0.80, 0.00, 0.20],
        [0.25, 0.00, 0.70, 0.05],
        [0.10, 0.20, 0.10, 0.60],
    ]

    drivers = [domain_scores[d]["primary_driver"] for d in order]

    # Boost correlation if shared driver
    if len(set(drivers)) < 4:
        M[0][2] += 0.05
        M[2][0] += 0.05

    new_vector = []

    for row in M:
        new_value = sum(row[i] * vector[i] for i in range(4))
        new_vector.append(round(new_value))

    for i, domain in enumerate(order):
        domain_scores[domain]["score"] = new_vector[i]

    return domain_scores