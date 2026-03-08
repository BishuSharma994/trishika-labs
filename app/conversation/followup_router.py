from app.conversation.prompt_builder import AstrologerPrompts


class FollowupRouter:

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
            "new_relationship": ["single", "new", "naya", "नया", "new relation"],
            "existing_relationship": ["already married", "married", "shaadi ho chuki", "rishta", "मौजूदा", "शादी हो चुकी", "विवाहित", "पति", "पत्नी"],
            "timing": ["when", "kab", "timing", "date", "कब", "समय"]
        },
        "health": {
            "stress": ["stress", "anxiety", "mental", "तनाव", "चिंता"],
            "lifestyle": ["lifestyle", "routine", "sleep", "diet", "जीवनशैली", "रूटीन"],
            "medical": ["disease", "illness", "medical", "diagnosis", "hospital", "बीमारी", "स्वास्थ्य समस्या"]
        }
    }

    INITIAL_QUESTIONS = {
        "career": {
            "en": "Are you currently focused on job switch, promotion, or business direction?",
            "devanagari": "क्या आपका फोकस नौकरी बदलने, प्रमोशन, या बिज़नेस दिशा पर है?",
            "roman": "Kya aapka focus job switch, promotion, ya business direction par hai?"
        },
        "finance": {
            "en": "Are you focusing more on savings, investments, or debt management right now?",
            "devanagari": "क्या आपका फोकस इस समय बचत, निवेश, या कर्ज प्रबंधन पर है?",
            "roman": "Kya aapka focus abhi savings, investment, ya debt management par hai?"
        },
        "marriage": {
            "en": "Are you seeking clarity in an existing marriage, or guidance for relationship growth?",
            "devanagari": "क्या आप मौजूदा विवाह में स्पष्टता चाहते हैं या संबंध की वृद्धि पर मार्गदर्शन चाहते हैं?",
            "roman": "Kya aap existing shaadi mein clarity chahte hain ya relationship growth par guidance chahte hain?"
        },
        "health": {
            "en": "Is your concern more about stress, lifestyle balance, or a specific health issue?",
            "devanagari": "क्या आपकी चिंता तनाव, लाइफस्टाइल संतुलन, या किसी विशेष स्वास्थ्य समस्या से जुड़ी है?",
            "roman": "Kya aapki concern stress, lifestyle balance, ya kisi specific health issue se judi hai?"
        }
    }

    NEXT_QUESTIONS = {
        "career": {
            "job_switch": {
                "en": "Do you want timing guidance for the best switch window?",
                "devanagari": "क्या आप नौकरी बदलने के सही समय की मार्गदर्शना चाहते हैं?",
                "roman": "Kya aap job switch ke sahi time ki guidance chahte hain?"
            },
            "promotion": {
                "en": "Do you want a practical 90-day promotion preparation path?",
                "devanagari": "क्या आप प्रमोशन के लिए 90-दिन की व्यावहारिक तैयारी चाहते हैं?",
                "roman": "Kya aap promotion ke liye 90-din ki practical tayari chahte hain?"
            },
            "business": {
                "en": "Do you want a caution-first expansion approach for business decisions?",
                "devanagari": "क्या आप व्यवसाय निर्णयों के लिए सावधानी-आधारित विस्तार दृष्टिकोण चाहते हैं?",
                "roman": "Kya aap business decisions ke liye caution-first expansion approach chahte hain?"
            },
            "general": {
                "en": "Would you like a focused monthly action plan for this area?",
                "devanagari": "क्या आप इस विषय के लिए मासिक कार्ययोजना चाहते हैं?",
                "roman": "Kya aap is vishay ke liye monthly action plan chahte hain?"
            }
        },
        "finance": {
            "savings": {
                "en": "Do you want a practical monthly savings discipline plan?",
                "devanagari": "क्या आप व्यावहारिक मासिक बचत अनुशासन योजना चाहते हैं?",
                "roman": "Kya aap practical monthly savings discipline plan chahte hain?"
            },
            "investment": {
                "en": "Do you want phased investment guidance instead of one-time exposure?",
                "devanagari": "क्या आप एकमुश्त के बजाय चरणबद्ध निवेश मार्गदर्शन चाहते हैं?",
                "roman": "Kya aap one-time ke bajay phased investment guidance chahte hain?"
            },
            "debt": {
                "en": "Do you want a debt-clearance sequence for the next few months?",
                "devanagari": "क्या आप अगले कुछ महीनों के लिए कर्ज-चुकौती क्रम चाहते हैं?",
                "roman": "Kya aap agle kuch mahino ke liye debt-clearance sequence chahte hain?"
            },
            "general": {
                "en": "Would you like a cautious 30-day money action plan?",
                "devanagari": "क्या आप सावधानी-आधारित 30-दिन की वित्तीय योजना चाहते हैं?",
                "roman": "Kya aap cautious 30-din ki financial plan chahte hain?"
            }
        },
        "marriage": {
            "new_relationship": {
                "en": "Do you want guidance on how to identify emotionally stable prospects?",
                "devanagari": "क्या आप भावनात्मक रूप से स्थिर संभावनाओं की पहचान पर मार्गदर्शन चाहते हैं?",
                "roman": "Kya aap emotionally stable prospects identify karne ka guidance chahte hain?"
            },
            "existing_relationship": {
                "en": "Do you want a practical communication plan for harmony in your marriage?",
                "devanagari": "क्या आप अपने विवाह में सामंजस्य के लिए व्यावहारिक संवाद योजना चाहते हैं?",
                "roman": "Kya aap apni shaadi mein harmony ke liye practical communication plan chahte hain?"
            },
            "timing": {
                "en": "Do you want clearer timing interpretation with preparation advice?",
                "devanagari": "क्या आप तैयारी सलाह के साथ स्पष्ट समय-व्याख्या चाहते हैं?",
                "roman": "Kya aap preparation advice ke saath clearer timing interpretation chahte hain?"
            },
            "general": {
                "en": "Would you like a short relationship action focus for the next month?",
                "devanagari": "क्या आप अगले महीने के लिए संबंध-केंद्रित कार्यदिशा चाहते हैं?",
                "roman": "Kya aap agle mahine ke liye relationship-focused action direction chahte hain?"
            }
        },
        "health": {
            "stress": {
                "en": "Do you want a stress-reduction routine aligned with your current phase?",
                "devanagari": "क्या आप वर्तमान चरण के अनुरूप तनाव-नियंत्रण दिनचर्या चाहते हैं?",
                "roman": "Kya aap current phase ke hisaab se stress-reduction routine chahte hain?"
            },
            "lifestyle": {
                "en": "Do you want a practical sleep-diet-routine reset plan?",
                "devanagari": "क्या आप नींद-आहार-रूटीन सुधार की व्यावहारिक योजना चाहते हैं?",
                "roman": "Kya aap sleep-diet-routine reset ki practical plan chahte hain?"
            },
            "medical": {
                "en": "Do you want a caution-first checklist for health monitoring?",
                "devanagari": "क्या आप स्वास्थ्य निगरानी के लिए सावधानी-आधारित चेकलिस्ट चाहते हैं?",
                "roman": "Kya aap health monitoring ke liye caution-first checklist chahte hain?"
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
        domain_map = FollowupRouter.INITIAL_QUESTIONS.get(domain, {})
        return domain_map.get(
            FollowupRouter._lang_key(language, script),
            "Would you like to go deeper in this area?"
        )

    @staticmethod
    def detect_followup_focus(domain, text):
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
    def is_followup_answer(text, last_followup_question, domain):
        if not text or not last_followup_question:
            return False

        focus = FollowupRouter.detect_followup_focus(domain, text)
        if focus != "general":
            return True

        tokens = len(text.split())
        if tokens <= 14 and not text.strip().startswith("/"):
            return True

        return False

    @staticmethod
    def get_next_followup_question(domain, focus, language, script, previous_question=None):
        domain_map = FollowupRouter.NEXT_QUESTIONS.get(domain, {})
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
            f"Follow-up context focus: {focus}\n"
            f"User follow-up answer: {user_text}\n\n"
            "Return ONLY a valid JSON object with keys:\n"
            "observation, cause, timing, guidance, followup\n\n"
            "Rules:\n"
            "- Keep each field concise and conversational.\n"
            "- Do not mention scores, rankings, engines, or internal systems.\n"
            "- Do not output markdown, headings, or extra text outside JSON.\n"
        )
