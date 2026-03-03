import swisseph as swe
from math import fabs

NAISARGIKA_BALA = {
    "Sun": 60,
    "Moon": 51,
    "Venus": 43,
    "Jupiter": 34,
    "Mercury": 26,
    "Mars": 17,
    "Saturn": 9,
    "Rahu": 30,
    "Ketu": 30
}


def compute_sthana_bala(dignity):
    result = {}
    for planet, data in dignity.items():
        if data["status"] == "Exalted":
            result[planet] = 60
        elif data["status"] == "Debilitated":
            result[planet] = 0
        else:
            result[planet] = 30
    return result


def compute_dig_bala(houses):
    result = {}
    for planet, house in houses.items():
        if planet == "Sun" and house == 10:
            result[planet] = 60
        elif planet == "Moon" and house == 4:
            result[planet] = 60
        elif planet == "Mars" and house == 10:
            result[planet] = 60
        elif planet == "Jupiter" and house == 1:
            result[planet] = 60
        elif planet == "Venus" and house == 4:
            result[planet] = 60
        elif planet == "Saturn" and house == 7:
            result[planet] = 60
        else:
            result[planet] = 30
    return result


def compute_kala_bala(base):
    result = {}
    birth_hour = base["birth_datetime"].hour

    for planet in base["longitudes"]:
        if planet in ["Sun", "Mars", "Jupiter"]:
            result[planet] = 60 if 6 <= birth_hour <= 18 else 30
        else:
            result[planet] = 60 if birth_hour < 6 or birth_hour > 18 else 30
    return result


def compute_cheshta_bala(base):
    result = {}
    jd = base["jd"]

    for planet, pid in [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY),
        ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS),
        ("Saturn", swe.SATURN)
    ]:
        pos, _ = swe.calc_ut(jd, pid)
        speed = pos[3]
        result[planet] = min(60, fabs(speed) * 10)

    result["Rahu"] = 30
    result["Ketu"] = 30

    return result


def compute_drik_bala(aspects):
    result = {}
    for planet in aspects:
        aspect_count = len(aspects[planet])
        result[planet] = min(60, aspect_count * 10)
    return result


def compute_full_shadbala(base, houses, dignity, aspects):

    sthana = compute_sthana_bala(dignity)
    dig = compute_dig_bala(houses)
    kala = compute_kala_bala(base)
    cheshta = compute_cheshta_bala(base)
    drik = compute_drik_bala(aspects)

    result = {}

    for planet in base["longitudes"]:

        naisargika = NAISARGIKA_BALA.get(planet, 30)

        total = (
            sthana.get(planet, 0)
            + dig.get(planet, 0)
            + kala.get(planet, 0)
            + cheshta.get(planet, 0)
            + drik.get(planet, 0)
            + naisargika
        )

        result[planet] = {
            "sthāna_bala": round(sthana.get(planet, 0), 2),
            "dig_bala": round(dig.get(planet, 0), 2),
            "kāla_bala": round(kala.get(planet, 0), 2),
            "cheshta_bala": round(cheshta.get(planet, 0), 2),
            "naisargika_bala": round(naisargika, 2),
            "drik_bala": round(drik.get(planet, 0), 2),
            "total": round(total, 2)
        }

    return result