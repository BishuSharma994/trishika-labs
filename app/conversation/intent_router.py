import re

class IntentRouter:
    """
    Classifies user queries and maps them to specific astrological triggers.
    """
    
    INTENT_MAP = {
        "career": {
            "keywords": ["job", "career", "promotion", "business", "work", "switch", "boss"],
            "target_houses": [10, 6, 11],
            "target_planets": ["Sun", "Saturn", "Mercury"]
        },
        "finance": {
            "keywords": ["money", "finance", "wealth", "loan", "debt", "salary", "paisa", "dhan"],
            "target_houses": [2, 11, 12],
            "target_planets": ["Jupiter", "Venus"]
        },
        "marriage": {
            "keywords": ["marriage", "wedding", "wife", "husband", "shaadi", "vivah", "partner", "relationship"],
            "target_houses": [7, 2, 8],
            "target_planets": ["Venus", "Jupiter"]
        },
        "health": {
            "keywords": ["health", "disease", "sick", "hospital", "swasthya", "bimari"],
            "target_houses": [6, 8, 12],
            "target_planets": ["Sun", "Moon"]
        }
    }

    @staticmethod
    def detect_domain(text, current_domain=None):
        text_lower = text.lower()
        
        # 1. Check strict keywords first
        for intent, data in IntentRouter.INTENT_MAP.items():
            for kw in data["keywords"]:
                if re.search(r'\b' + kw + r'\b', text_lower):
                    return intent
                    
        # 2. If no new intent detected, maintain the active session domain
        return current_domain or "general"

    @staticmethod
    def get_astrology_targets(intent):
        """Returns the specific houses and planets needed for this topic."""
        return IntentRouter.INTENT_MAP.get(intent, {
            "target_houses": [1, 5, 9], # General fallback (Trikona)
            "target_planets": ["Moon", "Sun"]
        })