import re

from app.ai import ask_ai
from app.conversation.language_engine import LanguageEngine


class ConversationQualityGuard:
    BANNED_PATTERNS = (
        r"\bprimary[_ ]driver\b",
        r"\brisk[_ ]factor\b",
        r"\bmomentum\b",
        r"\bprojection\b",
        r"\bdomain score\b",
        r"\bjson\b",
        r"\bdasha\b",
        r"\bantardasha\b",
        r"\bmahadasha\b",
        r"\blagna\b",
        r"\bmoon sign\b",
    )

    STOCK_PHRASES = (
        "aapke chart ke hisaab se",
        "according to your chart",
        "as per your chart",
        "your chart suggests",
        "current phase",
        "active themes",
        "current life themes",
        "positive changes",
        "support milega",
        "results will come",
        "mixed signals",
        "agle future",
        "structured approach",
    )

    TIMING_MARKERS = (
        "week",
        "weeks",
        "month",
        "months",
        "mahine",
        "haft",
        "din",
        "day",
        "days",
    )

    ACTION_MARKERS = (
        "1.",
        "2.",
        "first",
        "second",
        "pehla",
        "doosra",
        "focus on",
        "kijiye",
        "rakhiye",
        "start",
        "avoid",
    )

    DISTRESS_MARKERS = (
        "lag raha",
        "pressure",
        "pareshan",
        "stress",
        "ruk gayi",
        "ruk gaya",
        "dar",
        "worried",
        "anxious",
        "burden",
        "karz",
        "jhagda",
    )

    ACK_MARKERS = (
        "samajh",
        "haan",
        "jo aap mehsoos",
        "yeh feeling",
        "i understand",
        "that makes sense",
        "i can see why",
        "bojh",
        "dabav",
    )

    @staticmethod
    def _normalize(text):
        return " ".join(str(text or "").strip().split())

    @staticmethod
    def _count_words(text):
        return len(re.findall(r"\w+", str(text or "")))

    @staticmethod
    def _contains_any(text, phrases):
        lowered = str(text or "").lower()
        return any(phrase in lowered for phrase in phrases)

    @staticmethod
    def _asks_for_timing(user_text):
        lowered = str(user_text or "").lower()
        return any(token in lowered for token in ("kab", "when", "how long", "kitna time", "timeline"))

    @staticmethod
    def _asks_for_actions(user_text):
        lowered = str(user_text or "").lower()
        return any(
            token in lowered
            for token in ("kya karna", "what should i do", "what to do", "kya karu", "guide me", "upay")
        )

    @staticmethod
    def _is_concern_statement(user_text):
        lowered = str(user_text or "").lower().strip()
        if not lowered:
            return False
        if ConversationQualityGuard._asks_for_actions(lowered) or ConversationQualityGuard._asks_for_timing(lowered):
            return False
        return any(token in lowered for token in ConversationQualityGuard.DISTRESS_MARKERS) or len(lowered.split()) >= 4

    @staticmethod
    def _user_shares_distress(user_text):
        lowered = str(user_text or "").lower()
        return any(token in lowered for token in ConversationQualityGuard.DISTRESS_MARKERS)

    @staticmethod
    def _reply_acknowledges(reply):
        lowered = str(reply or "").lower()
        first_clause = re.split(r"[.!?\n]", lowered, maxsplit=1)[0]
        return any(token in first_clause for token in ConversationQualityGuard.ACK_MARKERS)

    @staticmethod
    def _looks_like_question(text):
        return str(text or "").strip().endswith("?")

    @staticmethod
    def _has_timing_window(reply):
        lowered = str(reply or "").lower()
        if any(marker in lowered for marker in ConversationQualityGuard.TIMING_MARKERS):
            return True
        return bool(re.search(r"\b\d+\s*[-–]?\s*\d*\s*(week|weeks|month|months|day|days|haft|mahine|din)\b", lowered))

    @staticmethod
    def _has_action_structure(reply):
        lowered = str(reply or "").lower()
        return any(marker in lowered for marker in ConversationQualityGuard.ACTION_MARKERS)

    @staticmethod
    def _has_presentation_style_list(reply):
        return bool(re.search(r"\b\d+\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:", str(reply or "")))

    @staticmethod
    def score_reply(user_text, reply, language, script, selection_only=False):
        score = 10.0
        issues = []
        normalized = ConversationQualityGuard._normalize(reply)
        lowered = normalized.lower()

        if not normalized:
            return 0.0, ["empty_reply"]

        for pattern in ConversationQualityGuard.BANNED_PATTERNS:
            if re.search(pattern, lowered):
                score -= 1.2
                issues.append(f"banned:{pattern}")

        for phrase in ConversationQualityGuard.STOCK_PHRASES:
            if phrase in lowered:
                score -= 0.6
                issues.append(f"stock:{phrase}")

        words = ConversationQualityGuard._count_words(normalized)
        if selection_only:
            if words < 5:
                score -= 0.4
                issues.append("selection_too_short")
            if words > 30:
                score -= 1.0
                issues.append("selection_too_long")
        elif words < 10:
            score -= 1.0
            issues.append("too_short")
        if words > 110:
            score -= 0.8
            issues.append("too_long")

        if selection_only and not ConversationQualityGuard._looks_like_question(normalized):
            score -= 2.0
            issues.append("selection_without_question")

        if "**" in normalized or "__" in normalized or "`" in normalized:
            score -= 0.6
            issues.append("markdown_formatting")

        if ConversationQualityGuard._asks_for_timing(user_text) and not ConversationQualityGuard._has_timing_window(normalized):
            score -= 1.4
            issues.append("timing_missing")

        if ConversationQualityGuard._asks_for_actions(user_text) and not ConversationQualityGuard._has_action_structure(normalized):
            score -= 1.4
            issues.append("actions_missing")

        if ConversationQualityGuard._has_presentation_style_list(normalized):
            score -= 0.8
            issues.append("presentation_style_list")

        if (
            ConversationQualityGuard._is_concern_statement(user_text)
            and not ConversationQualityGuard._asks_for_actions(user_text)
            and ConversationQualityGuard._has_action_structure(normalized)
        ):
            score -= 1.5
            issues.append("premature_action_list")

        if (
            ConversationQualityGuard._user_shares_distress(user_text)
            and not ConversationQualityGuard._reply_acknowledges(normalized)
        ):
            score -= 1.2
            issues.append("missing_emotional_ack")

        detected = LanguageEngine.detect_language(normalized)
        if language == LanguageEngine.ENGLISH and detected != LanguageEngine.ENGLISH:
            score -= 1.6
            issues.append("english_mismatch")
        if language == LanguageEngine.HINDI_DEVANAGARI and detected != LanguageEngine.HINDI_DEVANAGARI:
            score -= 1.6
            issues.append("devanagari_mismatch")

        if language == LanguageEngine.HINDI_ROMAN and re.search(r"[\u0900-\u097f]", normalized):
            score -= 1.2
            issues.append("roman_script_mismatch")

        return max(0.0, round(score, 2)), issues

    @staticmethod
    def sanitize(reply):
        text = ConversationQualityGuard._normalize(reply)
        if not text:
            return text

        replacements = (
            (r"(?i)\baccording to your chart[:,]?\s*", ""),
            (r"(?i)\bas per your chart[:,]?\s*", ""),
            (r"(?i)\byour chart suggests[:,]?\s*", ""),
            (r"(?i)\baapke chart ke hisaab se[:,]?\s*", ""),
            (r"(?i)\baapki kundli ke hisaab se[:,]?\s*", ""),
        )

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)

        text = text.replace("**", "").replace("__", "").replace("`", "")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def maybe_rewrite(user_text, draft_reply, language, script, topic=None, selection_only=False):
        cleaned = ConversationQualityGuard.sanitize(draft_reply)
        score, issues = ConversationQualityGuard.score_reply(
            user_text=user_text,
            reply=cleaned,
            language=language,
            script=script,
            selection_only=selection_only,
        )

        if score >= 9.7:
            return cleaned, score, issues

        current_reply = cleaned
        current_score = score
        current_issues = issues

        for _ in range(2):
            issue_list = ", ".join(current_issues) if current_issues else "generic_tone"
            rewrite_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are polishing a Vedic astrologer bot reply for production quality. "
                        "Rewrite the draft so it sounds premium, natural, specific, and human, like a thoughtful astrologer replying on WhatsApp. "
                        "Keep the same language and script as the user. "
                        "Do not mention chart, dasha, lagna, moon sign, internal scores, or internal labels unless the user explicitly asked for astrological basis. "
                        "Avoid stock openings, awkward phrasing, vague filler, and presentation-style formatting. "
                        "Replace phrases like active themes, current phase, or positive changes with natural real-life language. "
                        "If the user sounds worried or pressured, open with one brief human acknowledgment before guidance. "
                        "If the user asked timing, include a natural time window. "
                        "If the user asked what to do, give 2-3 concrete action steps in spoken language, not heading-style labels. "
                        "If the latest user message is only a topic/subtopic selection, return exactly one concise clarifying question without a greeting or extra commentary."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic or 'general'}\n"
                        f"Latest user message: {user_text}\n"
                        f"Draft reply: {current_reply}\n"
                        f"Quality issues: {issue_list}\n"
                        "Rewrite now."
                    ),
                },
            ]

            rewritten = ask_ai(rewrite_messages)
            rewritten = ConversationQualityGuard.sanitize(rewritten)
            rewritten_score, rewritten_issues = ConversationQualityGuard.score_reply(
                user_text=user_text,
                reply=rewritten,
                language=language,
                script=script,
                selection_only=selection_only,
            )

            if rewritten_score > current_score:
                current_reply = rewritten
                current_score = rewritten_score
                current_issues = rewritten_issues

            if current_score >= 9.85:
                break

        return current_reply, current_score, current_issues
