class AstrologyResponseTemplate:

    DOMAIN_LABELS = {
        "career": {"en": "career", "hi_dev": "करियर", "hi_rom": "career"},
        "finance": {"en": "finance", "hi_dev": "धन", "hi_rom": "paisa"},
        "marriage": {"en": "marriage", "hi_dev": "विवाह", "hi_rom": "shaadi"},
        "health": {"en": "health", "hi_dev": "स्वास्थ्य", "hi_rom": "health"}
    }

    @staticmethod
    def _is_hi_dev(language, script):
        return language == "hi" and script == "devanagari"

    @staticmethod
    def _is_hi_rom(language, script):
        return language == "hi" and script == "roman"

    @staticmethod
    def _domain_name(domain, language, script):
        labels = AstrologyResponseTemplate.DOMAIN_LABELS.get(domain, {})

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return labels.get("hi_dev", "इस विषय")

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return labels.get("hi_rom", "is vishay")

        return labels.get("en", "this area")

    @staticmethod
    def _headers():
        return {
            "observation": "Observation:",
            "cause": "Planetary Cause:",
            "timing": "Timing Insight:",
            "guidance": "Guidance:",
            "followup": "Follow-up Question:"
        }

    @staticmethod
    def _build_observation(domain, score, language, script):
        domain_name = AstrologyResponseTemplate._domain_name(domain, language, script)

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            tone = "मजबूत" if score >= 65 else "मध्यम" if score >= 50 else "चुनौतीपूर्ण"
            return f"आपकी कुंडली में {domain_name} के योग {tone} दिखाई दे रहे हैं।"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            tone = "strong" if score >= 65 else "moderate" if score >= 50 else "challenging"
            return f"Aapki kundli mein {domain_name} ke yog {tone} dikh rahe hain."

        tone = "strong" if score >= 65 else "moderate" if score >= 50 else "challenging"
        return f"Your chart shows {tone} indications in {domain_name}."

    @staticmethod
    def _build_cause(primary_driver, language, script):
        planet = primary_driver or "Unknown"

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return f"{planet} का प्रभाव इस विषय का मुख्य कारण बन रहा है और परिणामों को प्रभावित कर रहा है।"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return f"{planet} ka prabhav is vishay ka primary cause ban raha hai aur results ko influence kar raha hai."

        return f"{planet} is the primary planetary driver shaping outcomes in this area."

    @staticmethod
    def _build_timing(momentum, language, script):
        m = (momentum or "Neutral").lower()

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            if m == "positive":
                return "आने वाले 2-3 वर्षों में धीरे-धीरे प्रगति और स्थिरता के संकेत मजबूत हैं।"
            if m == "challenging":
                return "अगले 12-18 महीनों में सावधानी के साथ धीरे-धीरे सुधार की संभावना है।"
            return "अगले 1-2 वर्षों में परिणाम क्रमिक रूप से बेहतर हो सकते हैं।"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            if m == "positive":
                return "Agle 2-3 saalon mein dheere dheere progress aur stability ke strong signals hain."
            if m == "challenging":
                return "Agle 12-18 mahino mein caution ke saath gradual sudhar possible hai."
            return "Agle 1-2 saalon mein results dheere dheere better ho sakte hain."

        if m == "positive":
            return "Over the next 2-3 years, momentum supports gradual growth and stronger stability."
        if m == "challenging":
            return "Over the next 12-18 months, improvement is possible with caution and patience."
        return "Over the next 1-2 years, progress is likely to be gradual."

    @staticmethod
    def _build_guidance(ai_guidance, risk_factor, language, script):
        base_guidance = (ai_guidance or "").strip()
        risk = risk_factor or "Unknown"

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            warning = f"चेतावनी: {risk} से जुड़े उतार-चढ़ाव में जल्दबाजी से बचें।"
            return f"{warning} {base_guidance}".strip()

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            warning = f"Warning: {risk} se jude utar-chadhav mein jaldbaazi se bachein."
            return f"{warning} {base_guidance}".strip()

        warning = f"Warning: avoid impulsive decisions around {risk}-linked fluctuations."
        return f"{warning} {base_guidance}".strip()

    @staticmethod
    def _build_followup(domain, language, script):
        if AstrologyResponseTemplate._is_hi_dev(language, script):
            if domain == "career":
                return "क्या आप नौकरी बदलना चाहते हैं या प्रमोशन पर ध्यान दे रहे हैं?"
            if domain == "finance":
                return "क्या आपका फोकस बचत पर है या निवेश पर?"
            if domain == "marriage":
                return "क्या आप नए रिश्ते की तलाश में हैं या मौजूदा संबंध पर स्पष्टता चाहते हैं?"
            return "क्या आपका सवाल लाइफस्टाइल, तनाव या किसी विशेष स्वास्थ्य चिंता से जुड़ा है?"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            if domain == "career":
                return "Kya aap job switch chahte hain ya promotion par focus kar rahe hain?"
            if domain == "finance":
                return "Kya aapka focus savings par hai ya investment par?"
            if domain == "marriage":
                return "Kya aap naya rishta dekh rahe hain ya existing relationship par clarity chahte hain?"
            return "Kya aapka sawal lifestyle, stress ya kisi specific health concern se juda hai?"

        if domain == "career":
            return "Are you focused on a job switch, or growth in your current role?"
        if domain == "finance":
            return "Are you prioritizing savings, debt reduction, or investments right now?"
        if domain == "marriage":
            return "Are you seeking a new relationship, or clarity in an existing one?"
        return "Is your concern mainly lifestyle balance, stress, or a specific health pattern?"

    @staticmethod
    def build_response(domain, domain_data, ai_guidance, language, script):
        domain_data = domain_data or {}

        score = domain_data.get("score", 50)
        primary_driver = domain_data.get("primary_driver", "Unknown")
        risk_factor = domain_data.get("risk_factor", "Unknown")
        momentum = domain_data.get("momentum", "Neutral")

        headers = AstrologyResponseTemplate._headers()

        observation = AstrologyResponseTemplate._build_observation(domain, score, language, script)
        cause = AstrologyResponseTemplate._build_cause(primary_driver, language, script)
        timing = AstrologyResponseTemplate._build_timing(momentum, language, script)
        guidance = AstrologyResponseTemplate._build_guidance(ai_guidance, risk_factor, language, script)
        followup = AstrologyResponseTemplate._build_followup(domain, language, script)

        return (
            f"{headers['observation']}\n{observation}\n\n"
            f"{headers['cause']}\n{cause}\n\n"
            f"{headers['timing']}\n{timing}\n\n"
            f"{headers['guidance']}\n{guidance}\n\n"
            f"{headers['followup']}\n{followup}"
        )
