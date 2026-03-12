import re


class DomainRouter:

    DOMAIN_KEYWORDS = {
        "career": [
            "career",
            "job",
            "naukri",
            "rojgar",
            "profession",
            "promotion",
            "business",
            "startup",
            "interview",
            "company",
            "salary",
            "work",
        ],
        "marriage": [
            "marriage",
            "shaadi",
            "vivah",
            "wife",
            "husband",
            "spouse",
            "rishta",
            "relationship",
            "partner",
            "pyaar",
            "love",
            "jhagda",
            "jagda",
            "jhagra",
            "jaghara",
            "ladai",
            "fight",
            "conflict",
            "divorce",
            "separation",
            "pati",
            "patni",
        ],
        "finance": [
            "finance",
            "money",
            "paisa",
            "vitt",
            "arthik",
            "income",
            "wealth",
            "investment",
            "loan",
            "emi",
            "debt",
            "bachat",
            "savings",
        ],
        "health": [
            "health",
            "sehat",
            "swasthya",
            "fitness",
            "disease",
            "illness",
            "stress",
            "anxiety",
            "sleep",
            "diet",
            "bimari",
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

    CORE_DOMAIN_MAP = {
        "relationship": "marriage",
        "family": "marriage",
        "education": "career",
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
            return DomainRouter.CORE_DOMAIN_MAP.get(best_domain, best_domain)

        return DomainRouter.CORE_DOMAIN_MAP.get(current_domain, current_domain)
