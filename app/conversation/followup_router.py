class FollowupRouter:

    FOLLOWUP_WORDS = [
        "when",
        "why",
        "how",
        "kab",
        "kyun",
        "kaise",
        "कब",
        "क्यों",
        "कैसे"
    ]

    @staticmethod
    def is_followup(text):

        if not text:
            return False

        t = text.lower()

        for w in FollowupRouter.FOLLOWUP_WORDS:

            if w in t:
                return True

        return False