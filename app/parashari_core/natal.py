from datetime import datetime
import swisseph as swe

# ============================================================
# CONSTANTS
# ============================================================

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def sign_index(degree: float) -> int:
    return int(degree // 30)


# ============================================================
# ROBUST DATETIME PARSER
# ============================================================

def parse_datetime(dob: str, time: str) -> datetime:

    dob_obj = None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            dob_obj = datetime.strptime(dob.strip(), fmt)
            break
        except ValueError:
            continue

    if dob_obj is None:
        raise ValueError("Invalid date format")

    time_obj = None
    for fmt in ("%H:%M", "%I:%M %p"):
        try:
            time_obj = datetime.strptime(time.strip(), fmt)
            break
        except ValueError:
            continue

    if time_obj is None:
        raise ValueError("Invalid time format")

    return datetime(
        dob_obj.year,
        dob_obj.month,
        dob_obj.day,
        time_obj.hour,
        time_obj.minute
    )


# ============================================================
# NATAL COMPUTATION
# ============================================================

def compute_natal(dob: str, time: str, latitude: float, longitude: float):

    birth_dt = parse_datetime(dob, time)

    swe.set_ephe_path("/usr/share/ephe")

    jd = swe.julday(
        birth_dt.year,
        birth_dt.month,
        birth_dt.day,
        birth_dt.hour + birth_dt.minute / 60.0
    )

    planet_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }

    longitudes = {}

    for name, body in planet_map.items():
        result = swe.calc_ut(jd, body)
        longitudes[name] = result[0][0]

    # Ketu opposite Rahu
    longitudes["Ketu"] = (longitudes["Rahu"] + 180) % 360

    # ---------------------------------------------------------
    # Correct Swiss houses usage
    # ---------------------------------------------------------

    house_cusps, ascmc = swe.houses(jd, latitude, longitude)

    asc_degree = ascmc[0]
    lagna_idx = sign_index(asc_degree)
    lagna_sign = SIGNS[lagna_idx]

    return {
        "lagna_sign": lagna_sign,
        "lagna_index": lagna_idx,
        "lagna_degree": asc_degree,
        "longitudes": longitudes,
        "birth_datetime": birth_dt
    }