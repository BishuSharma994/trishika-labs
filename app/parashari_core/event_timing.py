def compute_house_activation(current_dasha, houses, bhavesh):

    activated_houses = set()

    md = current_dasha.get("mahadasha")
    ad = current_dasha.get("antardasha")
    pd = current_dasha.get("pratyantardasha")

    for planet in [md, ad, pd]:

        if not planet:
            continue

        if planet in houses:
            activated_houses.add(houses[planet])

        for house, data in bhavesh.items():
            if data["lord"] == planet:
                activated_houses.add(int(house))

    return sorted(list(activated_houses))