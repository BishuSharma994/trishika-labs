import re


class DomainRouter:

    DOMAIN_KEYWORDS = {
        "career": [
            "career",
            "job",
            "naukri",
            "profession",
            "promotion",
            "work",
        ],
        "marriage": [
            "marriage",
            "shaadi",
            "vivah",
            "wife",
            "husband",
            "spouse",
        ],
        "finance": [
            "finance",
            "money",
            "paisa",
            "income",
            "wealth",
            "investment",
        ],
        "health": [
            "health",
            "sehat",
            "fitness",
            "disease",
            "illness",
        ],
        "relationship": [
            "relationship",
            "love",
            "dating",
            "partner",
        ],
        "family": [
            "family",
            "parents",
            "ghar",
            "home",
        ],
        "education": [
            "education",
            "study",
            "exam",
            "college",
            "learning",
        ],
    }

    @staticmethod
    def detect(text, current_domain=None):

        t = str(text or "").lower()

        best_domain = None
        best_len = 0

        for domain, words in DomainRouter.DOMAIN_KEYWORDS.items():

            for word in words:

                if re.search(rf"\b{re.escape(word)}\b", t):

                    if len(word) > best_len:
                        best_domain = domain
                        best_len = len(word)

        if best_domain:
            return best_domain

        return current_domain