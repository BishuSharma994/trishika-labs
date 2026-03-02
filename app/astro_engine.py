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
    def degree_to_sign_index(degree):
        return int(degree / 30) % 12

    @staticmethod
    def degree_to_sign(degree):
        return SIGNS[int(degree / 30) % 12]

    @staticmethod
    def calculate_nakshatra(moon_degree):
        return NAKSHATRAS[int(moon_degree / (360 / 27)) % 27]

    @staticmethod
    def map_planet_to_house(planet_degree, lagna_index):
        planet_sign_index = int(planet_degree / 30) % 12
        house_number = (planet_sign_index - lagna_index) % 12 + 1
        return house_number

    @staticmethod
    def generate_chart(dob, time, lat, lon, tz_offset=5.5):

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        jd = ParashariEngine.to_julian(dob, time)
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

        planetary_longitudes = {}

        for name, planet_id in planets.items():
            position, _ = swe.calc_ut(
                jd,
                planet_id,
                swe.FLG_SWIEPH | swe.FLG_SIDEREAL
            )
            planetary_longitudes[name] = position[0] % 360

        # Lagna from sidereal houses
        houses, ascmc = swe.houses_ex(
            jd,
            lat,
            lon,
            b'P',
            swe.FLG_SIDEREAL
        )

        ascendant_degree = ascmc[0] % 360
        lagna_index = ParashariEngine.degree_to_sign_index(ascendant_degree)

        house_mapping = {}

        for planet, degree in planetary_longitudes.items():
            house_mapping[planet] = ParashariEngine.map_planet_to_house(
                degree,
                lagna_index
            )

        return {
            "lagna_sign": SIGNS[lagna_index],
            "moon_sign": ParashariEngine.degree_to_sign(planetary_longitudes["Moon"]),
            "nakshatra": ParashariEngine.calculate_nakshatra(planetary_longitudes["Moon"]),
            "planetary_longitudes": planetary_longitudes,
            "planetary_houses": house_mapping
        }