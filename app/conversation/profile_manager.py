import json


class ProfileManager:
    FREE_USER_PROFILES = 1
    PREMIUM_USER_PROFILES = 10

    @staticmethod
    def _is_hi_dev(language, script):
        return (
            language in {"hindi_devanagari", "hi_dev"}
            or (language == "hi" and script == "devanagari")
        )

    @staticmethod
    def _is_hi_rom(language, script):
        return (
            language in {"hindi_roman", "hi_rom"}
            or (language == "hi" and script in {"roman", "latin"})
        )

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
            return "मैं किसकी कुंडली देखूँ - आपकी या परिवार के किसी सदस्य की?"

        if ProfileManager._is_hi_rom(language, script):
            return "Main kiski kundli dekhun - aapki ya parivar ke kisi sadasya ki?"

        return "Whose chart should I read: yours or a family member's?"

    @staticmethod
    def declaration_keyboard(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return [["1 मेरी कुंडली"], ["2 परिवार सदस्य की कुंडली"]]

        if ProfileManager._is_hi_rom(language, script):
            return [["1 Meri Kundli"], ["2 Parivar Sadasya Ki Kundli"]]

        return [["1 My Chart"], ["2 Family Member Chart"]]

    @staticmethod
    def profile_name_prompt(language, script):
        if ProfileManager._is_hi_dev(language, script):
            return "कृपया उस परिवार सदस्य का नाम भेजें।"

        if ProfileManager._is_hi_rom(language, script):
            return "Kripya us parivar sadasya ka naam bhejiye."

        return "Please share the family member's name."

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
            return "आप इस प्रीमियम प्लान में अधिकतम 10 कुंडलियां जोड़ सकते हैं।"

        if ProfileManager._is_hi_rom(language, script):
            return "Aap is premium plan mein maximum 10 kundliyan add kar sakte hain."

        return "You can add up to 10 members in the family astrology plan."

    @staticmethod
    def upgrade_message(session, language, script):
        if ProfileManager.is_premium(session):
            if ProfileManager._is_hi_dev(language, script):
                return (
                    "आपने 10 प्रोफाइल की सीमा पूरी कर ली है। "
                    "10 से अधिक कुंडलियों के लिए Higher Premium Tier में अपग्रेड करें।"
                )
            if ProfileManager._is_hi_rom(language, script):
                return (
                    "Aap 10 profiles ki limit tak pahunch gaye hain. "
                    "10 se zyada kundliyon ke liye Higher Premium Tier mein upgrade karein."
                )
            return (
                "You have reached the 10-profile limit. "
                "Upgrade to a higher premium tier to add more charts."
            )

        if ProfileManager._is_hi_dev(language, script):
            return (
                "फ्री प्लान में केवल 1 प्रोफाइल उपलब्ध है। "
                "10 कुंडलियों तक के लिए Premium Family Plan में अपग्रेड करें।"
            )
        if ProfileManager._is_hi_rom(language, script):
            return (
                "Free plan mein sirf 1 profile available hai. "
                "10 kundliyon tak ke liye Premium Family Plan mein upgrade karein."
            )
        return (
            "Free plan supports only 1 profile. "
            "Upgrade to Premium Family to access up to 10 charts."
        )

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
            "1",
            "1 my chart",
            "1 meri kundli",
            "1 मेरी कुंडली",
            "swayam",
            "khud ki",
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
            "2",
            "2 family member chart",
            "2 family member ki kundli",
            "2 परिवार सदस्य की कुंडली",
            "parivar",
            "parivar sadasya",
        }

        if any(token in t for token in family_tokens):
            return "family"

        if any(token in t for token in self_tokens):
            return "self"

        return None
