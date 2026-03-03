def detect_yogas(base, houses, bhavesh):

    yogas = []

    # Raja Yoga: Trine lord in Kendra
    for house, data in bhavesh.items():
        if house in [5, 9] and data["lord_house"] in [1, 4, 7, 10]:
            yogas.append("Raja Yoga")

    # Dhana Yoga: 2nd lord + 11th lord in same house
    lord_2 = bhavesh[2]["lord"]
    lord_11 = bhavesh[11]["lord"]

    if houses[lord_2] == houses[lord_11]:
        yogas.append("Dhana Yoga")

    return list(set(yogas))