import json

from app.astro_engine import ParashariEngine
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.life_translation_engine import translate_to_life_guidance
from app.conversation.memory_engine import MemoryEngine
from app.conversation.profile_manager import ProfileManager
from app.conversation.state_manager import StateManager
from app.conversation.life_stage_detector import detect as detect_life_stage
from app.utils.age_calculator import calculate_age
from app.utils.birth_data_parser import BirthDataParser
from app.utils.geo_resolver import resolve_coordinates


# -----------------------------------------------------------------------------
# Keyboard / text helpers (language-aware)
# -----------------------------------------------------------------------------

TOPIC_TEXTS = {
    LanguageEngine.ENGLISH:          "Birth details received.\n\nWhat would you like to understand first?",
    LanguageEngine.HINDI_ROMAN:      "Janm details mil gayi.\n\nSabse pehle kis baare mein samajhna chahenge?",
    LanguageEngine.HINDI_DEVANAGARI: "\u091c\u0928\u094d\u092e \u0935\u093f\u0935\u0930\u0923 \u092e\u093f\u0932 \u0917\u090f\u0964\n\n\u0938\u092c\u0938\u0947 \u092a\u0939\u0932\u0947 \u0915\u093f\u0938 \u0935\u093f\u0937\u092f \u092e\u0947\u0902 \u0938\u092e\u091d\u0928\u093e \u091a\u093e\u0939\u0947\u0902\u0917\u0947?",
}

TOPIC_KEYBOARDS = {
    LanguageEngine.ENGLISH:          [["Career", "Marriage"], ["Finance", "Health"]],
    LanguageEngine.HINDI_ROMAN:      [["Career", "Shaadi"],   ["Finance", "Health"]],
    LanguageEngine.HINDI_DEVANAGARI: [["\u0915\u0930\u093f\u092f\u0930", "\u0935\u093f\u0935\u093e\u0939"], ["\u0935\u093f\u0924\u094d\u0924", "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f"]],
}

TOPIC_RETRY_TEXTS = {
    LanguageEngine.ENGLISH:          "Please choose one area first: Career, Marriage, Finance, or Health.",
    LanguageEngine.HINDI_ROMAN:      "Pehle ek area choose kijiye: Career, Shaadi, Finance, ya Health.",
    LanguageEngine.HINDI_DEVANAGARI: "\u0915\u0943\u092a\u092f\u093e \u092a\u0939\u0932\u0947 \u090f\u0915 \u0935\u093f\u0937\u092f \u091a\u0941\u0928\u0947\u0902: \u0915\u0930\u093f\u092f\u0930, \u0935\u093f\u0935\u093e\u0939, \u0935\u093f\u0924\u094d\u0924, \u092f\u093e \u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f\u0964",
}

BIRTHDATA_ERROR_TEXTS = {
    LanguageEngine.ENGLISH:          "Please share your date of birth, exact birth time, and birth place.\nExample: 15-08-1990, 10:30 AM, Delhi",
    LanguageEngine.HINDI_ROMAN:      "Kripya janm ki tareekh, exact samay, aur jagah bhejiye.\nUdaharan: 15-08-1990, 10:30 AM, Delhi",
    LanguageEngine.HINDI_DEVANAGARI: "\u0915\u0943\u092a\u092f\u093e \u091c\u0928\u094d\u092e \u0915\u0940 \u0924\u093e\u0930\u0940\u0916, \u0938\u091f\u0940\u0915 \u0938\u092e\u092f \u0914\u0930 \u091c\u0928\u094d\u092e \u0938\u094d\u0925\u093e\u0928 \u092d\u0947\u091c\u0947\u0902\u0964\n\u0909\u0926\u093e\u0939\u0930\u0923: 15-08-1990, 10:30 AM, \u0926\u093f\u0932\u094d\u0932\u0940",
}

BIRTHDATA_PROMPT_TEXTS = {
    LanguageEngine.ENGLISH: (
        "Please share your date of birth, exact birth time, and birth place.\n"
        "Example: 15-08-1990, 10:30 AM, Delhi"
    ),
    LanguageEngine.HINDI_ROMAN: (
        "Kripya janm ki tareekh, exact samay, aur jagah bhejiye.\n"
        "Udaharan: 15-08-1990, 10:30 AM, Delhi"
    ),
    LanguageEngine.HINDI_DEVANAGARI: (
        "कृपया जन्म की तारीख, सटीक समय और जन्म स्थान भेजें।\n"
        "उदाहरण: 15-08-1990, 10:30 AM, दिल्ली"
    ),
}

