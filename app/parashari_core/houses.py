from .natal import sign_index

def compute_houses(base):

    lagna=base["lagna_index"]
    result={}

    for p,deg in base["longitudes"].items():
        result[p]=(sign_index(deg)-lagna)%12+1

    return result