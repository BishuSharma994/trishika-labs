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
    def translate(text, language, script):

        if not text:
            return text

        if language not in {"hi", "hindi_roman", "hindi_devanagari"}:
            return text

        mapping = PlanetTranslator.MAP_DEV if script == "devanagari" else PlanetTranslator.MAP_ROM

        for eng, local in mapping.items():
            text = text.replace(eng, local)

        return text
