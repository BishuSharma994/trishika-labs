import swisseph as swe
from datetime import datetime

SIGNS = [
    "Aries","Taurus","Gemini","Cancer",
    "Leo","Virgo","Libra","Scorpio",
    "Sagittarius","Capricorn","Aquarius","Pisces"
]

def parse_datetime(dob, time):
    for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y %I:%M %p"):
        try:
            return datetime.strptime(f"{dob} {time}", fmt)
        except:
            continue
    raise ValueError("Invalid date/time format")

def sign_index(deg):
    return int(deg/30) % 12

def compute_natal(dob, time, lat, lon, tz_offset=5.5):

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    birth_dt = parse_datetime(dob,time)

    jd = swe.julday(
        birth_dt.year,
        birth_dt.month,
        birth_dt.day,
        birth_dt.hour + birth_dt.minute/60
    ) - tz_offset/24

    planets = {
        "Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,
        "Mercury":swe.MERCURY,"Jupiter":swe.JUPITER,
        "Venus":swe.VENUS,"Saturn":swe.SATURN,
        "Rahu":swe.TRUE_NODE
    }

    longitudes={}
    for p,pid in planets.items():
        pos,_=swe.calc_ut(
            jd,pid,
            swe.FLG_SWIEPH|swe.FLG_SIDEREAL
        )
        longitudes[p]=pos[0]%360

    longitudes["Ketu"]=(longitudes["Rahu"]+180)%360

    houses,ascmc=swe.houses_ex(
        jd,lat,lon,b'P',
        swe.FLG_SIDEREAL
    )

    asc=ascmc[0]%360
    lagna_idx=sign_index(asc)

    return {
        "jd":jd,
        "longitudes":longitudes,
        "lagna_index":lagna_idx,
        "lagna_sign":SIGNS[lagna_idx]
    }