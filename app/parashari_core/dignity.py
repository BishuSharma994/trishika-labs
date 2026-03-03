from .natal import sign_index, SIGNS

EXALTATION={"Sun":"Aries","Moon":"Taurus",
            "Mars":"Capricorn","Mercury":"Virgo",
            "Jupiter":"Cancer","Venus":"Pisces",
            "Saturn":"Libra"}

DEBILITATION={"Sun":"Libra","Moon":"Scorpio",
              "Mars":"Cancer","Mercury":"Pisces",
              "Jupiter":"Capricorn","Venus":"Virgo",
              "Saturn":"Aries"}

def compute_dignity(base):

    result={}
    for p,deg in base["longitudes"].items():

        sign=SIGNS[sign_index(deg)]

        if p in EXALTATION and EXALTATION[p]==sign:
            status="Exalted"
        elif p in DEBILITATION and DEBILITATION[p]==sign:
            status="Debilitated"
        else:
            status="Neutral"

        result[p]={"sign":sign,"status":status}

    return result