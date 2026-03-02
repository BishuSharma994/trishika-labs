import swisseph as swe
from datetime import datetime

SIGNS = [
    "Aries","Taurus","Gemini","Cancer",
    "Leo","Virgo","Libra","Scorpio",
    "Sagittarius","Capricorn","Aquarius","Pisces"
]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira",
    "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
    "Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
    "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]


class ParashariEngine:

    @staticmethod
    def to_julian(dob_str, time_str):
        dt = None

        for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y %I:%M %p"):
            try:
                dt = datetime.strptime(f"{dob_str} {time_str}", fmt)
                break
            except ValueError:
                continue

        if dt is None:
            raise ValueError("Invalid date/time format")

        decimal_hour = dt.hour + dt.minute / 60.0

        return swe.julday(
            dt.year,
            dt.month,
            dt.day,
            decimal_hour
        )

    @staticmethod
    def degree_to_sign(degree):
        index = int(degree / 30) % 12
        return SIGNS[index]

    @staticmethod
    def calculate_nakshatra(moon_degree):
        index = int(moon_degree / (360 / 27)) % 27
        return NAKSHATRAS[index]

    @staticmethod
    def generate_chart(dob, time, lat, lon, tz_offset=5.5):

        # Set Lahiri Ayanamsa (Sidereal Mode)
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        jd = ParashariEngine.to_julian(dob, time)

        # Convert local time to UTC
        jd -= tz_offset / 24.0

        planets = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mars": swe.MARS,
            "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS,
            "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE,
        }

        chart = {}

        for name, planet_id in planets.items():
            position, _ = swe.calc_ut(
                jd,
                planet_id,
                swe.FLG_SWIEPH | swe.FLG_SIDEREAL
            )
            lon_val = position[0] % 360
            chart[name] = lon_val

        # Sidereal Houses (Placidus for now)
        houses, ascmc = swe.houses_ex(
            jd,
            lat,
            lon,
            b'P',
            swe.FLG_SIDEREAL
        )

        ascendant_degree = ascmc[0] % 360

        lagna_sign = ParashariEngine.degree_to_sign(ascendant_degree)
        moon_sign = ParashariEngine.degree_to_sign(chart["Moon"])
        nakshatra_name = ParashariEngine.calculate_nakshatra(chart["Moon"])

        return {
            "lagna": lagna_sign,
            "moon_sign": moon_sign,
            "nakshatra": nakshatra_name,
            "planetary_longitudes": chart
        }