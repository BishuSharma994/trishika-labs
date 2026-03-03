from datetime import timedelta

VIMSHOTTARI_SEQUENCE = [
    ("Ketu",7),("Venus",20),("Sun",6),
    ("Moon",10),("Mars",7),
    ("Rahu",18),("Jupiter",16),
    ("Saturn",19),("Mercury",17)
]

NAK_LORDS = [
    "Ketu","Venus","Sun","Moon","Mars",
    "Rahu","Jupiter","Saturn","Mercury"
] * 3


def calculate_pratyantardasha(ad_planet, ad_years, ad_start):

    result = []
    sequence = VIMSHOTTARI_SEQUENCE
    ad_index = [p for p,_ in sequence].index(ad_planet)

    current = ad_start

    for i in range(9):
        pd_planet, pd_years = sequence[(ad_index+i)%9]

        duration_years = (ad_years * pd_years) / 120
        end = current + timedelta(days=duration_years*365.25)

        result.append({
            "pratyantardasha": pd_planet,
            "start": current.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d")
        })

        current = end

    return result


def calculate_antardasha(md_planet, md_years, md_start):

    result = []
    sequence = VIMSHOTTARI_SEQUENCE
    md_index = [p for p,_ in sequence].index(md_planet)

    current = md_start

    for i in range(9):
        ad_planet, ad_years = sequence[(md_index+i)%9]

        duration_years = (md_years * ad_years) / 120
        end = current + timedelta(days=duration_years*365.25)

        praty = calculate_pratyantardasha(
            ad_planet,
            duration_years,
            current
        )

        result.append({
            "antardasha": ad_planet,
            "start": current.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "pratyantardashas": praty
        })

        current = end

    return result


def compute_dasha(base):

    moon_deg = base["longitudes"]["Moon"]
    birth_dt = base["birth_datetime"]

    nak_index = int(moon_deg/(360/27))
    nak_lord = NAK_LORDS[nak_index]

    nak_size = 360/27
    completed = moon_deg % nak_size
    balance_ratio = 1 - (completed/nak_size)

    sequence = VIMSHOTTARI_SEQUENCE
    start_index = [p for p,_ in sequence].index(nak_lord)

    result = []

    # First Mahadasha (partial balance)
    md_planet, md_years = sequence[start_index]
    remaining_years = md_years * balance_ratio

    current_start = birth_dt
    current_end = current_start + timedelta(days=remaining_years*365.25)

    antardashas = calculate_antardasha(
        md_planet,
        remaining_years,
        current_start
    )

    result.append({
        "mahadasha": md_planet,
        "start": current_start.strftime("%Y-%m-%d"),
        "end": current_end.strftime("%Y-%m-%d"),
        "antardashas": antardashas
    })

    # Remaining 8 Mahadashas
    idx = (start_index+1)%9
    current_start = current_end

    for _ in range(8):

        md_planet, md_years = sequence[idx]
        current_end = current_start + timedelta(days=md_years*365.25)

        antardashas = calculate_antardasha(
            md_planet,
            md_years,
            current_start
        )

        result.append({
            "mahadasha": md_planet,
            "start": current_start.strftime("%Y-%m-%d"),
            "end": current_end.strftime("%Y-%m-%d"),
            "antardashas": antardashas
        })

        current_start = current_end
        idx = (idx+1)%9

    return result