PROFILE_LOADED_TEXTS = {
    LanguageEngine.ENGLISH:          "Using profile: {name}",
    LanguageEngine.HINDI_ROMAN:      "Yeh profile use kar rahe hain: {name}",
    LanguageEngine.HINDI_DEVANAGARI: "यह प्रोफाइल उपयोग हो रही है: {name}",
}

TOPIC_INPUT_ALIASES = {
    "career": {"career", "karir", "kariyar"},
    "marriage": {"marriage", "shaadi", "shadi", "vivah"},
    "finance": {"finance", "money", "paisa", "wealth"},
    "health": {"health", "sehat", "swasthya"},
}


def _topic_keyboard_response(lang, text_map=None):
    """Return a dict with text + topic selection keyboard."""
    texts = text_map or TOPIC_TEXTS
    return {
        "text": texts.get(lang, texts[LanguageEngine.ENGLISH]),
        "keyboard": {
            "keyboard": TOPIC_KEYBOARDS.get(lang, TOPIC_KEYBOARDS[LanguageEngine.ENGLISH]),
            "resize_keyboard": True,
            "one_time_keyboard": True,
        },
    }


def _birthdata_prompt_response(lang):
    return {
        "text": BIRTHDATA_PROMPT_TEXTS.get(lang, BIRTHDATA_PROMPT_TEXTS[LanguageEngine.ENGLISH]),
        "keyboard": {"remove_keyboard": True},
    }


def _normalize_free_text(text):
    return " ".join(str(text or "").strip().lower().split())


def _is_selection_only_input(text, topic):
    normalized = _normalize_free_text(text)
    if not normalized or not topic:
        return False

    if normalized in TOPIC_INPUT_ALIASES.get(topic, set()):
        return True

    detected_subtopic = ConsultationEngine._detect_subtopic(topic, text)
    if detected_subtopic and len(normalized.split()) <= 3:
        return True

    return False


def _infer_subtopic(user_id, topic, current_text):
    if not topic:
        return None

    direct = ConsultationEngine._detect_subtopic(topic, current_text)
    if direct:
        return direct

    history = list(MemoryEngine.get_history(user_id))
    for msg in reversed(history):
        if msg.get("role") != "user":
            continue
        subtopic = ConsultationEngine._detect_subtopic(topic, msg.get("content"))
        if subtopic:
            return subtopic

    return None


# -----------------------------------------------------------------------------

