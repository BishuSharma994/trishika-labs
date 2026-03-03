from .natal import SIGNS

def _divisional_sign(deg, division):

    sign_index = int(deg / 30)
    part = int((deg % 30) / (30 / division))
    return SIGNS[(sign_index * division + part) % 12]


def compute_d10(base):

    d10 = {}
    for planet, deg in base["longitudes"].items():
        d10[planet] = _divisional_sign(deg, 10)
    return d10


def compute_d7(base):

    d7 = {}
    for planet, deg in base["longitudes"].items():
        d7[planet] = _divisional_sign(deg, 7)
    return d7


def compute_d12(base):

    d12 = {}
    for planet, deg in base["longitudes"].items():
        d12[planet] = _divisional_sign(deg, 12)
    return d12
