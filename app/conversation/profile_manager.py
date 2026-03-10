import json


class ProfileManager:
    FREE_USER_PROFILES = 1
    PREMIUM_USER_PROFILES = 10

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

        cleaned = []

        for item in source:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            dob = str(item.get("dob", "")).strip()
            tob = str(item.get("tob", "")).strip()
            place = str(item.get("place", "")).strip()

            if not name:
                continue

            cleaned.append(
                {
                    "name": name,
                    "dob": dob,
                    "tob": tob,
                    "place": place,
                }
            )

        return cleaned

    @staticmethod
    def serialize_profiles(profiles):
        return json.dumps(profiles or [])

    @staticmethod
    def is_premium(session):
        plan_tier = str(getattr(session, "plan_tier", "") or "").strip().lower()
        return plan_tier in {"premium", "premium_family", "family", "pro"}

    @staticmethod
    def max_profiles(session):
        if ProfileManager.is_premium(session):
            return ProfileManager.PREMIUM_USER_PROFILES
        return ProfileManager.FREE_USER_PROFILES

    @staticmethod
    def upsert_profile(profiles, profile, max_allowed):
        profiles = list(profiles or [])
        profile = profile or {}

        name = str(profile.get("name", "")).strip()
        if not name:
            return profiles, False, False

        normalized_name = name.lower()

        for idx, existing in enumerate(profiles):
            if str(existing.get("name", "")).strip().lower() == normalized_name:
                profiles[idx] = {
                    "name": name,
                    "dob": str(profile.get("dob", "")).strip(),
                    "tob": str(profile.get("tob", "")).strip(),
                    "place": str(profile.get("place", "")).strip(),
                }
                return profiles, True, False

        if len(profiles) >= max_allowed:
            return profiles, False, True

        profiles.append(
            {
                "name": name,
                "dob": str(profile.get("dob", "")).strip(),
                "tob": str(profile.get("tob", "")).strip(),
                "place": str(profile.get("place", "")).strip(),
            }
        )

        return profiles, True, False

    @staticmethod
    def declaration_prompt(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "क्या यह आपकी कुंडली है या किसी family member की?"

        if ProfileManager._is_hi_rom(language, script):
            return "Kya yeh aapki kundli hai ya kisi family member ki?"

        return "Is this your chart or a family member chart?"

    @staticmethod
    def profile_name_prompt(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "किस family member के लिए पढ़ना है? कृपया नाम लिखें।"

        if ProfileManager._is_hi_rom(language, script):
            return "Kis family member ke liye reading chahiye? Kripya naam likhein."

        return "Which family member is this for? Please share their name."

    @staticmethod
    def default_profile_name(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "स्वयं"

        if ProfileManager._is_hi_rom(language, script):
            return "Swayam"

        return "Self"

    @staticmethod
    def limit_message(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "Aap family astrology plan mein 10 members tak add kar sakte hain."

        if ProfileManager._is_hi_rom(language, script):
            return "Aap family astrology plan mein 10 members tak add kar sakte hain."

        return "You can add up to 10 members in the family astrology plan."

    @staticmethod
    def detect_profile_scope(text):
        if not text:
            return None

        t = text.strip().lower()

        self_tokens = {
            "my",
            "mine",
            "self",
            "meri",
            "mera",
            "मेरी",
            "मेरी कुंडली",
            "self chart",
        }

        family_tokens = {
            "family",
            "member",
            "mother",
            "father",
            "wife",
            "husband",
            "brother",
            "sister",
            "daughter",
            "son",
            "family member",
            "परिवार",
            "मां",
            "पिता",
            "पत्नी",
            "पति",
            "bhai",
            "behen",
        }

        if any(token in t for token in family_tokens):
            return "family"

        if any(token in t for token in self_tokens):
            return "self"

        return None
