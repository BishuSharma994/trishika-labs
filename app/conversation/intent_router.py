import re
from difflib import SequenceMatcher


class IntentRouter:

    DOMAIN_MAP = {
        "career": {
            "keywords": {
                "career", "job", "work", "promotion", "business", "office",
                "naukri", "kaam", "interview", "boss", "switch job",
                "carrer", "carrier", "profession",
            },
            "target_houses": [10, 6, 11],
            "target_planets": ["Saturn", "Sun", "Mercury"],
        },
        "finance": {
            "keywords": {
                "finance", "money", "wealth", "salary", "income", "investment",
                "invest", "savings", "spending", "budget", "loan", "debt",
                "paisa", "paise", "dhan", "bachat", "nivesh",
            },
            "target_houses": [2, 11, 5],
            "target_planets": ["Jupiter", "Venus", "Mars"],
        },
        "marriage": {
            "keywords": {
                "marriage", "married", "shaadi", "partner", "relationship",
                "wife", "husband", "spouse", "rishta", "wedding",
                "shadi", "sadhi",
            },
            "target_houses": [7, 2, 11],
            "target_planets": ["Venus", "Jupiter", "Moon"],
        },
        "health": {
            "keywords": {
                "health", "stress", "sleep", "diet", "routine", "hospital",
                "disease", "illness", "sehat", "bimari", "recovery",
                "helth",
            },
            "target_houses": [1, 6, 8],
            "target_planets": ["Moon", "Saturn", "Mars"],
        },
    }

    INTENT_MAP = {
        "aisa bhi hota hai": "validation",
        "aisa v hota hai": "validation",
        "already married": "context_update",
        "kya karna chahiye": "instruction",
        "what should i do": "instruction",
        "what can i do": "instruction",
        "what should i review": "step_detail",
        "how exactly": "clarification",
        "kaise sudhar": "clarification",
        "what kind": "clarification",
        "aisa hota hai": "validation",
        "kiya review karu": "step_detail",
        "kya review karu": "step_detail",
        "kya karu": "instruction",
        "kya karun": "instruction",
        "kiya karu": "instruction",
        "kiya karun": "instruction",
        "review karu": "step_detail",
        "review kya": "step_detail",
        "kis tarah": "mechanism",
        "kis se": "mechanism",
        "kissey": "mechanism",
        "kisse": "mechanism",
        "how long": "timing",
        "what is": "definition",
        "kya hai": "definition",
        "yeh kya": "definition",
        "matlab": "definition",
        "theek hai": "affirmation",
        "thik hai": "affirmation",
        "lekin": "context_update",
        "already": "context_update",
        "ho chuka": "context_update",
        "but": "context_update",
        "sach me": "validation",
        "kiya": "definition",
        "kya": "definition",
        "kaisa": "clarification",
        "kaisey": "instruction",
        "kaise": "instruction",
        "haan": "affirmation",
        "okay": "affirmation",
        "hmm": "affirmation",
        "how": "instruction",
        "han": "affirmation",
        "thik": "affirmation",
        "acha": "affirmation",
        "achha": "affirmation",
        "kab": "timing",
        "aur": "clarification",
        "ji": "affirmation",
        "ok": "affirmation",
        "more": "clarification",
    }

    FUZZY_MATCH_THRESHOLD = 0.84
    FUZZY_MIN_LENGTH = 4
    INTENT_PRIORITY = {
        "context_update": 0,
        "instruction": 1,
        "timing": 1,
        "step_detail": 1,
        "mechanism": 1,
        "clarification": 1,
        "definition": 1,
        "validation": 1,
        "affirmation": 3,
        "general": 9,
    }

    GENERAL_TARGETS = {
        "target_houses": [1, 5, 9],
        "target_planets": ["Moon", "Saturn"],
    }

    PLANET_KEYWORDS = {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
        "rahu": "Rahu",
        "ketu": "Ketu",
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
        matches = []

        for phrase, intent in sorted(
            IntentRouter.INTENT_MAP.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if re.search(rf"\b{re.escape(phrase)}\b", normalized):
                matches.append((phrase, intent))

        if matches:
            phrase, intent = min(
                matches,
                key=lambda item: (
                    IntentRouter.INTENT_PRIORITY.get(item[1], 9),
                    -len(item[0]),
                ),
            )
            return {
                "intent": intent,
                "matched_phrase": phrase,
                "normalized_text": normalized,
            }

        return {
            "intent": "general",
            "matched_phrase": "",
            "normalized_text": normalized,
        }

    @staticmethod
    def _fuzzy_match_token(token, keyword):
        token_value = str(token or "").strip().lower()
        keyword_value = str(keyword or "").strip().lower()
        if len(token_value) < IntentRouter.FUZZY_MIN_LENGTH:
            return False
        if len(keyword_value) < IntentRouter.FUZZY_MIN_LENGTH:
            return False
        if token_value[0] != keyword_value[0]:
            return False
        if abs(len(token_value) - len(keyword_value)) > 2:
            return False
        if len(token_value) >= 5 and len(keyword_value) >= 5 and token_value[:2] != keyword_value[:2]:
            return False
        return SequenceMatcher(None, token_value, keyword_value).ratio() >= IntentRouter.FUZZY_MATCH_THRESHOLD

    @staticmethod
    def detect_domain(text, current_domain=None):
        normalized = IntentRouter._normalize_text(text)
        if not normalized:
            return current_domain

        tokens = normalized.split()
        best_topic = current_domain
        best_score = 0

        for topic, data in IntentRouter.DOMAIN_MAP.items():
            score = 0

            if normalized == topic:
                score += 6
            elif any(IntentRouter._fuzzy_match_token(token, topic) for token in tokens):
                score += 4

            for keyword in data["keywords"]:
                if re.search(rf"\b{re.escape(keyword)}\b", normalized):
                    score += max(2, len(keyword.split()) + 1)
                elif " " not in keyword and any(IntentRouter._fuzzy_match_token(token, keyword) for token in tokens):
                    score += 1

            if score > best_score:
                best_score = score
                best_topic = topic

        return best_topic if best_score > 0 else current_domain

    @staticmethod
    def normalize_topic(text):
        return IntentRouter.detect_domain(text, current_domain=None)

    @staticmethod
    def detect_planet(text, fallback=None):
        normalized = IntentRouter._normalize_text(text)
        for token, planet in IntentRouter.PLANET_KEYWORDS.items():
            if re.search(rf"\b{re.escape(token)}\b", normalized):
                return planet
        return fallback

    @staticmethod
    def get_astrology_targets(intent):
        return IntentRouter.DOMAIN_MAP.get(intent, IntentRouter.GENERAL_TARGETS)
