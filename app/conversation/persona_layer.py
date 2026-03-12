class PersonaLayer:

    TOPIC_LABELS = {
        "career": {"en": "career", "hi_rom": "career", "hi_dev": "करियर"},
        "finance": {"en": "finance", "hi_rom": "finance", "hi_dev": "वित्त"},
        "marriage": {"en": "marriage", "hi_rom": "shaadi", "hi_dev": "विवाह"},
        "health": {"en": "health", "hi_rom": "swasthya", "hi_dev": "स्वास्थ्य"},
        "general": {"en": "this area", "hi_rom": "is vishay", "hi_dev": "इस विषय"},
    }

    SUBTOPIC_LABELS = {
        "job_switch": {"en": "job switch", "hi_rom": "naukri badalna", "hi_dev": "नौकरी बदलना"},
        "promotion": {"en": "promotion", "hi_rom": "padonnati", "hi_dev": "पदोन्नति"},
        "business_direction": {"en": "business direction", "hi_rom": "vyavsay disha", "hi_dev": "व्यवसाय दिशा"},
        "savings": {"en": "savings", "hi_rom": "bachat", "hi_dev": "बचत"},
        "investment": {"en": "investment", "hi_rom": "nivesh", "hi_dev": "निवेश"},
        "debt_management": {"en": "debt management", "hi_rom": "karz prabandhan", "hi_dev": "कर्ज प्रबंधन"},
        "single_path": {"en": "new relationship path", "hi_rom": "naye rishtay ki disha", "hi_dev": "नए रिश्ते की दिशा"},
        "relationship_stability": {"en": "relationship stability", "hi_rom": "rishtay ki sthirta", "hi_dev": "रिश्ते की स्थिरता"},
        "married_life": {"en": "married life", "hi_rom": "vivahit jeevan", "hi_dev": "विवाहित जीवन"},
        "stress": {"en": "stress", "hi_rom": "tanav", "hi_dev": "तनाव"},
        "lifestyle_balance": {"en": "lifestyle balance", "hi_rom": "jeevanshaili santulan", "hi_dev": "जीवनशैली संतुलन"},
        "specific_condition": {"en": "specific condition", "hi_rom": "vishesh sthiti", "hi_dev": "विशेष स्थिति"},
        "general": {"en": "current focus", "hi_rom": "vartaman focus", "hi_dev": "वर्तमान फोकस"},
    }

    @staticmethod
    def _is_hi_dev(language, script):
        return language in {"hindi_devanagari", "hi_dev"} or (language == "hi" and script == "devanagari")

    @staticmethod
    def _is_hi_rom(language, script):
        return language in {"hindi_roman", "hi_rom"} or (language == "hi" and script in {"roman", "latin"})

    @staticmethod
    def _localized(language, script, en, hi_rom, hi_dev):
        if PersonaLayer._is_hi_dev(language, script):
            return hi_dev
        if PersonaLayer._is_hi_rom(language, script):
            return hi_rom
        return en

    @staticmethod
    def _topic_label(topic, language, script):
        key = "en"
        if PersonaLayer._is_hi_dev(language, script):
            key = "hi_dev"
        elif PersonaLayer._is_hi_rom(language, script):
            key = "hi_rom"
        return PersonaLayer.TOPIC_LABELS.get(topic, PersonaLayer.TOPIC_LABELS["general"]).get(key, topic)

    @staticmethod
    def _subtopic_label(subtopic, language, script):
        key = "en"
        if PersonaLayer._is_hi_dev(language, script):
            key = "hi_dev"
        elif PersonaLayer._is_hi_rom(language, script):
            key = "hi_rom"
        return PersonaLayer.SUBTOPIC_LABELS.get(subtopic, PersonaLayer.SUBTOPIC_LABELS["general"]).get(key, subtopic)

    @staticmethod
    def _format_actions(actions):
        lines = []
        for idx, action in enumerate(actions or [], start=1):
            lines.append(f"{idx}. {action}")
        return "\n".join(lines)

    @staticmethod
    def format_guidance(guidance, language="english", script="latin"):
        data = guidance or {}
        topic_label = PersonaLayer._topic_label(data.get("topic"), language, script)
        subtopic_label = PersonaLayer._subtopic_label(data.get("subtopic"), language, script)
        level = int(data.get("level", 1))
        planet = str(data.get("planet") or "Moon")
        house = str(data.get("house") or "")
        stability = str(data.get("stability") or "moderate")
        stress_source = str(data.get("stress_source") or "stress cycle")
        support = str(data.get("supporting_influence") or planet)
        routine = str(data.get("routine") or "")
        behavior = str(data.get("behavior") or "")
        timeframe = str(data.get("timeframe") or "21 day cycle")
        focus_areas = data.get("focus_areas") or []
        actions = data.get("actions") or []
        remedy = str(data.get("remedy") or "")

        focus_line = ", ".join(str(item) for item in focus_areas[:4])
        action_block = PersonaLayer._format_actions(actions)

        if level <= 1:
            return PersonaLayer._localized(
                language,
                script,
                (
                    f"{topic_label.title()} ({subtopic_label}) current stability: {stability}.\n"
                    f"Stress source: {stress_source}.\n"
                    f"Supporting influence: {support}.\n\n"
                    f"Routine: {routine}\n"
                    f"Behavior: {behavior}\n"
                    f"Time window: {timeframe}"
                ),
                (
                    f"{topic_label.capitalize()} ({subtopic_label}) ki vartaman sthirta: {stability}.\n"
                    f"Tanav ka mool: {stress_source}.\n"
                    f"Sahayak prabhav: {support}.\n\n"
                    f"Niyamit routine: {routine}\n"
                    f"Vyavaharik sujhav: {behavior}\n"
                    f"Samay avadhi: {timeframe}"
                ),
                (
                    f"{topic_label} ({subtopic_label}) की वर्तमान स्थिरता: {stability}।\n"
                    f"तनाव का स्रोत: {stress_source}।\n"
                    f"सहायक प्रभाव: {support}।\n\n"
                    f"नियमित दिनचर्या: {routine}\n"
                    f"व्यवहारिक सुझाव: {behavior}\n"
                    f"समय अवधि: {timeframe}"
                ),
            )

        if level == 2:
            return PersonaLayer._localized(
                language,
                script,
                (
                    f"{topic_label.title()} ({subtopic_label}) explanation:\n"
                    f"{planet} influence in house {house} is currently {stability}.\n"
                    f"Primary stress source: {stress_source}; supporting influence: {support}.\n"
                    f"Focus areas: {focus_line}.\n\n"
                    f"Routine: {routine}\n"
                    f"Behavior: {behavior}\n"
                    f"Time window: {timeframe}"
                ),
                (
                    f"{topic_label.capitalize()} ({subtopic_label}) ka spasht vivaran:\n"
                    f"{planet} ka prabhav house {house} mein abhi {stability} sthiti dikha raha hai.\n"
                    f"Mukhya tanav srot: {stress_source}; sahayak prabhav: {support}.\n"
                    f"Dhyan ke kshetra: {focus_line}.\n\n"
                    f"Routine: {routine}\n"
                    f"Vyavaharik anushasan: {behavior}\n"
                    f"Samay avadhi: {timeframe}"
                ),
                (
                    f"{topic_label} ({subtopic_label}) का स्पष्ट विवरण:\n"
                    f"{planet} का प्रभाव house {house} में अभी {stability} स्थिति दिखा रहा है।\n"
                    f"मुख्य तनाव स्रोत: {stress_source}; सहायक प्रभाव: {support}।\n"
                    f"ध्यान के क्षेत्र: {focus_line}।\n\n"
                    f"रूटीन: {routine}\n"
                    f"व्यवहारिक अनुशासन: {behavior}\n"
                    f"समय अवधि: {timeframe}"
                ),
            )

        if level == 3:
            return PersonaLayer._localized(
                language,
                script,
                (
                    f"Practical routine for {topic_label} ({subtopic_label}):\n"
                    f"{action_block}\n\n"
                    f"Core routine: {routine}\n"
                    f"Core behavior: {behavior}\n"
                    f"Execution window: {timeframe}"
                ),
                (
                    f"{topic_label.capitalize()} ({subtopic_label}) ke liye practical routine:\n"
                    f"{action_block}\n\n"
                    f"Mukhya routine: {routine}\n"
                    f"Mukhya vyavahar: {behavior}\n"
                    f"Anupalan avadhi: {timeframe}"
                ),
                (
                    f"{topic_label} ({subtopic_label}) के लिए प्रायोगिक दिनचर्या:\n"
                    f"{action_block}\n\n"
                    f"मुख्य रूटीन: {routine}\n"
                    f"मुख्य व्यवहार: {behavior}\n"
                    f"अनुपालन अवधि: {timeframe}"
                ),
            )

        return PersonaLayer._localized(
            language,
            script,
            (
                f"Remedy plan for {topic_label} ({subtopic_label}):\n"
                f"{action_block}\n\n"
                f"Remedy emphasis: {remedy}\n"
                f"Keep this for {timeframe}."
            ),
            (
                f"{topic_label.capitalize()} ({subtopic_label}) ke liye upay yojana:\n"
                f"{action_block}\n\n"
                f"Mukhya upay: {remedy}\n"
                f"Isse {timeframe} tak lagatar chalaiye."
            ),
            (
                f"{topic_label} ({subtopic_label}) के लिए उपाय योजना:\n"
                f"{action_block}\n\n"
                f"मुख्य उपाय: {remedy}\n"
                f"इसे {timeframe} तक निरंतर रखें।"
            ),
        )
