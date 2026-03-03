from .natal import sign_index, SIGNS

MOVABLE=["Aries","Cancer","Libra","Capricorn"]
FIXED=["Taurus","Leo","Scorpio","Aquarius"]
DUAL=["Gemini","Virgo","Sagittarius","Pisces"]

def compute_navamsa(base):

    navamsa={}
    for p,deg in base["longitudes"].items():

        sign_idx=int(deg/30)
        sign=SIGNS[sign_idx]
        part=int((deg%30)/(30/9))

        if sign in MOVABLE:
            start=sign_idx
        elif sign in FIXED:
            start=(sign_idx+8)%12
        else:
            start=(sign_idx+4)%12

        navamsa[p]=SIGNS[(start+part)%12]

    return navamsa