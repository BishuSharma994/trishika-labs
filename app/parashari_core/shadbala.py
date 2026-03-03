NAISARGIKA={"Sun":60,"Moon":51,"Venus":43,
            "Jupiter":34,"Mercury":26,
            "Mars":17,"Saturn":9}

def compute_shadbala(base,houses,dignity):

    result={}

    for p in base["longitudes"]:

        sthana=20 if dignity[p]["status"]=="Exalted" else 10
        dig=10 if houses[p]==10 else 5
        nais=NAISARGIKA.get(p,20)/6

        total=round(sthana+dig+nais,2)

        result[p]={
            "sthāna":sthana,
            "dig":dig,
            "naisargika":round(nais,2),
            "total":total
        }

    return result