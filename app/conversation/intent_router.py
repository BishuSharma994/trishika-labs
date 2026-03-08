class IntentRouter:

    DOMAIN_KEYWORDS = {
        "career": [
            "career", "job", "promotion", "work", "profession",
            "office", "boss", "salary", "employment", "switch job",
            "करियर", "कैरियर", "नौकरी"
        ],
        "finance": [
            "money", "finance", "wealth", "income", "business",
            "profit", "loss", "investment", "financial",
            "paisa", "dhan", "arthik", "धन", "पैसा", "आर्थिक"
        ],
        "marriage": [
            "marriage", "marry", "relationship", "love",
            "partner", "wife", "husband", "shaadi", "divorce",
            "vivah", "विवाह", "शादी", "रिश्ता", "संबंध"
        ],
        "health": [
            "health", "disease", "illness", "sick",
            "fitness", "injury", "hospital",
            "sehat", "swasthya", "स्वास्थ्य", "सेहत"
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
