ASPECT_RULES={
    "Sun":[7],"Moon":[7],"Mercury":[7],"Venus":[7],
    "Mars":[4,7,8],"Jupiter":[5,7,9],
    "Saturn":[3,7,10],"Rahu":[7],"Ketu":[7]
}

def compute_aspects(houses):

    result={}
    for p,h in houses.items():
        result[p]=[((h+a-1)%12+1)
                   for a in ASPECT_RULES[p]]

    return result