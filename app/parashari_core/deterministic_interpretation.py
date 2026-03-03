def generate_deterministic_summary(chart):

    summary = {}

    summary["strength_ranking"] = sorted(
        chart["shadbala"].items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )

    summary["weak_planets"] = [
        p for p, data in chart["shadbala"].items()
        if data["total"] < 150
    ]

    summary["high_sarva_houses"] = [
        h for h, v in chart["ashtakavarga"]["sarva"].items()
        if v >= 30
    ]

    summary["low_sarva_houses"] = [
        h for h, v in chart["ashtakavarga"]["sarva"].items()
        if v <= 20
    ]

    return summary
