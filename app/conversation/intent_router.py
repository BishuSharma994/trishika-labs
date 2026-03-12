import re
from difflib import SequenceMatcher


class IntentRouter:

    DOMAIN_KEYWORDS = {
        "career": [
            "career", "job", "promotion", "work", "profession",
            "office", "boss", "salary", "employment", "switch job",
            "business direction", "biz direction",
            "करियर", "कैरियर", "नौकरी",
        ],
        "finance": [
            "money", "finance", "wealth", "income", "business",
            "profit", "loss", "investment", "financial",
            "debt", "loan", "emi", "karz", "karja", "कर्ज",
            "paisa", "dhan", "arthik", "धन", "पैसा", "आर्थिक",
        ],
        "marriage": [
            "marriage", "marry", "relationship", "love",
            "partner", "wife", "husband", "shaadi", "divorce",
            "vivah", "rishta", "spouse",
            "विवाह", "शादी", "रिश्ता", "संबंध",
        ],
        "health": [
            "health", "disease", "illness", "sick",
            "fitness", "injury", "hospital", "stress", "anxiety",
            "sehat", "swasthya", "स्वास्थ्य", "सेहत",
        ],
    }

    TOPIC_SHORTCUTS = {
        "1": "career",
        "2": "marriage",
        "3": "finance",
        "4": "health",
    }

    INTENT_NORMALIZATION = {
        "timing": [
            "how long", "how long time", "kitna time", "kitne din", "kab",
            "when", "timing", "timeline", "time frame", "future", "samay",
            "कब", "समय",
        ],
        "explanation": [
            "tell me about", "explain", "why", "reason", "details",
            "kya matlab", "kaisa", "samjhao", "समझाओ",
        ],
        "guidance": [
            "how do i", "what should i do", "what to do", "guide me",
            "kya karu", "kya karun", "kaise bachun", "kaise bache",
            "करना चाहिए", "क्या करूँ",
        ],
        "detail": [
            "more", "aur", "aage", "continue", "go deeper", "deep",
            "zyada", "or batao", "और", "विस्तार",
        ],
        "context": [
            "where", "which area", "kis topic", "kis baare", "topic",
            "किस विषय", "कहां",
        ],
        "remedy": [
            "remedy", "remeady", "remady", "upay", "upaay", "upaye",
            "upai", "totka", "उपाय",
        ],
        "affirm": [
            "yes", "haan", "han", "ha", "ok", "okay", "sure", "ji",
            "please give", "de do", "de dijiye", "हाँ", "जी",
        ],
        "language_switch": [
            "in english", "english", "in hindi", "hindi roman", "hindi",
            "switch language", "change language",
        ],
    }

    FUZZY_INTENTS = ("timing", "guidance", "detail", "remedy", "affirm")
    FUZZY_MIN_SCORE = 0.82
    FUZZY_DOMAIN_MIN_SCORE = 0.86

    @staticmethod
    def _normalize_text(text):
        value = str(text or "").strip().lower()
        value = re.sub(r"[^a-z0-9\u0900-\u097f\s]", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _tokenize(text):
        normalized = IntentRouter._normalize_text(text)
        if not normalized:
            return []
        return normalized.split()

    @staticmethod
    def _best_fuzzy_match(tokens, keywords):
        best_score = 0.0
        for token in tokens:
            if len(token) < 3:
                continue
            for keyword in keywords:
                if len(keyword) < 3:
                    continue
                score = SequenceMatcher(None, token, keyword).ratio()
                if score > best_score:
                    best_score = score
        return best_score

    @staticmethod
    def detect_domain(text: str, current_domain=None):
        if not text:
            return current_domain

        normalized = IntentRouter._normalize_text(text)
        if normalized in IntentRouter.TOPIC_SHORTCUTS:
            return IntentRouter.TOPIC_SHORTCUTS[normalized]

        best_domain = current_domain
        best_len = 0
        for domain, keywords in IntentRouter.DOMAIN_KEYWORDS.items():
            for word in keywords:
                pattern = rf"\b{re.escape(word.lower())}\b"
                if re.search(pattern, normalized):
                    if len(word) > best_len:
                        best_len = len(word)
                        best_domain = domain

        if best_domain:
            return best_domain

        tokens = IntentRouter._tokenize(normalized)
        fuzzy_best_domain = None
        fuzzy_best_score = 0.0
        for domain, keywords in IntentRouter.DOMAIN_KEYWORDS.items():
            score = IntentRouter._best_fuzzy_match(tokens, keywords)
            if score > fuzzy_best_score:
                fuzzy_best_score = score
                fuzzy_best_domain = domain

        if fuzzy_best_domain and fuzzy_best_score >= IntentRouter.FUZZY_DOMAIN_MIN_SCORE:
            return fuzzy_best_domain

        return best_domain

    @staticmethod
    def normalize_intent(text: str):
        normalized = IntentRouter._normalize_text(text)
        if not normalized:
            return {"intent": None, "confidence": 0.0, "matched": None}

        for intent, phrases in IntentRouter.INTENT_NORMALIZATION.items():
            for phrase in phrases:
                if phrase in normalized:
                    return {"intent": intent, "confidence": 0.99, "matched": phrase}

        tokens = IntentRouter._tokenize(normalized)
        best_intent = None
        best_score = 0.0
        for intent in IntentRouter.FUZZY_INTENTS:
            score = IntentRouter._best_fuzzy_match(tokens, IntentRouter.INTENT_NORMALIZATION[intent])
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent and best_score >= IntentRouter.FUZZY_MIN_SCORE:
            return {"intent": best_intent, "confidence": best_score, "matched": "fuzzy"}

        return {"intent": None, "confidence": 0.0, "matched": None}
