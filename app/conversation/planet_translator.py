class PlanetTranslator:

    MAP_DEV = {
        "Sun": "सूर्य",
        "Moon": "चंद्र",
        "Mars": "मंगल",
        "Mercury": "बुध",
        "Jupiter": "गुरु",
        "Venus": "शुक्र",
        "Saturn": "शनि",
        "Rahu": "राहु",
        "Ketu": "केतु"
    }

    MAP_ROM = {
        "Sun": "Surya",
        "Moon": "Chandra",
        "Mars": "Mangal",
        "Mercury": "Budh",
        "Jupiter": "Guru",
        "Venus": "Shukra",
        "Saturn": "Shani",
        "Rahu": "Rahu",
        "Ketu": "Ketu"
    }

    @staticmethod
    def translate(name, language, script):

        if language != "hi":
            return name

        if script == "devanagari":
            return PlanetTranslator.MAP_DEV.get(name, name)

        if script == "roman":
            return PlanetTranslator.MAP_ROM.get(name, name)

        return name