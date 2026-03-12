class AstrologyResponseTemplate:

    TOPIC_LABELS = {
        "career": {"en": "career", "hi_rom": "career", "hi_dev": "करियर"},
        "finance": {"en": "finance", "hi_rom": "finance", "hi_dev": "वित्त"},
        "marriage": {"en": "marriage", "hi_rom": "shaadi", "hi_dev": "विवाह"},
        "health": {"en": "health", "hi_rom": "swasthya", "hi_dev": "स्वास्थ्य"},
    }

    SUBTOPIC_LABELS = {
        "career": {
            "job_switch": {"en": "job switch", "hi_rom": "naukri badalna", "hi_dev": "नौकरी बदलना"},
            "promotion": {"en": "promotion", "hi_rom": "padonnati", "hi_dev": "पदोन्नति"},
            "business_direction": {"en": "business direction", "hi_rom": "vyavsay disha", "hi_dev": "व्यवसाय दिशा"},
        },
        "finance": {
            "savings": {"en": "savings", "hi_rom": "bachat", "hi_dev": "बचत"},
            "investment": {"en": "investment", "hi_rom": "nivesh", "hi_dev": "निवेश"},
            "debt_management": {"en": "debt management", "hi_rom": "karz prabandhan", "hi_dev": "कर्ज प्रबंधन"},
        },
        "marriage": {
            "single_path": {"en": "new relationship path", "hi_rom": "naye rishtay ki disha", "hi_dev": "नए रिश्ते की दिशा"},
            "relationship_stability": {"en": "relationship stability", "hi_rom": "rishtay ki sthirta", "hi_dev": "रिश्ते की स्थिरता"},
            "married_life": {"en": "married life", "hi_rom": "vivahit jeevan", "hi_dev": "विवाहित जीवन"},
        },
        "health": {
            "stress": {"en": "stress", "hi_rom": "tanav", "hi_dev": "तनाव"},
            "lifestyle_balance": {"en": "lifestyle balance", "hi_rom": "jeevanshaili santulan", "hi_dev": "जीवनशैली संतुलन"},
            "specific_condition": {"en": "specific condition", "hi_rom": "vishesh sthiti", "hi_dev": "विशेष स्थिति"},
        },
    }

    SUBTOPIC_OPTIONS = {
        "career": {
            "en": "job switch, promotion, or business direction",
            "hi_rom": "naukri badalna, padonnati, ya vyavsay disha",
            "hi_dev": "नौकरी बदलना, पदोन्नति, या व्यवसाय दिशा",
        },
        "finance": {
            "en": "savings, investment, or debt management",
            "hi_rom": "bachat, nivesh, ya karz prabandhan",
            "hi_dev": "बचत, निवेश, या कर्ज प्रबंधन",
        },
        "marriage": {
            "en": "new relationship, relationship stability, or married life",
            "hi_rom": "naya rishta, rishtay ki sthirta, ya vivahit jeevan",
            "hi_dev": "नया रिश्ता, रिश्ते की स्थिरता, या विवाहित जीवन",
        },
        "health": {
            "en": "stress, lifestyle balance, or specific condition",
            "hi_rom": "tanav, jeevanshaili santulan, ya vishesh sthiti",
            "hi_dev": "तनाव, जीवनशैली संतुलन, या विशेष स्थिति",
        },
    }

    @staticmethod
    def _is_hi_dev(language, script):
        return language in {"hindi_devanagari", "hi_dev"} or (language == "hi" and script == "devanagari")

    @staticmethod
    def _is_hi_rom(language, script):
        return language in {"hindi_roman", "hi_rom"} or (language == "hi" and script in {"roman", "latin"})

    @staticmethod
    def _lang_key(language, script):
        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return "hi_dev"
        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return "hi_rom"
        return "en"

    @staticmethod
    def _localized(language, script, en, hi_rom, hi_dev):
        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return hi_dev
        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return hi_rom
        return en

    @staticmethod
    def topic_label(topic, language, script):
        key = AstrologyResponseTemplate._lang_key(language, script)
        labels = AstrologyResponseTemplate.TOPIC_LABELS.get(topic, {})
        return labels.get(key, topic or "topic")

    @staticmethod
    def subtopic_label(topic, subtopic, language, script):
        key = AstrologyResponseTemplate._lang_key(language, script)
        labels = AstrologyResponseTemplate.SUBTOPIC_LABELS.get(topic, {}).get(subtopic, {})
        if labels:
            return labels.get(key, subtopic or "focus")
        return subtopic or AstrologyResponseTemplate._localized(
            language,
            script,
            "focus",
            "focus",
            "फोकस",
        )

    @staticmethod
    def topic_prompt(language, script):
        return AstrologyResponseTemplate._localized(
            language,
            script,
            "Please choose one topic: career, marriage, finance, or health.",
            "Kripya ek topic chuniye: career, shaadi, finance, ya health.",
            "कृपया एक विषय चुनें: करियर, विवाह, वित्त, या स्वास्थ्य।",
        )

    @staticmethod
    def subtopic_prompt(topic, language, script):
        key = AstrologyResponseTemplate._lang_key(language, script)
        options = AstrologyResponseTemplate.SUBTOPIC_OPTIONS.get(topic, {}).get(
            key,
            AstrologyResponseTemplate.SUBTOPIC_OPTIONS.get(topic, {}).get("en", "your current focus"),
        )
        topic_label = AstrologyResponseTemplate.topic_label(topic, language, script)
        return AstrologyResponseTemplate._localized(
            language,
            script,
            f"In {topic_label}, what is your exact focus: {options}?",
            f"{topic_label} mein aapka spasht kendr kya hai: {options}?",
            f"{topic_label} में आपका सटीक फोकस क्या है: {options}?",
        )

    @staticmethod
    def _momentum_label(momentum, language, script):
        key = str(momentum or "neutral").strip().lower()
        if key == "positive":
            return AstrologyResponseTemplate._localized(language, script, "supportive", "anukul", "अनुकूल")
        if key == "challenging":
            return AstrologyResponseTemplate._localized(language, script, "sensitive", "sankraman-sheel", "संवेदनशील")
        return AstrologyResponseTemplate._localized(language, script, "neutral", "santulit", "संतुलित")

    @staticmethod
    def _followup_line(state, language, script):
        if state == "ANALYSIS":
            return AstrologyResponseTemplate._localized(
                language,
                script,
                "Type: timing, guidance, remedy, or more.",
                "Likhiye: samay, margdarshan, upay, ya aur vivaran.",
                "लिखें: समय, मार्गदर्शन, उपाय, या और विवरण।",
            )
        if state == "TIMING":
            return AstrologyResponseTemplate._localized(
                language,
                script,
                "If needed next: guidance or remedy.",
                "Agar chahen agla charan: margdarshan ya upay.",
                "यदि चाहें अगला चरण: मार्गदर्शन या उपाय।",
            )
        if state == "GUIDANCE":
            return AstrologyResponseTemplate._localized(
                language,
                script,
                "If needed next: remedy or timing.",
                "Agar chahen agla charan: upay ya samay margdarshan.",
                "यदि चाहें अगला चरण: उपाय या समय।",
            )
        return AstrologyResponseTemplate._localized(
            language,
            script,
            "You can ask for another topic anytime.",
            "Aap kabhi bhi doosra topic puch sakte hain.",
            "आप कभी भी दूसरा विषय पूछ सकते हैं।",
        )

    @staticmethod
    def build_state_response(state, topic, subtopic, domain_data, language, script):
        data = domain_data or {}
        components = data.get("components", {}) or {}

        score = int(data.get("score", 50))
        projection = int(data.get("projection_next_year", score))
        driver = str(data.get("primary_driver", "Unknown"))
        risk = str(data.get("risk_factor", "Unknown"))
        momentum_label = AstrologyResponseTemplate._momentum_label(data.get("momentum"), language, script)
        topic_label = AstrologyResponseTemplate.topic_label(topic, language, script)
        subtopic_label = AstrologyResponseTemplate.subtopic_label(topic, subtopic, language, script)

        house_struct = int(components.get("house_structural", 50))
        lord_strength = int(components.get("house_lord_strength", 50))
        ashtakavarga = int(components.get("ashtakavarga", 50))
        dasha = int(components.get("dasha_activation", 50))

        if state == "ANALYSIS":
            message = AstrologyResponseTemplate._localized(
                language,
                script,
                (
                    f"{topic_label.title()} - {subtopic_label}: chart score {score}/100. "
                    f"Primary driver {driver}; pressure point {risk}."
                ),
                (
                    f"{topic_label.capitalize()} - {subtopic_label}: kundli ank {score}/100. "
                    f"Mukhya grah prabhav {driver}; dabav bindu {risk}."
                ),
                (
                    f"{topic_label} - {subtopic_label}: चार्ट स्कोर {score}/100। "
                    f"मुख्य प्रभाव {driver}; दबाव बिंदु {risk}।"
                ),
            )
            return f"{message}\n\n{AstrologyResponseTemplate._followup_line(state, language, script)}"

        if state == "EXPLANATION":
            message = AstrologyResponseTemplate._localized(
                language,
                script,
                (
                    f"{topic_label.title()} - {subtopic_label} breakdown: "
                    f"structure {house_struct}, lord strength {lord_strength}, "
                    f"ashtakavarga {ashtakavarga}, dasha activation {dasha}."
                ),
                (
                    f"{topic_label.capitalize()} - {subtopic_label} ka vishleshan: "
                    f"sanrachna {house_struct}, swami bal {lord_strength}, "
                    f"ashtakavarga {ashtakavarga}, dasha sakriyata {dasha}."
                ),
                (
                    f"{topic_label} - {subtopic_label} का विभाजन: "
                    f"संरचना {house_struct}, स्वामी बल {lord_strength}, "
                    f"अष्टकवर्ग {ashtakavarga}, दशा सक्रियता {dasha}।"
                ),
            )
            return f"{message}\n\n{AstrologyResponseTemplate._followup_line('ANALYSIS', language, script)}"

        if state == "TIMING":
            message = AstrologyResponseTemplate._localized(
                language,
                script,
                (
                    f"{topic_label.title()} - {subtopic_label} timing: momentum flag {momentum_label}, "
                    f"next-year projection {projection}/100."
                ),
                (
                    f"{topic_label.capitalize()} - {subtopic_label} ka samay sanket: gati sthiti {momentum_label}, "
                    f"agle varsh ka anumaan {projection}/100."
                ),
                (
                    f"{topic_label} - {subtopic_label} का समय संकेत: गति स्थिति {momentum_label}, "
                    f"अगले वर्ष का अनुमान {projection}/100।"
                ),
            )
            return f"{message}\n\n{AstrologyResponseTemplate._followup_line(state, language, script)}"

        if state == "GUIDANCE":
            message = AstrologyResponseTemplate._localized(
                language,
                script,
                (
                    f"{topic_label.title()} - {subtopic_label} action plan: "
                    f"(1) one focused step daily, (2) avoid high-risk decisions during {risk}-trigger periods, "
                    "(3) weekly score review."
                ),
                (
                    f"{topic_label.capitalize()} - {subtopic_label} ke liye karya yojana: "
                    f"(1) roz ek kendrit kadam, (2) {risk} ke dauran jald nirnay se bachen, "
                    "(3) saptahik pragati samiksha karein."
                ),
                (
                    f"{topic_label} - {subtopic_label} कार्य योजना: "
                    f"(1) रोज एक केंद्रित कदम, (2) {risk} के दौरान जल्द निर्णय न लें, "
                    "(3) साप्ताहिक प्रगति समीक्षा करें।"
                ),
            )
            return f"{message}\n\n{AstrologyResponseTemplate._followup_line(state, language, script)}"

        message = AstrologyResponseTemplate._localized(
            language,
            script,
            (
                f"{topic_label.title()} - {subtopic_label} remedy track: "
                f"align routine with {driver}, control reactions linked with {risk}, and follow a 21-day consistency cycle."
            ),
            (
                f"{topic_label.capitalize()} - {subtopic_label} upay path: "
                f"{driver} anukool dincharya rakhein, {risk} se judi pratikriya niyantrit karein, "
                "aur 21-din lagatar anushasan apnaayein."
            ),
            (
                f"{topic_label} - {subtopic_label} उपाय पथ: "
                f"{driver} अनुकूल दिनचर्या रखें, {risk} से जुड़ी प्रतिक्रियाएँ नियंत्रित करें, "
                "और 21-दिन का नियमित अनुशासन अपनाएँ।"
            ),
        )
        return f"{message}\n\n{AstrologyResponseTemplate._followup_line('REMEDY', language, script)}"
