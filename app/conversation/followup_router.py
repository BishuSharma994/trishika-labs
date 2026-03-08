from app.conversation.prompt_builder import AstrologerPrompts


class FollowupRouter:

    INITIAL_FOLLOWUP = {
        "career": {
            "en": "Are you focused on a job switch, promotion, or business direction?",
            "devanagari": "क्या आपका फोकस नौकरी बदलने, प्रमोशन, या बिज़नेस दिशा पर है?",
            "roman": "Kya aapka focus job switch, promotion, ya business direction par hai?"
        },
        "finance": {
            "en": "Are you focusing on savings, investments, or debt management?",
            "devanagari": "क्या आपका फोकस बचत, निवेश, या कर्ज प्रबंधन पर है?",
            "roman": "Kya aapka focus savings, investment, ya karz management par hai?"
        },
        "marriage": {
            "en": "Are you seeking a new relationship or clarity in an existing one?",
            "devanagari": "क्या आप नए रिश्ते की तलाश में हैं या मौजूदा संबंध में स्पष्टता चाहते हैं?",
            "roman": "Kya aap naya rishta dekh rahe hain ya existing relationship mein clarity chahte hain?"
        },
        "health": {
            "en": "Is your concern mainly stress, lifestyle balance, or a specific health issue?",
            "devanagari": "क्या आपकी चिंता मुख्यतः तनाव, लाइफस्टाइल संतुलन, या किसी विशेष स्वास्थ्य समस्या से जुड़ी है?",
            "roman": "Kya aapki concern mainly stress, lifestyle balance, ya kisi specific health issue se judi hai?"
        }
    }

    OPTION_KEYWORDS = {
        "career": {
            "job_switch": ["switch", "change job", "new job", "job switch", "naukri", "job", "बदल", "नई नौकरी"],
            "promotion": ["promotion", "growth", "raise", "salary", "increment", "प्रमोशन", "वृद्धि"],
            "business": ["business", "startup", "entrepreneur", "vyapar", "व्यापार"]
        },
        "finance": {
            "savings": ["saving", "savings", "save", "bachat", "बचत"],
            "investment": ["investment", "invest", "sip", "stocks", "mutual", "nivesh", "निवेश"],
            "debt": ["debt", "loan", "emi", "karz", "कर्ज", "ऋण"]
        },
        "marriage": {
            "new_relationship": ["new", "single", "find partner", "naya", "नया", "रिश्ता"],
            "existing_relationship": ["existing", "current", "partner", "married", "pati", "patni", "मौजूदा", "संबंध"],
            "timing": ["when", "kab", "timing", "date", "कब", "समय"]
        },
        "health": {
            "stress": ["stress", "anxiety", "mental", "तनाव", "चिंता"],
            "lifestyle": ["lifestyle", "routine", "sleep", "diet", "vyayam", "जीवनशैली", "रूटीन"],
            "medical": ["disease", "illness", "medical", "diagnosis", "hospital", "बीमारी", "स्वास्थ्य समस्या"]
        }
    }

    NEXT_FOLLOWUP = {
        "career": {
            "job_switch": {
                "en": "Do you want timing guidance for the best switch window?",
                "devanagari": "क्या आप नौकरी बदलने के सही समय की स्पष्ट टाइमिंग मार्गदर्शना चाहते हैं?",
                "roman": "Kya aap job switch ke best window ki timing guidance chahte hain?"
            },
            "promotion": {
                "en": "Do you want a 90-day strategy for promotion preparation?",
                "devanagari": "क्या आप प्रमोशन की तैयारी के लिए 90-दिन की रणनीति चाहते हैं?",
                "roman": "Kya aap promotion preparation ke liye 90-din ki strategy chahte hain?"
            },
            "business": {
                "en": "Do you want risk-vs-growth guidance before expanding business decisions?",
                "devanagari": "क्या आप व्यवसाय विस्तार से पहले जोखिम बनाम वृद्धि पर मार्गदर्शन चाहते हैं?",
                "roman": "Kya aap business expansion se pehle risk-vs-growth guidance chahte hain?"
            },
            "general": {
                "en": "Would you like a focused monthly action plan for your career direction?",
                "devanagari": "क्या आप अपने करियर दिशा के लिए मासिक कार्ययोजना चाहते हैं?",
                "roman": "Kya aap apni career direction ke liye monthly action plan chahte hain?"
            }
        },
        "finance": {
            "savings": {
                "en": "Do you want a monthly savings discipline plan tailored to your chart momentum?",
                "devanagari": "क्या आप अपनी कुंडली की गति के अनुसार मासिक बचत योजना चाहते हैं?",
                "roman": "Kya aap chart momentum ke hisaab se monthly savings plan chahte hain?"
            },
            "investment": {
                "en": "Do you want phased investment timing guidance instead of one-time exposure?",
                "devanagari": "क्या आप एकमुश्त निवेश के बजाय चरणबद्ध निवेश टाइमिंग मार्गदर्शन चाहते हैं?",
                "roman": "Kya aap one-time exposure ke bajay phased investment timing guidance chahte hain?"
            },
            "debt": {
                "en": "Do you want a debt-clearance priority sequence for the next 6 months?",
                "devanagari": "क्या आप अगले 6 महीनों के लिए कर्ज चुकाने की प्राथमिकता क्रम चाहते हैं?",
                "roman": "Kya aap agle 6 mahino ke liye debt-clearance priority sequence chahte hain?"
            },
            "general": {
                "en": "Would you like a cautious 30-day finance action plan?",
                "devanagari": "क्या आप सावधानी-आधारित 30-दिन की वित्तीय कार्ययोजना चाहते हैं?",
                "roman": "Kya aap cautious 30-din ki finance action plan chahte hain?"
            }
        },
        "marriage": {
            "new_relationship": {
                "en": "Do you want guidance on how to filter serious prospects more clearly?",
                "devanagari": "क्या आप गंभीर संभावनाओं को बेहतर पहचानने के लिए मार्गदर्शन चाहते हैं?",
                "roman": "Kya aap serious prospects ko better filter karne ka guidance chahte hain?"
            },
            "existing_relationship": {
                "en": "Do you want a practical communication plan for emotional stability in this bond?",
                "devanagari": "क्या आप इस संबंध में भावनात्मक स्थिरता के लिए व्यावहारिक संवाद योजना चाहते हैं?",
                "roman": "Kya aap is bond me emotional stability ke liye practical communication plan chahte hain?"
            },
            "timing": {
                "en": "Do you want a clearer timing window with preparation advice?",
                "devanagari": "क्या आप तैयारी सलाह के साथ स्पष्ट समय-विंडो चाहते हैं?",
                "roman": "Kya aap preparation advice ke saath clearer timing window chahte hain?"
            },
            "general": {
                "en": "Would you like a short relationship-priority action plan for the next month?",
                "devanagari": "क्या आप अगले महीने के लिए संबंध-प्राथमिकता कार्ययोजना चाहते हैं?",
                "roman": "Kya aap agle mahine ke liye relationship-priority action plan chahte hain?"
            }
        },
        "health": {
            "stress": {
                "en": "Do you want a stress-reduction routine aligned with your current momentum?",
                "devanagari": "क्या आप वर्तमान गति के अनुरूप तनाव कम करने की दिनचर्या चाहते हैं?",
                "roman": "Kya aap current momentum ke anuroop stress-reduction routine chahte hain?"
            },
            "lifestyle": {
                "en": "Do you want a practical sleep-diet-routine reset plan for 30 days?",
                "devanagari": "क्या आप 30 दिनों के लिए नींद-आहार-रूटीन सुधार योजना चाहते हैं?",
                "roman": "Kya aap 30 din ke liye sleep-diet-routine reset plan chahte hain?"
            },
            "medical": {
                "en": "Do you want caution-first guidance on what to monitor medically?",
                "devanagari": "क्या आप चिकित्सा दृष्टि से किन संकेतों पर ध्यान रखें, इस पर सावधानी मार्गदर्शन चाहते हैं?",
                "roman": "Kya aap medically kin signals ko monitor karein, is par caution-first guidance chahte hain?"
            },
            "general": {
                "en": "Would you like a balanced weekly health-action checklist?",
                "devanagari": "क्या आप संतुलित साप्ताहिक स्वास्थ्य-कार्य चेकलिस्ट चाहते हैं?",
                "roman": "Kya aap balanced weekly health-action checklist chahte hain?"
            }
        }
    }

    @staticmethod
    def _lang_key(language, script):
        if language == "hi" and script == "devanagari":
            return "devanagari"
        if language == "hi" and script == "roman":
            return "roman"
        return "en"

    @staticmethod
    def get_initial_followup_question(domain, language, script):
        domain_map = FollowupRouter.INITIAL_FOLLOWUP.get(domain, {})
        return domain_map.get(
            FollowupRouter._lang_key(language, script),
            "Would you like to go deeper into this area?"
        )

    @staticmethod
    def detect_followup_answer(domain, text):
        if not domain or not text:
            return "general"

        t = text.lower()
        options = FollowupRouter.OPTION_KEYWORDS.get(domain, {})

        for focus, keywords in options.items():
            for token in keywords:
                if token.lower() in t:
                    return focus

        return "general"

    @staticmethod
    def get_next_followup_question(domain, focus, language, script, previous_question=None):
        domain_map = FollowupRouter.NEXT_FOLLOWUP.get(domain, {})
        question_map = domain_map.get(focus) or domain_map.get("general")

        if not question_map:
            return ""

        question = question_map.get(
            FollowupRouter._lang_key(language, script),
            ""
        )

        if previous_question and question.strip() == previous_question.strip():
            fallback_map = domain_map.get("general", {})
            fallback = fallback_map.get(
                FollowupRouter._lang_key(language, script),
                ""
            )

            if fallback and fallback.strip() != previous_question.strip():
                return fallback

            if language == "hi" and script == "devanagari":
                return "क्या आप इस विषय के लिए अगले 30 दिनों की व्यावहारिक योजना चाहते हैं?"

            if language == "hi" and script == "roman":
                return "Kya aap is vishay ke liye agle 30 din ki practical yojana chahte hain?"

            return "Would you like a practical 30-day action plan for this area?"

        return question

    @staticmethod
    def build_deeper_prompt(domain, domain_data, language, script, user_id, user_text, focus):
        base_prompt = AstrologerPrompts.build_domain_prompt(
            domain=domain,
            domain_data=domain_data,
            language=language,
            script=script,
            user_id=user_id,
            question=user_text
        )

        return (
            f"{base_prompt}\n\n"
            f"Current follow-up focus: {focus}\n"
            f"User follow-up answer: {user_text}\n\n"
            "Return ONLY a valid JSON object with these keys:\n"
            "observation, cause, timing, guidance, followup\n\n"
            "Rules:\n"
            "- Each value must be a plain string.\n"
            "- Keep each field concise (1-2 sentences).\n"
            "- Do not output markdown, bullets, headings, or extra text outside JSON.\n"
        )