class DialogEngine:

    # ------------------------------------------------------------------
    @staticmethod
    def load_chart(user_id, session):
        dob   = session.dob
        tob   = session.tob
        place = session.place

        if session.chart_data:
            try:
                return json.loads(session.chart_data)
            except Exception:
                pass

        lat, lon = resolve_coordinates(place)
        chart = ParashariEngine.generate_chart(dob, tob, lat, lon)
        StateManager.update_session(user_id, chart_data=json.dumps(chart))
        return chart

    # ------------------------------------------------------------------
    @staticmethod
    def process(user_id, text, session=None):
        MemoryEngine.add_user_message(user_id, text)
        session = StateManager.get_or_create_session(user_id)

        # Single source of truth for language
        lang   = getattr(session, "language_mode", LanguageEngine.ENGLISH) or LanguageEngine.ENGLISH
        script = getattr(session, "script", None) or "latin"

        # --------------------------------------------------------------
        # /start - reset everything
        # --------------------------------------------------------------
        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None,
                language_mode=None,
                language_confirmed=False,
                language_state_blob=None,
                last_domain=None,
                conversation_phase=ConsultationEngine.START,
                consultation_state_blob=ConsultationEngine.bootstrap_state(
                    language=LanguageEngine.ENGLISH,
                    flow_state=ConsultationEngine.START,
                ),
                chart_data=None,
                persona_introduced=False,
                pending_profile_name=None,
                active_profile_name=None,
            )
            MemoryEngine.clear(user_id)
            return {
                "text": "Please choose your language to begin.\n\n\u0915\u0943\u092a\u092f\u093e \u0936\u0941\u0930\u0942 \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0905\u092a\u0928\u0940 \u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902\u0964",
                "keyboard": {
                    "keyboard": [["English"], ["\u0939\u093f\u0902\u0926\u0940"], ["Hindi (Roman)"]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                },
            }

        # --------------------------------------------------------------
        # LANGUAGE FLOW
        # --------------------------------------------------------------
        language_result = LanguageEngine.handle_language(session, text)
        if language_result:
            old_mode = getattr(session, "language_mode", None)
            update = {}
            if language_result.get("language_mode"):
                new_mode = language_result["language_mode"]
                update["language_mode"] = new_mode
                update["language"] = new_mode
                update["consultation_state_blob"] = ConsultationEngine.reset_language(
                    getattr(session, "consultation_state_blob", None),
                    new_mode,
                )
                consultation_state = ConsultationEngine.load_state(update["consultation_state_blob"])
                update["conversation_phase"] = consultation_state.get("state")
            if "language_confirmed" in language_result:
                update["language_confirmed"] = language_result["language_confirmed"]
            if language_result.get("state_blob"):
                update["language_state_blob"] = language_result["state_blob"]
            if language_result.get("script"):
                update["script"] = language_result["script"]
            if language_result.get("step"):
                update["step"] = language_result["step"]

            # Explicit language switch while already in conversation should reset repetition context.
            if old_mode and language_result.get("language_mode") and language_result["language_mode"] != old_mode:
                update["consultation_state_blob"] = ConsultationEngine.reset_language(
                    getattr(session, "consultation_state_blob", None),
                    language_result["language_mode"],
                )
                consultation_state = ConsultationEngine.load_state(update["consultation_state_blob"])
                update["conversation_phase"] = consultation_state.get("state")

            if update:
                StateManager.update_session(user_id, **update)
                for k, v in update.items():
                    setattr(session, k, v)

            if language_result.get("response"):
                reply = language_result["response"]
                bot_text = reply.get("text", "") if isinstance(reply, dict) else reply
                MemoryEngine.add_bot_message(user_id, bot_text)
                return reply

        # --------------------------------------------------------------
        # PROFILE SCOPE COLLECTION
        # --------------------------------------------------------------
        if session.step == "profile_scope":
            scope = ProfileManager.detect_profile_scope(text)

            if not scope:
                response = {
                    "text": ProfileManager.declaration_prompt(lang, script),
                    "keyboard": {
                        "keyboard": ProfileManager.declaration_keyboard(lang, script),
                        "resize_keyboard": True,
                        "one_time_keyboard": True,
                    },
                }
                MemoryEngine.add_bot_message(user_id, response["text"])
                return response

            if scope == "self":
                profile_name = ProfileManager.default_profile_name(lang, script)
                StateManager.update_session(
                    user_id,
                    pending_profile_name=profile_name,
                    active_profile_name=profile_name,
                    step="birthdata",
                    chart_data=None,
                    consultation_state_blob=ConsultationEngine.move_state(
                        getattr(session, "consultation_state_blob", None),
                        ConsultationEngine.COLLECT_BIRTHDATA,
                        language=lang,
                        reset_depth=True,
                    ),
                    conversation_phase=ConsultationEngine.COLLECT_BIRTHDATA,
                )
                response = _birthdata_prompt_response(lang)
                MemoryEngine.add_bot_message(user_id, response["text"])
                return response

            StateManager.update_session(
                user_id,
                pending_profile_name=None,
                step="profile_name",
                chart_data=None,
                consultation_state_blob=ConsultationEngine.move_state(
                    getattr(session, "consultation_state_blob", None),
                    ConsultationEngine.COLLECT_BIRTHDATA,
                    language=lang,
                    reset_depth=True,
                ),
                conversation_phase=ConsultationEngine.COLLECT_BIRTHDATA,
            )
            response = {
                "text": ProfileManager.profile_name_prompt(lang, script),
                "keyboard": {"remove_keyboard": True},
            }
            MemoryEngine.add_bot_message(user_id, response["text"])
            return response

        # --------------------------------------------------------------
        # PROFILE NAME COLLECTION (for family member)
        # --------------------------------------------------------------
        if session.step == "profile_name":
            profile_name = str(text or "").strip()

            if not profile_name or profile_name.startswith("/"):
                response = {
                    "text": ProfileManager.profile_name_prompt(lang, script),
                    "keyboard": {"remove_keyboard": True},
                }
                MemoryEngine.add_bot_message(user_id, response["text"])
                return response

            existing_profiles = ProfileManager.parse_profiles(getattr(session, "profiles", None))
            existing_profile = None
            for item in existing_profiles:
                if str(item.get("name", "")).strip().lower() == profile_name.lower():
                    existing_profile = item
                    break

            if existing_profile and existing_profile.get("dob") and existing_profile.get("tob") and existing_profile.get("place"):
                dob = existing_profile.get("dob")
                tob = existing_profile.get("tob")
                place = existing_profile.get("place")
                age = calculate_age(dob)
                life_stage = detect_life_stage(age)
                StateManager.update_session(
                    user_id,
                    pending_profile_name=None,
                    active_profile_name=existing_profile.get("name", profile_name),
                    dob=dob,
                    tob=tob,
                    place=place,
                    age=age,
                    life_stage=life_stage,
                    step="question",
                    conversation_phase=ConsultationEngine.TOPIC_SELECTION,
                    consultation_state_blob=ConsultationEngine.bootstrap_state(
                        language=lang,
                        flow_state=ConsultationEngine.TOPIC_SELECTION,
                    ),
                    chart_data=None,
                )
                loaded_line = PROFILE_LOADED_TEXTS.get(lang, PROFILE_LOADED_TEXTS[LanguageEngine.ENGLISH]).format(
                    name=existing_profile.get("name", profile_name)
                )
                topic_response = _topic_keyboard_response(lang)
                topic_response["text"] = f"{loaded_line}\n\n{topic_response['text']}"
                MemoryEngine.add_bot_message(user_id, topic_response["text"])
                return topic_response

            StateManager.update_session(
                user_id,
                pending_profile_name=profile_name,
                active_profile_name=profile_name,
                step="birthdata",
                chart_data=None,
                consultation_state_blob=ConsultationEngine.move_state(
                    getattr(session, "consultation_state_blob", None),
                    ConsultationEngine.COLLECT_BIRTHDATA,
                    language=lang,
                    reset_depth=True,
                ),
                conversation_phase=ConsultationEngine.COLLECT_BIRTHDATA,
            )
            response = _birthdata_prompt_response(lang)
            MemoryEngine.add_bot_message(user_id, response["text"])
            return response

        # --------------------------------------------------------------
        # BIRTH DATA COLLECTION
        # --------------------------------------------------------------
        if session.step == "birthdata":
            parsed = BirthDataParser.parse_birth_data(text)
            dob    = parsed.get("date")
            tob    = parsed.get("time")
            place  = parsed.get("place")

            if not dob or not tob or not place:
                response = {
                    "text": BIRTHDATA_ERROR_TEXTS.get(lang, BIRTHDATA_ERROR_TEXTS[LanguageEngine.ENGLISH]),
                    "keyboard": {"remove_keyboard": True},
                }
                MemoryEngine.add_bot_message(user_id, response["text"])
                return response

            age        = calculate_age(dob)
            life_stage = detect_life_stage(age)
            profile_name = (
                getattr(session, "pending_profile_name", None)
                or getattr(session, "active_profile_name", None)
                or ProfileManager.default_profile_name(lang, script)
            )
            existing_profiles = ProfileManager.parse_profiles(getattr(session, "profiles", None))
            max_profiles = ProfileManager.max_profiles(session)
            updated_profiles, stored, limit_reached = ProfileManager.upsert_profile(
                existing_profiles,
                {
                    "name": profile_name,
                    "dob": dob,
                    "tob": tob,
                    "place": place,
                },
                max_profiles,
            )

            if limit_reached:
                if ProfileManager.is_premium(session):
                    limit_text = (
                        f"{ProfileManager.limit_message(lang, script)}\n\n"
                        f"{ProfileManager.upgrade_message(session, lang, script)}"
                    )
                else:
                    limit_text = ProfileManager.upgrade_message(session, lang, script)
                StateManager.update_session(
                    user_id,
                    step="profile_scope",
                    pending_profile_name=None,
                )
                response = {
                    "text": limit_text,
                    "keyboard": {
                        "keyboard": ProfileManager.declaration_keyboard(lang, script),
                        "resize_keyboard": True,
                        "one_time_keyboard": True,
                    },
                }
                MemoryEngine.add_bot_message(user_id, response["text"])
                return response

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                age=age,
                life_stage=life_stage,
                step="question",
                language_confirmed=True,
                consultation_state_blob=ConsultationEngine.bootstrap_state(
                    language=lang,
                    flow_state=ConsultationEngine.TOPIC_SELECTION,
                ),
                conversation_phase=ConsultationEngine.TOPIC_SELECTION,
                profiles=ProfileManager.serialize_profiles(updated_profiles if stored else existing_profiles),
                active_profile_name=profile_name,
                pending_profile_name=None,
                chart_data=None,
            )

            lang = getattr(session, "language_mode", LanguageEngine.ENGLISH) or LanguageEngine.ENGLISH
            response = _topic_keyboard_response(lang)
            MemoryEngine.add_bot_message(user_id, response["text"])
            return response

        # --------------------------------------------------------------
        # MAIN CONSULTATION
        # --------------------------------------------------------------
        if session.step == "question":
            consultation_state = ConsultationEngine.load_state(
                getattr(session, "consultation_state_blob", None)
            )
            active_topic = consultation_state.get("topic") or getattr(session, "last_domain", None)
            domain = IntentRouter.detect_domain(text, current_domain=active_topic)
            current_topic = domain or active_topic
            current_subtopic = _infer_subtopic(user_id, current_topic, text)
            
            chart        = DialogEngine.load_chart(user_id, session)
            score_domain = ConsultationEngine.score_domain(current_topic)
            if score_domain:
                domain_data = dict(chart.get("domain_scores", {}).get(score_domain, {}))
            else:
                domain_data = {}

            from app.ai import ask_ai
            from app.conversation.prompt_builder import AstrologerPrompts
            from app.conversation.quality_guard import ConversationQualityGuard

            # 1. Get System Instructions + Data
            llm_domain_data = {
                "topic": current_topic,
                "subtopic": current_subtopic,
                "lagna": chart.get("lagna"),
                "moon_sign": chart.get("moon_sign"),
                "current_dasha": chart.get("current_dasha"),
                **domain_data,
            }
            if current_topic:
                analysis_payload = ConsultationEngine._build_analysis_payload(
                    {"topic": current_topic},
                    domain_data,
                )
                grounded = translate_to_life_guidance(
                    analysis=analysis_payload,
                    topic=current_topic,
                    subtopic=current_subtopic,
                    depth=3,
                )
                llm_domain_data["grounded_guidance"] = {
                    "focus_areas": grounded.get("focus_areas", [])[:3],
                    "actions": grounded.get("actions", [])[:3],
                    "timeframe": grounded.get("timeframe"),
                    "routine": grounded.get("routine"),
                    "behavior": grounded.get("behavior"),
                }
            messages = AstrologerPrompts.build_system_messages(llm_domain_data, lang, script)
            selection_only = _is_selection_only_input(text, current_topic)
            if selection_only:
                messages.append(
                    {
                        "role": "system",
                        "content": (
                            f"Current discussion topic: {current_topic or 'general'}. "
                            "The latest user message is only a topic or subtopic selection. "
                            "Ask exactly one concise clarifying question. "
                            "Do not give analysis, timing, remedies, or bullet points yet."
                        ),
                    }
                )
            else:
                intent = IntentRouter.normalize_intent(text).get("intent")
                messages.append(
                    {
                        "role": "system",
                        "content": (
                            f"Current discussion topic: {current_topic or 'general'}. "
                            "The latest user message contains a real concern or follow-up. "
                            "Answer directly, stay specific, and avoid repeated stock openings."
                        ),
                    }
                )
                if intent == "timing":
                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                "The user is asking for timing. "
                                "Answer mainly with a natural time window and a short explanation. "
                                "Do not give a long action list unless the user explicitly asked for guidance."
                            ),
                        }
                    )
                elif intent in {"guidance", "remedy"}:
                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                "The user is explicitly asking what to do. "
                                "Give clear practical guidance in a human, spoken style."
                            ),
                        }
                    )
                else:
                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                "The user is sharing a situation or concern. "
                                "Interpret what is happening first. "
                                "Do not jump into a step list unless the user explicitly asks for guidance."
                            ),
                        }
                    )

            context_brief = MemoryEngine.build_context_brief(user_id)
            if context_brief:
                messages.append(
                    {
                        "role": "system",
                        "content": (
                            "Recent consultation context to preserve continuity:\n"
                            f"{context_brief}"
                        ),
                    }
                )

            # 2. Append Native Chat History
            history = MemoryEngine.get_history(user_id)
            for msg in history:
                messages.append(msg)

            # 3. Call OpenAI
            ai_reply = ask_ai(messages)
            ai_reply, quality_score, quality_issues = ConversationQualityGuard.maybe_rewrite(
                user_text=text,
                draft_reply=ai_reply,
                language=lang,
                script=script,
                topic=current_topic,
                selection_only=selection_only,
            )
            ai_reply = LanguageEngine.enforce_response_language(session, ai_reply)

            # 4. Save State and Memory
            StateManager.update_session(user_id, last_domain=current_topic)
            MemoryEngine.add_bot_message(user_id, ai_reply)

            return {
                "text": ai_reply,
                "keyboard": {"remove_keyboard": True},
            }

        # --------------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------------
        return {
            "text": "Type /start to begin.",
            "keyboard": {"remove_keyboard": True},
        }
