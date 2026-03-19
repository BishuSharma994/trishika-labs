import re


class IntentRouter:

    DOMAIN_MAP = {
        "career": {
            "keywords": {
                "career", "job", "work", "promotion", "business", "office",
                "naukri", "kaam", "interview", "boss", "switch job",
            },
            "target_houses": [10, 6, 11],
            "target_planets": ["Saturn", "Sun", "Mercury"],
        },
        "finance": {
            "keywords": {
                "finance", "money", "wealth", "salary", "income", "investment",
                "invest", "savings", "spending", "budget", "loan", "debt",
                "paisa", "dhan", "bachat", "nivesh",
            },
            "target_houses": [2, 11, 5],
            "target_planets": ["Jupiter", "Venus", "Mars"],
        },
        "marriage": {
            "keywords": {
                "marriage", "married", "shaadi", "partner", "relationship",
                "wife", "husband", "spouse", "rishta", "wedding",
            },
            "target_houses": [7, 2, 11],
            "target_planets": ["Venus", "Jupiter", "Moon"],
        },
        "health": {
            "keywords": {
                "health", "stress", "sleep", "diet", "routine", "hospital",
                "disease", "illness", "sehat", "bimari", "recovery",
            },
            "target_houses": [1, 6, 8],
            "target_planets": ["Moon", "Saturn", "Mars"],
        },
    }

    INTENT_MAP = {
        "what should i do": "instruction",
        "how long": "timing",
        "kaisey": "instruction",
        "kaise": "instruction",
        "how": "instruction",
        "aur": "detail",
        "more": "detail",
    }

    EXTRA_INTENT_KEYWORDS = {
        "when": "timing",
        "kab": "timing",
        "timing": "timing",
        "remedy": "remedy",
        "upay": "remedy",
        "detail": "detail",
        "explain": "detail",
    }

    GENERAL_TARGETS = {
        "target_houses": [1, 5, 9],
        "target_planets": ["Moon", "Saturn"],
    }

    @staticmethod
    def _normalize_text(text):
        value = str(text or "").strip().lower()
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def contains_devanagari(text):
        return any("\u0900" <= char <= "\u097f" for char in str(text or ""))

    @staticmethod
    def normalize_intent(text):
        normalized = IntentRouter._normalize_text(text)

        for phrase, intent in sorted(
            IntentRouter.INTENT_MAP.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if re.search(rf"\b{re.escape(phrase)}\b", normalized):
                return {
                    "intent": intent,
                    "normalized_text": normalized,
                }

        for phrase, intent in IntentRouter.EXTRA_INTENT_KEYWORDS.items():
            if re.search(rf"\b{re.escape(phrase)}\b", normalized):
                return {
                    "intent": intent,
                    "normalized_text": normalized,
                }

        return {
            "intent": "general",
            "normalized_text": normalized,
        }

    @staticmethod
    def detect_domain(text, current_domain=None):
        normalized = IntentRouter._normalize_text(text)
        if not normalized:
            return current_domain

        best_topic = current_domain
        best_score = 0

        for topic, data in IntentRouter.DOMAIN_MAP.items():
            score = 0

            if normalized == topic:
                score += 6

            for keyword in data["keywords"]:
                if re.search(rf"\b{re.escape(keyword)}\b", normalized):
                    score += max(2, len(keyword.split()) + 1)

            if score > best_score:
                best_score = score
                best_topic = topic

        return best_topic if best_score > 0 else current_domain

    @staticmethod
    def normalize_topic(text):
        return IntentRouter.detect_domain(text, current_domain=None)

    @staticmethod
    def get_astrology_targets(intent):
        return IntentRouter.DOMAIN_MAP.get(intent, IntentRouter.GENERAL_TARGETS)
