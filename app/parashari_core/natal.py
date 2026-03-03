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
    """
    Supported DOB formats:
        - DD-MM-YYYY
        - YYYY-MM-DD

    Supported Time formats:
        - HH:MM (24h)
        - HH:MM AM/PM
    """

    # -------------------------
    # Parse Date
    # -------------------------

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

    # -------------------------
    # Parse Time
    # -------------------------

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

    # -------------------------
    # Combine
    # -------------------------

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

def compute_natal(dob: str, time: str, lat: float, lon: float):

    birth_dt = parse_datetime(dob, time)

    # Swiss Ephemeris path (Railway compatible)
    swe.set_ephe_path("/usr/share/ephe")

    # Julian Day
    julian_day = swe.julday(
        birth_dt.year,
        birth_dt.month,
        birth_dt.day,
        birth_dt.hour + birth_dt.minute / 60.0
    )

    # Planet mapping
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

    # Compute planetary longitudes
    for name, body in planets.items():
        result = swe.calc_ut(julian_day, body)
        longitude = result[0][0]
        longitudes[name] = longitude

    # Ketu opposite Rahu
    longitudes["Ketu"] = (longitudes["Rahu"] + 180) % 360

    # -------------------------------------------------------
    # CORRECT Swiss Ephemeris houses call
    # -------------------------------------------------------

    houses, ascmc = swe.houses(julian_day, lat, lon)

    # Ascendant is first value of ascmc
    lagna_degree = ascmc[0]
    lagna_sign = SIGNS[sign_index(lagna_degree)]

    return {
        "lagna_sign": lagna_sign,
        "longitudes": longitudes
    }