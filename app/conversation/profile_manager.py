import json


class ProfileManager:

    FREE_MAX_PROFILES = 1
    PREMIUM_MAX_PROFILES = 10

    @staticmethod
    def _is_hi_dev(language, script):
        return language == "hi" and script == "devanagari"

    @staticmethod
    def _is_hi_rom(language, script):
        return language == "hi" and script == "roman"

    @staticmethod
    def parse_profiles(raw_profiles):
        if not raw_profiles:
            return []

        if isinstance(raw_profiles, list):
            source = raw_profiles
        else:
            try:
                source = json.loads(raw_profiles)
            except Exception:
                return []

        profiles = []

        for item in source:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            dob = str(item.get("dob", "")).strip()
            tob = str(item.get("tob", "")).strip()
            place = str(item.get("place", "")).strip()

            if not name:
                continue

            profiles.append({
                "name": name,
                "dob": dob,
                "tob": tob,
                "place": place
            })

        return profiles

    @staticmethod
    def serialize_profiles(profiles):
        return json.dumps(profiles or [])

    @staticmethod
    def is_premium_family(session):
        if bool(getattr(session, "is_premium", False)):
            return True

        plan_tier = str(getattr(session, "plan_tier", "") or "").lower()
        subscription_plan = str(getattr(session, "subscription_plan", "") or "").lower()

        premium_tokens = {
            "premium",
            "premium_family",
            "family",
            "family_plan",
            "pro"
        }

        if plan_tier in premium_tokens:
            return True

        if any(token in subscription_plan for token in ("premium", "family", "pro")):
            return True

        return False

    @staticmethod
    def max_profiles(session):
        if ProfileManager.is_premium_family(session):
            return ProfileManager.PREMIUM_MAX_PROFILES
        return ProfileManager.FREE_MAX_PROFILES

    @staticmethod
    def upsert_profile(profiles, profile, limit):
        profiles = profiles or []
        profile = profile or {}

        name = str(profile.get("name", "")).strip()
        if not name:
            return profiles, False, False

        normalized = name.lower()

        for idx, item in enumerate(profiles):
            existing = str(item.get("name", "")).strip().lower()
            if existing == normalized:
                profiles[idx] = {
                    "name": name,
                    "dob": str(profile.get("dob", "")).strip(),
                    "tob": str(profile.get("tob", "")).strip(),
                    "place": str(profile.get("place", "")).strip()
                }
                return profiles, True, False

        if len(profiles) >= limit:
            return profiles, False, True

        profiles.append({
            "name": name,
            "dob": str(profile.get("dob", "")).strip(),
            "tob": str(profile.get("tob", "")).strip(),
            "place": str(profile.get("place", "")).strip()
        })
        return profiles, True, False

    @staticmethod
    def default_profile_name(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "स्वयं"
        if ProfileManager._is_hi_rom(language, script):
            return "Swayam"
        return "Self"

    @staticmethod
    def declaration_prompt(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "क्या यह आपकी कुंडली है या किसी और फैमिली सदस्य की?"
        if ProfileManager._is_hi_rom(language, script):
            return "Kya yeh aapki kundli hai ya kisi aur family member ki?"
        return "Is this your chart or a family member's chart?"

    @staticmethod
    def profile_name_prompt(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "कृपया परिवार सदस्य का नाम लिखें।"
        if ProfileManager._is_hi_rom(language, script):
            return "Kripya family member ka naam likhein."
        return "Please share the family member's name."

    @staticmethod
    def limit_message(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return (
                "आप फैमिली एस्ट्रोलॉजी प्लान में 10 सदस्यों तक जोड़ सकते हैं। "
                "अपग्रेड करने पर पूरे परिवार की कुंडली विश्लेषण मिल सकती है।"
            )

        if ProfileManager._is_hi_rom(language, script):
            return (
                "Aap family astrology plan mein 10 members tak add kar sakte hain. "
                "Upgrade karne par poore parivaar ki kundli analysis mil sakti hai."
            )

        return (
            "You can add up to 10 members in the family astrology plan. "
            "Upgrading unlocks full family kundli analysis."
        )

    @staticmethod
    def detect_profile_scope(text):
        if not text:
            return None

        t = text.lower().strip()

        self_tokens = [
            "my",
            "mine",
            "self",
            "meri",
            "mera",
            "meri kundli",
            "मेरी",
            "मेरी कुंडली",
            "स्वयं"
        ]
        family_tokens = [
            "family",
            "member",
            "wife",
            "husband",
            "mother",
            "father",
            "son",
            "daughter",
            "bhai",
            "behen",
            "family member",
            "parivaar",
            "परिवार",
            "मां",
            "पिता",
            "पत्नी",
            "पति"
        ]

        if any(token in t for token in family_tokens):
            return "family"

        if any(token in t for token in self_tokens):
            return "self"

        return None
