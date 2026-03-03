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


def sign_index(degree):
    return int(degree // 30)


# ============================================================
# ROBUST DATETIME PARSER
# ============================================================

def parse_datetime(dob: str, time: str):

    dob_obj = None
    dob_formats = ["%d-%m-%Y", "%Y-%m-%d"]

    for fmt in dob_formats:
        try:
            dob_obj = datetime.strptime(dob.strip(), fmt)
            break
        except ValueError:
            continue

    if dob_obj is None:
        raise ValueError("Invalid date format")

    time_obj = None
    time_formats = ["%H:%M", "%I:%M %p"]

    for fmt in time_formats:
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

def compute_natal(dob, time, lat, lon):

    birth_dt = parse_datetime(dob, time)

    swe.set_ephe_path("/usr/share/ephe")

    julian_day = swe.julday(
        birth_dt.year,
        birth_dt.month,
        birth_dt.day,
        birth_dt.hour + birth_dt.minute / 60.0
    )

    planets = {
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

    for name, body in planets.items():
        lon, _ = swe.calc_ut(julian_day, body)
        longitudes[name] = lon[0]

    # Ketu is opposite Rahu
    longitudes["Ketu"] = (longitudes["Rahu"] + 180) % 360

    # Lagna
    ascendant, _ = swe.houses(julian_day, lat, lon)
    lagna_degree = ascendant[0]
    lagna_sign = SIGNS[sign_index(lagna_degree)]

    return {
        "lagna_sign": lagna_sign,
        "longitudes": longitudes
    }