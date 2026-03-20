# Life Translation Engine Data
# Contains the templates and mappings for the deterministic astrology engine.

PLANET_MAP = {
    "Sun": {"en": "Sun", "hi": "Surya"},
    "Moon": {"en": "Moon", "hi": "Chandra"},
    "Mars": {"en": "Mars", "hi": "Mangal"},
    "Mercury": {"en": "Mercury", "hi": "Budh"},
    "Jupiter": {"en": "Jupiter", "hi": "Guru"},
    "Venus": {"en": "Venus", "hi": "Shukra"},
    "Saturn": {"en": "Saturn", "hi": "Shani"},
    "Rahu": {"en": "Rahu", "hi": "Rahu"},
    "Ketu": {"en": "Ketu", "hi": "Ketu"},
}

# Domain Maps for scoring
CAREER_MAP = {"10": "high", "6": "medium", "2": "low"}
FINANCE_MAP = {"2": "high", "11": "medium", "9": "low"}
HEALTH_MAP = {"1": "high", "6": "medium", "8": "low"}
MARRIAGE_MAP = {"7": "high", "5": "medium", "2": "low"}

# Outcome Lines
OUTCOME_LINES = {
    "career": {
        "en": [
            "{planet} is influencing your professional sector strongly.",
            "Your career path is currently under the gaze of {planet}.",
            "{planet} suggests a period of transformation in your work life."
        ],
        "hi": [
            "{planet} aapke career ko prabhavit kar raha hai.",
            "Aapka career abhi {planet} ke prabhav mein hai.",
            "{planet} aapke work life mein badlav la raha hai."
        ]
    },
    "finance": {
        "en": [
            "{planet} is impacting your financial flow.",
            "Your savings and earnings are being tested by {planet}.",
            "{planet} indicates a shift in your financial stability."
        ],
        "hi": [
            "{planet} aapki arthik sthiti par asar dal raha hai.",
            "Aapki savings {planet} ke karan thodi upar-niche ho sakti hai.",
            "{planet} paise ke mamle mein badlav dikha raha hai."
        ]
    },
    "health": {
        "en": [
            "{planet} requires you to pay attention to your vitality.",
            "Your health sector is being activated by {planet}.",
            "{planet} suggests a need for balance in your physical well-being."
        ],
        "hi": [
            "{planet} aapki sehat par dhyan dene ko keh raha hai.",
            "Aapki health par {planet} ka asar dikh raha hai.",
            "{planet} sharirik santulan banaye rakhne ka sanket de raha hai."
        ]
    },
    "marriage": {
        "en": [
            "{planet} is bringing focus to your relationships.",
            "Your marital prospects are being influenced by {planet}.",
            "{planet} suggests a time of reflection in your personal life."
        ],
        "hi": [
            "{planet} aapke rishton par roshni dal raha hai.",
            "Aapki shadi ke yog par {planet} ka prabhav hai.",
            "{planet} niji jeevan mein soch-vichar ka samay dikha raha hai."
        ]
    }
}

# Mechanism Lines
MECHANISM_LINES = {
    "career": {
        "en": [
            "This creates a need for discipline and structured effort.",
            "You might feel a push towards new responsibilities.",
            "Opportunities may come through patience and hard work."
        ],
        "hi": [
            "Isse anushasan aur mehnat ki zarurat badh jati hai.",
            "Aapko nayi zimmedariyan mil sakti hain.",
            "Sabar aur kadi mehnat se mauke milenge."
        ]
    },
    "finance": {
        "en": [
            "This indicates a time to be cautious with investments.",
            "Flow of money might be irregular but promising.",
            "Structuring your expenses will bring relief."
        ],
        "hi": [
            "Yeh nivesh mein savdhani baratne ka samay hai.",
            "Paise ka bahav thoda ruk-ruk kar ho sakta hai.",
            "Kharchon ko sahi dhang se manage karne se labh hoga."
        ]
    },
    "health": {
        "en": [
            "This calls for a better daily routine and diet.",
            "Stress might be a factor, so relaxation is key.",
            "Regular exercise will help mitigate these effects."
        ],
        "hi": [
            "Dincharaya aur khan-pan sudharne ki zarurat hai.",
            "Tanav kam karne ke liye aaram karein.",
            "Rozana vyayam karne se fayda hoga."
        ]
    },
    "marriage": {
        "en": [
            "Open communication is essential right now.",
            "Patience is required to understand your partner.",
            "This is a time to build trust and understanding."
        ],
        "hi": [
            "Khul kar baat karna abhi zaruri hai.",
            "Partner ko samajhne ke liye sabar rakhein.",
            "Yeh vishwas aur samajh badhane ka samay hai."
        ]
    }
}

# Action Library (3 items list for shuffling)
ACTION_LIBRARY = {
    "career": {
        "en": [
            "Create a daily task list.",
            "Upskill in your current domain.",
            "Network with seniors in your field.",
            "Focus on finishing pending tasks.",
            "Avoid office politics."
        ],
        "hi": [
            "Rozana ke kaamon ki list banayein.",
            "Apne field mein nayi skills seekhein.",
            "Seniors se bana kar rakhein.",
            "Adhure kaam pure karne par dhyan dein.",
            "Office ki politics se door rahein."
        ]
    },
    "finance": {
        "en": [
            "Track your daily expenses.",
            "Avoid impulsive buying for 2 weeks.",
            "Start a small recurring deposit.",
            "Review your subscription services.",
            "Plan a monthly budget."
        ],
        "hi": [
            "Rozana ke kharche note karein.",
            "2 hafte tak bekar kharidari na karein.",
            "Choti bachat shuru karein.",
            "Apne subscriptions ko review karein.",
            "Mahine ka budget banayein."
        ]
    },
    "health": {
        "en": [
            "Drink 3 liters of water daily.",
            "Walk for 20 minutes in the morning.",
            "Avoid heavy meals after 8 PM.",
            "Practice 5 minutes of meditation.",
            "Sleep by 11 PM."
        ],
        "hi": [
            "Rozana 3 litre paani piyein.",
            "Subah 20 minute sair karein.",
            "Raat 8 baje ke baad bhari khana na khayein.",
            "5 minute dhyan (meditation) karein.",
            "Raat 11 baje tak so jayein."
        ]
    },
    "marriage": {
        "en": [
            "Spend quality time without phones.",
            "Listen more than you speak.",
            "Plan a small surprise or gift.",
            "Avoid bringing up past arguments.",
            "Express gratitude daily."
        ],
        "hi": [
            "Phone ke bina quality time bitayein.",
            "Bolne se zyada sunne ki koshish karein.",
            "Chota sa surprise plan karein.",
            "Purani baatein na ukhadein.",
            "Rozana shukriya ada karein."
        ]
    }
}