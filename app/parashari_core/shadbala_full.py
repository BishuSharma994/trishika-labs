def compute_full_shadbala(base, houses, dignity):

    result = {}

    for planet in base["longitudes"]:

        result[planet] = {
            "sthāna_bala": 0,
            "dig_bala": 0,
            "kāla_bala": 0,
            "chesta_bala": 0,
            "naisargika_bala": 0,
            "drik_bala": 0,
            "total": 0
        }

    return result