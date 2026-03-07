class IntentRouter:

    DOMAIN_KEYWORDS = {
        "career": [
            "career", "job", "promotion", "work", "profession",
            "office", "boss", "salary", "employment", "switch job"
        ],
        "finance": [
            "money", "finance", "wealth", "income", "business",
            "profit", "loss", "investment", "financial"
        ],
        "marriage": [
            "marriage", "marry", "relationship", "love",
            "partner", "wife", "husband", "shaadi", "divorce"
        ],
        "health": [
            "health", "disease", "illness", "sick",
            "fitness", "injury", "hospital"
        ]
    }

    @staticmethod
    def detect_domain(text: str):

        if not text:
            return None

        t = text.lower()

        for domain, keywords in IntentRouter.DOMAIN_KEYWORDS.items():

            for word in keywords:

                if word in t:
                    return domain

        return None