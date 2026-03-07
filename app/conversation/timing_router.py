class TimingRouter:

    TIMING_KEYWORDS_EN = [
        "when",
        "time",
        "year",
        "period",
        "future",
        "next",
        "soon"
    ]

    TIMING_KEYWORDS_ROMAN = [
        "kab",
        "kaunsa time",
        "kaunsi date",
        "kab tak",
        "kab hoga",
        "kab milega"
    ]

    TIMING_KEYWORDS_DEVANAGARI = [
        "कब",
        "समय",
        "किस वर्ष",
        "कब होगा",
        "कब मिलेगा",
        "भविष्य"
    ]

    @staticmethod
    def is_timing_question(text: str):

        if not text:
            return False

        t = text.lower()

        for word in TimingRouter.TIMING_KEYWORDS_EN:
            if word in t:
                return True

        for word in TimingRouter.TIMING_KEYWORDS_ROMAN:
            if word in t:
                return True

        for word in TimingRouter.TIMING_KEYWORDS_DEVANAGARI:
            if word in text:
                return True

        return False