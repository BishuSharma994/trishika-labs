import json
import logging
import re
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)


class ConsultationEngine:

    DOMAIN_ENTRY = "DOMAIN_ENTRY"
    STATUS_CAPTURE = "STATUS_CAPTURE"
    DIAGNOSTIC = "DIAGNOSTIC"
    INTERPRETATION = "INTERPRETATION"
    GUIDANCE = "GUIDANCE"
    ACTION_PLAN = "ACTION_PLAN"

    INTENT_HIGH_CONFIDENCE = 0.84
    INTENT_LOW_CONFIDENCE = 0.62

    INTENT_KEYWORDS = {
        "remedy": {
            "upay", "upaye", "upaay", "upaaye", "upai", "upaiye", "upaie", "upchar", "totka",
            "remedy", "remedies", "remady", "remeady", "remidey", "solution",
            "उपाय", "उपायों", "उपचार",
        },
        "timing": {
            "kab", "kabhi", "when", "timing", "time", "date", "samay", "kaisa timing",
            "timeline", "window", "समय", "कब", "टाइमिंग",
        },
        "detail": {
            "aur", "more", "detail", "details", "deep", "deeper", "zyada",
            "explain", "elaborate", "और", "विस्तार",
        },
        "affirm": {
            "yes", "haan", "han", "ha", "ji", "ok", "okay", "theek", "thik", "bilkul",
            "yes please", "please give", "de dijiye", "de do", "bataiye", "bataye",
            "haan ji", "जी", "हाँ",
        },
    }

    # --------------------------------------------------

    DOMAIN_ALIASES = {
        "career": ["career","job","naukri","profession","work"],
        "marriage": ["marriage","shaadi","vivah","wife","husband"],
        "finance": ["finance","money","paisa","income","wealth"],
        "health": ["health","fitness","disease","sehat"]
    }

    STATUS_MAP = {
        "marriage": {
            "single": ["1","single","not married","avivahit","अविवाहित"],
            "relationship": ["2","relationship","dating","sambandh","संबंध"],
            "married": ["3","married","already married","spouse","vivahit","विवाहित"]
        }
    }

    # --------------------------------------------------

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
    def _domain_entry_question(domain, language, script):
        if domain == "marriage":
            if ConsultationEngine._is_hi_dev(language, script):
                return (
                    "विवाह पर सही मार्गदर्शन के लिए पहले आपकी वर्तमान स्थिति समझना जरूरी है।\n\n"
                    "आपकी स्थिति क्या है?\n"
                    "1. अविवाहित\n"
                    "2. संबंध में\n"
                    "3. विवाहित"
                )
            if ConsultationEngine._is_hi_rom(language, script):
                return (
                    "Shaadi par sahi margdarshan ke liye pehle aapki vartaman sthiti samajhna zaroori hai.\n\n"
                    "Aapki sthiti kya hai?\n"
                    "1. Avivahit\n"
                    "2. Sambandh mein\n"
                    "3. Vivahit"
                )
            return (
                "To guide you accurately on marriage, I first need your current relationship status.\n\n"
                "What is your current situation?\n"
                "1. Single\n"
                "2. In a relationship\n"
                "3. Already married"
            )

        if ConsultationEngine._is_hi_dev(language, script):
            questions = {
                "career": "करियर में आपका मुख्य ध्यान किस पर है: नौकरी बदलना, पदोन्नति, या व्यापार दिशा?",
                "finance": "वित्त में आपका मुख्य ध्यान किस पर है: बचत, निवेश, या कर्ज प्रबंधन?",
                "health": "स्वास्थ्य में आपकी मुख्य चिंता क्या है: तनाव, जीवनशैली संतुलन, या कोई विशेष समस्या?",
            }
            return questions.get(domain, "कृपया इस विषय से जुड़ी अपनी वर्तमान स्थिति एक पंक्ति में बताएं।")

        if ConsultationEngine._is_hi_rom(language, script):
            questions = {
                "career": "Career mein aapka mukhya dhyan kis par hai: naukri badalna, padonnati, ya vyavsay disha?",
                "finance": "Vitt mein aapka mukhya dhyan kis par hai: bachat, nivesh, ya karz prabandhan?",
                "health": "Swasthya mein aapki mukhya chinta kya hai: tanav, jeevanshaili santulan, ya koi vishesh samasya?",
            }
            return questions.get(domain, "Kripya is vishay se judi apni vartaman sthiti ek pankti mein batayiye.")

        questions = {
            "career": "In career, what is your current focus: job switch, promotion, or business direction?",
            "finance": "In finance, what are you prioritizing right now: savings, investments, or debt management?",
            "health": "In health, is your concern mainly stress, lifestyle balance, or a specific issue?",
        }
        return questions.get(domain, "Please share your current situation in one line for this topic.")

    @staticmethod
    def _marriage_retry_prompt(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return "कृपया एक विकल्प चुनें:\n1 अविवाहित\n2 संबंध में\n3 विवाहित"
        if ConsultationEngine._is_hi_rom(language, script):
            return "Kripya ek vikalp chuniye:\n1 Avivahit\n2 Sambandh mein\n3 Vivahit"
        return "Please choose one option.\n1 Single\n2 Relationship\n3 Married"

    @staticmethod
    def _marriage_diagnostic_prompt(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return "वर्तमान संबंध की स्थिति स्थिर है, मिश्रित है, या तनावपूर्ण है?"
        if ConsultationEngine._is_hi_rom(language, script):
            return "Vartaman sambandh ki sthiti sthir hai, mishrit hai, ya tanavpurn hai?"
        return "Is your current relationship harmony stable, mixed, or under stress?"

    @staticmethod
    def _localized(language, script, en, hi_rom, hi_dev):
        if ConsultationEngine._is_hi_dev(language, script):
            return hi_dev
        if ConsultationEngine._is_hi_rom(language, script):
            return hi_rom
        return en

    @staticmethod
    def _status_noted_text(status, language, script):
        status_label = ConsultationEngine._status_label(status, language, script)
        return ConsultationEngine._localized(
            language,
            script,
            f"Noted. Current status: {status_label}.",
            f"Theek hai. Aapki vartaman sthiti: {status_label}.",
            f"ठीक है। आपकी वर्तमान स्थिति: {status_label}।",
        )

    @staticmethod
    def _domain_label(domain, language, script):
        labels = {
            "career": ("career", "career", "करियर"),
            "finance": ("finance", "vitt", "वित्त"),
            "marriage": ("relationship", "shaadi", "विवाह"),
            "health": ("health", "swasthya", "स्वास्थ्य"),
        }
        en, hi_rom, hi_dev = labels.get(domain, ("this area", "is area", "इस विषय"))
        return ConsultationEngine._localized(language, script, en, hi_rom, hi_dev)

    @staticmethod
    def _status_label(status, language, script):
        status_key = str(status or "").strip().lower()
        labels = {
            "single": ("single", "avivahit", "अविवाहित"),
            "relationship": ("in a relationship", "sambandh mein", "संबंध में"),
            "married": ("married", "vivahit", "विवाहित"),
        }
        en, hi_rom, hi_dev = labels.get(status_key, (status_key, status_key, status_key))
        return ConsultationEngine._localized(language, script, en, hi_rom, hi_dev)

    @staticmethod
    def _diagnostic_stage_text(domain, domain_data, language, script):
        primary_driver = domain_data.get("primary_driver") or "graha dasha ka prabhav"
        risk_factor = domain_data.get("risk_factor") or "jaldbaazi"
        domain_label = ConsultationEngine._domain_label(domain, language, script)
        return ConsultationEngine._localized(
            language,
            script,
            (
                f"From your chart and what you shared, this {domain_label} situation is workable. "
                f"The key driver is {primary_driver}, so progress is possible if you stay patient and consistent."
            ),
            (
                f"Aapki kundli ke sanket aur aapki baat ke aadhar par {domain_label} ki sthiti sambhalne yogya hai. "
                f"Ismein {primary_driver} ka pramukh prabhav hai, isliye {risk_factor} se bachkar dhairya se aage badhiye."
            ),
            (
                f"आपने जो साझा किया और कुंडली संकेत देखकर लगता है कि {domain_label} की स्थिति संभाली जा सकती है। "
                f"इसमें {primary_driver} का प्रभाव प्रमुख है, इसलिए {risk_factor} से बचते हुए धैर्य रखना जरूरी होगा।"
            ),
        )

    @staticmethod
    def _interpretation_stage_text(domain, domain_data, language, script):
        momentum = (domain_data.get("momentum") or "neutral").lower()
        if momentum == "positive":
            en_momentum = "momentum is supportive right now"
            hi_rom_momentum = "momentum abhi supportive hai"
            hi_dev_momentum = "गति इस समय सहायक है"
        elif momentum == "challenging":
            en_momentum = "the phase is sensitive right now"
            hi_rom_momentum = "yeh phase abhi sensitive hai"
            hi_dev_momentum = "यह चरण अभी संवेदनशील है"
        else:
            en_momentum = "momentum is mixed at the moment"
            hi_rom_momentum = "momentum abhi mixed hai"
            hi_dev_momentum = "गति इस समय मिश्रित है"

        return ConsultationEngine._localized(
            language,
            script,
            (
                f"Planetary combinations show that {en_momentum}. "
                "Take decisions in steps instead of one big jump, and verify timing before major commitments."
            ),
            (
                f"Grah sanyojan batate hain ki {hi_rom_momentum}. "
                "Nirnay ek saath lene ke bajay kadam-dar-kadam lijiye, aur bade faislon se pehle samay ka mulyankan kijiye."
            ),
            (
                f"ग्रह संयोजन दिखाते हैं कि {hi_dev_momentum}। "
                "निर्णय एक बार में लेने के बजाय चरणों में लें और बड़े निर्णयों से पहले समय का मूल्यांकन करें।"
            ),
        )

    @staticmethod
    def _guidance_stage_text(domain, language, script):
        domain_label = ConsultationEngine._domain_label(domain, language, script)
        return ConsultationEngine._localized(
            language,
            script,
            (
                f"For better {domain_label} outcomes, keep communication clear, "
                "avoid impulsive reactions, and review progress weekly."
            ),
            (
                f"Behtar {domain_label} parinam ke liye samvaad spasht rakhiye, "
                "aavesh mein pratikriya dene se bachiye, aur har saptah pragati ka punaravalokan kijiye."
            ),
            (
                f"बेहतर {domain_label} परिणामों के लिए संवाद स्पष्ट रखें, "
                "आवेगपूर्ण प्रतिक्रिया से बचें और साप्ताहिक प्रगति की समीक्षा करें।"
            ),
        )

    @staticmethod
    def _action_plan_text(domain, domain_data, language, script, user_text):
        risk_factor = domain_data.get("risk_factor") or "jaldbaazi"
        focus_line = str(user_text or "").strip()
        if len(focus_line) > 120:
            focus_line = focus_line[:120].rstrip() + "..."
        if not focus_line:
            focus_line = ConsultationEngine._localized(
                language,
                script,
                "current concern",
                "vartaman chinta",
                "वर्तमान चिंता",
            )

        return ConsultationEngine._localized(
            language,
            script,
            (
                "Let's move practically.\n"
                f"1) For the next 7 days, stay consistent on one priority linked to '{focus_line}'.\n"
                f"2) Avoid decisions during high {risk_factor} moments; pause and reassess after a few hours.\n"
                "3) On day 8, review what improved and what repeated.\n\n"
                "If you want, I can now go deeper into timing or remedies for this exact concern."
            ),
            (
                "Chaliye ise vyavaharik roop se aage badhate hain.\n"
                f"1) Agle 7 din '{focus_line}' se judi ek mukhya disha par lagataar dhyan rakhiye.\n"
                f"2) {risk_factor} ke dauran turant nirnay na lijiye; kuch ghante rukkar punah sochiye.\n"
                "3) Athve din dekhiyega kya sudhara aur kya baar-baar doharaya gaya.\n\n"
                "Agar aap chahein to ab main isi mudde par sidhe upay ya spasht samay margdarshan de sakta hoon."
            ),
            (
                "इसे व्यावहारिक तरीके से आगे बढ़ाते हैं।\n"
                f"1) अगले 7 दिन '{focus_line}' से जुड़ी एक मुख्य दिशा पर लगातार ध्यान दें।\n"
                f"2) {risk_factor} के दौरान तुरंत निर्णय न लें; कुछ घंटे रुककर पुनः विचार करें।\n"
                "3) 8वें दिन देखें क्या बेहतर हुआ और क्या दोहराया गया।\n\n"
                "यदि चाहें तो अब मैं इसी विषय पर सीधे उपाय या स्पष्ट समय मार्गदर्शन दे सकता हूँ।"
            ),
        )

    @staticmethod
    def _next_question_text(language, script):
        return ConsultationEngine._localized(
            language,
            script,
            "Share your next question.",
            "Apna agla sawal share kijiye.",
            "अपना अगला सवाल साझा कीजिए।",
        )

    @staticmethod
    def _contains_any(text, words):
        t = ConsultationEngine._normalized_text(text)
        return any(w in t for w in words)

    @staticmethod
    def _normalized_text(text):
        t = str(text or "").lower()
        t = re.sub(r"[^a-z0-9\u0900-\u097f\s]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    @staticmethod
    def _best_similarity_match(tokens, keywords):
        best_score = 0.0
        best_token = None
        best_keyword = None
        for token in tokens:
            if len(token) < 3:
                continue
            for keyword in keywords:
                if len(keyword) < 3:
                    continue
                score = SequenceMatcher(None, token, keyword).ratio()
                if score > best_score:
                    best_score = score
                    best_token = token
                    best_keyword = keyword
        return best_score, best_token, best_keyword

    @staticmethod
    def _log_intent_event(domain, stage, text, intent, confidence, note, method=None, matched=None):
        sample = ConsultationEngine._normalized_text(text)[:160]
        logger.info(
            "intent_telemetry domain=%s stage=%s intent=%s confidence=%.2f note=%s method=%s matched=%s text=%s",
            domain,
            stage,
            intent,
            confidence,
            note,
            method or "na",
            matched or "na",
            sample,
        )

    @staticmethod
    def _is_question_like(text):
        raw = str(text or "")
        normalized = ConsultationEngine._normalized_text(text)
        if "?" in raw:
            return True
        question_words = {
            "kya", "kaise", "kab", "kyon", "kyu", "how", "what", "when", "why", "can", "please",
            "बताइए", "कैसे", "कब", "क्या", "क्यों",
        }
        tokens = set(normalized.split())
        return bool(tokens & question_words)

    @staticmethod
    def _intent_clarifier_text(language, script):
        return ConsultationEngine._localized(
            language,
            script,
            "To guide you precisely, reply with one choice: remedy, timing, or detail.",
            "Sahi margdarshan ke liye ek vikalp likhiye: upay, timing, ya detail.",
            "सटीक मार्गदर्शन के लिए एक विकल्प लिखें: उपाय, समय, या विस्तार।",
        )

    @staticmethod
    def _detect_followup_intent(user_text):
        t = ConsultationEngine._normalized_text(user_text)
        base = {
            "intent": None,
            "confidence": 0.0,
            "method": "none",
            "candidate": None,
            "matched": None,
        }
        if not t:
            return base

        tokens = t.split()

        # Exact containment has top priority.
        for intent in ("remedy", "timing", "detail", "affirm"):
            keywords = ConsultationEngine.INTENT_KEYWORDS[intent]
            if any((kw in t) for kw in keywords):
                return {
                    "intent": intent,
                    "confidence": 0.99,
                    "method": "exact",
                    "candidate": intent,
                    "matched": intent,
                }

        # Fuzzy fallback for spelling mistakes.
        best_intent = None
        best_score = 0.0
        best_match = None
        for intent in ("remedy", "timing", "detail", "affirm"):
            score, token, keyword = ConsultationEngine._best_similarity_match(
                tokens, ConsultationEngine.INTENT_KEYWORDS[intent]
            )
            if score > best_score:
                best_score = score
                best_intent = intent
                best_match = f"{token}->{keyword}" if token and keyword else None

        if best_intent and best_score >= ConsultationEngine.INTENT_HIGH_CONFIDENCE:
            return {
                "intent": best_intent,
                "confidence": best_score,
                "method": "fuzzy_high",
                "candidate": best_intent,
                "matched": best_match,
            }
        if best_intent and best_score >= ConsultationEngine.INTENT_LOW_CONFIDENCE:
            return {
                "intent": None,
                "confidence": best_score,
                "method": "fuzzy_low",
                "candidate": best_intent,
                "matched": best_match,
            }

        return base

    @staticmethod
    def _momentum_label(momentum, language, script):
        momentum_key = (momentum or "neutral").lower()
        if momentum_key == "positive":
            return ConsultationEngine._localized(language, script, "supportive", "anukul", "अनुकूल")
        if momentum_key == "challenging":
            return ConsultationEngine._localized(language, script, "sensitive", "sankraman-sheel", "संवेदनशील")
        return ConsultationEngine._localized(language, script, "mixed", "mishrit", "मिश्रित")

    @staticmethod
    def _direct_followup_response(domain, domain_data, language, script, intent):
        momentum = (domain_data.get("momentum") or "mixed").lower()
        risk_factor = domain_data.get("risk_factor") or "jaldbaazi"
        domain_label = ConsultationEngine._domain_label(domain, language, script)
        momentum_label = ConsultationEngine._momentum_label(momentum, language, script)

        if intent == "remedy":
            return ConsultationEngine._localized(
                language,
                script,
                (
                    f"For {domain_label}, start with these remedies: keep a fixed morning discipline, "
                    f"avoid reactive decisions around {risk_factor}, and take one grounded action daily for 21 days."
                ),
                (
                    f"{domain_label} ke liye pramukh upay yeh hain: subah ka niyamit anushasan rakhiye, "
                    f"{risk_factor} ke samay turant nirnay na lijiye, aur 21 din tak roz ek sthir kadam lijiye."
                ),
                (
                    f"{domain_label} के लिए पहले ये उपाय अपनाएँ: सुबह की दिनचर्या स्थिर रखें, "
                    f"{risk_factor} के समय आवेगपूर्ण निर्णय न लें, और 21 दिन तक रोज़ एक स्थिर कदम लें।"
                ),
            )

        if intent == "timing":
            return ConsultationEngine._localized(
                language,
                script,
                (
                    f"Timing-wise, momentum for {domain_label} is currently {momentum_label}. "
                    "Next 6-12 weeks should be used for preparation and calibrated execution."
                ),
                (
                    f"Samay ke hisab se {domain_label} ka pravah abhi {momentum_label} hai. "
                    "Agle 6-12 hafton mein taiyari aur santulit kriyanvayan sarvottam rahega."
                ),
                (
                    f"समय के अनुसार {domain_label} का प्रवाह अभी {momentum_label} है। "
                    "अगले 6-12 सप्ताह तैयारी और संतुलित क्रियान्वयन के लिए उपयुक्त रहेंगे।"
                ),
            )

        if intent == "detail":
            return ConsultationEngine._localized(
                language,
                script,
                (
                    f"Going deeper: in {domain_label}, progress will come from consistency, not speed. "
                    f"Your main leverage is disciplined execution while managing {risk_factor} patterns."
                ),
                (
                    f"Gehraai se dekhein to {domain_label} mein pragati gati se nahi, lagataar prayas se aayegi. "
                    f"Aapki mukhya shakti anushasit kriya hai; bas {risk_factor} ke dhanche ko niyantrit rakhiye."
                ),
                (
                    f"और गहराई से देखें तो {domain_label} में प्रगति गति से नहीं, निरंतरता से आएगी। "
                    f"आपकी मुख्य शक्ति अनुशासित क्रिया है; बस {risk_factor} के पैटर्न को नियंत्रित रखें।"
                ),
            )

        return None

    # --------------------------------------------------

    @staticmethod
    def detect_domain(text, current_domain=None):

        t = str(text or "").lower()

        for domain, aliases in ConsultationEngine.DOMAIN_ALIASES.items():
            for alias in aliases:
                if re.search(rf"\b{alias}\b", t):
                    return domain

        return None

    # --------------------------------------------------

    @staticmethod
    def score_domain(domain):

        return domain

    # --------------------------------------------------

    @staticmethod
    def load_state(blob):

        if not blob:
            return {"domain_memory": {}}

        try:
            return json.loads(blob)
        except Exception:
            return {"domain_memory": {}}

    @staticmethod
    def dump_state(state):

        return json.dumps(state, ensure_ascii=False)

    # --------------------------------------------------

    @staticmethod
    def parse_status(domain, text):

        mapping = ConsultationEngine.STATUS_MAP.get(domain, {})

        t = str(text or "").lower()

        for status, words in mapping.items():
            for w in words:
                if re.search(rf"\b{w}\b", t):
                    return status

        return None

    # --------------------------------------------------

    @staticmethod
    def generate_response(
        domain,
        domain_data,
        language,
        script,
        stage,
        age,
        life_stage,
        user_goal,
        current_dasha,
        transits,
        persona_introduced=False,
        chart=None,
        theme_shown=False,
        user_text="",
        session_state_blob=None,
        domain_switched=False,
    ):

        state = ConsultationEngine.load_state(session_state_blob)

        memory = state["domain_memory"].setdefault(domain, {})
        intent_info = ConsultationEngine._detect_followup_intent(user_text)
        detected_intent = intent_info["intent"]
        intent_candidate = intent_info["candidate"]

        if intent_info["method"] == "fuzzy_low":
            ConsultationEngine._log_intent_event(
                domain=domain,
                stage=stage,
                text=user_text,
                intent=intent_candidate,
                confidence=float(intent_info["confidence"]),
                note="low_confidence_candidate",
                method=intent_info.get("method"),
                matched=intent_info.get("matched"),
            )

        if detected_intent in {"remedy", "timing", "detail"}:
            memory["last_requested_intent"] = detected_intent
            memory["pending_intent"] = detected_intent
        elif detected_intent == "affirm":
            pending_intent = memory.get("pending_intent")
            if pending_intent in {"remedy", "timing", "detail"}:
                detected_intent = pending_intent
            else:
                detected_intent = None

        if stage in {
            ConsultationEngine.DIAGNOSTIC,
            ConsultationEngine.INTERPRETATION,
            ConsultationEngine.GUIDANCE,
            ConsultationEngine.ACTION_PLAN,
        } and detected_intent in {"remedy", "timing", "detail"}:
            direct_reply = ConsultationEngine._direct_followup_response(
                domain=domain,
                domain_data=domain_data or {},
                language=language,
                script=script,
                intent=detected_intent,
            )
            if direct_reply:
                memory["pending_intent"] = None
                return {
                    "text": direct_reply,
                    "next_stage": ConsultationEngine.ACTION_PLAN,
                    "state_blob": ConsultationEngine.dump_state(state),
                }

        if (
            stage in {ConsultationEngine.GUIDANCE, ConsultationEngine.ACTION_PLAN}
            and detected_intent is None
            and ConsultationEngine._is_question_like(user_text)
        ):
            if intent_candidate in {"remedy", "timing", "detail"}:
                memory["pending_intent"] = intent_candidate
            ConsultationEngine._log_intent_event(
                domain=domain,
                stage=stage,
                text=user_text,
                intent=intent_candidate or "unknown",
                confidence=float(intent_info.get("confidence") or 0.0),
                note="clarifier_prompted",
                method=intent_info.get("method"),
                matched=intent_info.get("matched"),
            )
            return {
                "text": ConsultationEngine._intent_clarifier_text(language, script),
                "next_stage": ConsultationEngine.ACTION_PLAN,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # DOMAIN ENTRY
        # ------------------------------------------

        if stage == ConsultationEngine.DOMAIN_ENTRY:
            question = ConsultationEngine._domain_entry_question(domain, language, script)
            next_stage = (
                ConsultationEngine.STATUS_CAPTURE
                if domain == "marriage"
                else ConsultationEngine.DIAGNOSTIC
            )

            return {
                "text": question,
                "next_stage": next_stage,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # STATUS CAPTURE
        # ------------------------------------------

        if stage == ConsultationEngine.STATUS_CAPTURE:
            if domain != "marriage":
                memory["status"] = str(user_text or "").strip()
                if ConsultationEngine._is_hi_dev(language, script):
                    bridge_text = "ठीक है, यह मैंने नोट कर लिया। अब मैं इसे आपकी कुंडली के संकेतों के साथ जोड़कर देखता हूँ।"
                elif ConsultationEngine._is_hi_rom(language, script):
                    bridge_text = "Theek hai, maine yeh note kar liya. Ab main ise aapki kundli ke sanketon ke saath dekh raha hoon."
                else:
                    bridge_text = "Noted. I will now evaluate this with your chart signals."
                return {
                    "text": bridge_text,
                    "next_stage": ConsultationEngine.DIAGNOSTIC,
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            status = ConsultationEngine.parse_status(domain, user_text)

            if not status:

                return {
                    "text": ConsultationEngine._marriage_retry_prompt(language, script),
                    "next_stage": ConsultationEngine.STATUS_CAPTURE,
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            memory["status"] = status

            question = ConsultationEngine._marriage_diagnostic_prompt(language, script)
            status_noted = ConsultationEngine._status_noted_text(status, language, script)

            return {
                "text": f"{status_noted}\n\n{question}",
                "next_stage": ConsultationEngine.DIAGNOSTIC,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # DIAGNOSTIC
        # ------------------------------------------

        if stage == ConsultationEngine.DIAGNOSTIC:

            memory["diagnostic"] = user_text

            text = ConsultationEngine._diagnostic_stage_text(
                domain=domain,
                domain_data=domain_data,
                language=language,
                script=script,
            )

            return {
                "text": text,
                "next_stage": ConsultationEngine.INTERPRETATION,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # INTERPRETATION
        # ------------------------------------------

        if stage == ConsultationEngine.INTERPRETATION:

            text = ConsultationEngine._interpretation_stage_text(
                domain=domain,
                domain_data=domain_data,
                language=language,
                script=script,
            )

            return {
                "text": text,
                "next_stage": ConsultationEngine.GUIDANCE,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # GUIDANCE
        # ------------------------------------------

        if stage == ConsultationEngine.GUIDANCE:

            text = ConsultationEngine._guidance_stage_text(
                domain=domain,
                language=language,
                script=script,
            )

            return {
                "text": text,
                "next_stage": ConsultationEngine.ACTION_PLAN,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------

        if stage == ConsultationEngine.ACTION_PLAN:
            memory["last_action_focus"] = str(user_text or "").strip()
            if not memory.get("pending_intent"):
                memory["pending_intent"] = memory.get("last_requested_intent") or "remedy"
            text = ConsultationEngine._action_plan_text(
                domain=domain,
                domain_data=domain_data,
                language=language,
                script=script,
                user_text=user_text,
            )
            return {
                "text": text,
                "next_stage": ConsultationEngine.ACTION_PLAN,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------

        return {
            "text": ConsultationEngine._next_question_text(language, script),
            "next_stage": ConsultationEngine.ACTION_PLAN,
            "state_blob": ConsultationEngine.dump_state(state),
        }
