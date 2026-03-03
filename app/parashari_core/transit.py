import swisseph as swe
from datetime import datetime
from .natal import sign_index

def compute_transit(base):

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    now=datetime.utcnow()
    jd=swe.julday(
        now.year,now.month,now.day,
        now.hour+now.minute/60
    )

    planets={
        "Sun":swe.SUN,"Moon":swe.MOON,
        "Mars":swe.MARS,"Mercury":swe.MERCURY,
        "Jupiter":swe.JUPITER,"Venus":swe.VENUS,
        "Saturn":swe.SATURN,"Rahu":swe.TRUE_NODE
    }

    result={}
    lagna=base["lagna_index"]

    for p,pid in planets.items():
        pos,_=swe.calc_ut(
            jd,pid,
            swe.FLG_SWIEPH|swe.FLG_SIDEREAL
        )
        deg=pos[0]%360
        result[p]=(sign_index(deg)-lagna)%12+1

    return result