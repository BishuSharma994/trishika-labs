VIMSHOTTARI=[
("Ketu",7),("Venus",20),("Sun",6),
("Moon",10),("Mars",7),
("Rahu",18),("Jupiter",16),
("Saturn",19),("Mercury",17)
]

NAK_LORDS=["Ketu","Venus","Sun","Moon","Mars",
           "Rahu","Jupiter","Saturn","Mercury"]*3

def compute_dasha(base):

    moon_deg=base["longitudes"]["Moon"]
    nak_index=int(moon_deg/(360/27))
    lord=NAK_LORDS[nak_index]

    return {"current_mahadasha_lord":lord}