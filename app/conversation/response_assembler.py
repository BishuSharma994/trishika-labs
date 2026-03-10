import re


class ResponseAssembler:
    # DialogEngine appends one follow-up question sentence after assembly.
    MAX_TOTAL_SENTENCES = 11
    MIN_TOTAL_SENTENCES = 8
    MAX_LLM_SENTENCES = 3
    MAX_SENTENCE_WORDS = 24

    @staticmethod
    def _split_sentences(text):
        raw = str(text or "").strip()
        if not raw:
            return []

        compact = re.sub(r"\s+", " ", raw)
        chunks = re.split(r"(?<=[.!?।])\s+|(?<=;)\s+", compact)

        sentences = []
        for chunk in chunks:
            cleaned = re.sub(r"^[-*\d\)\.(]+\s*", "", chunk.strip())
            if cleaned:
                sentences.append(cleaned)

        if sentences:
            return sentences

        return [compact]

    @staticmethod
    def _normalize_key(sentence):
        lowered = str(sentence or "").strip().lower()
        lowered = re.sub(r"[^\w\u0900-\u097f\s]", " ", lowered)
        lowered = re.sub(r"\s+", " ", lowered).strip()
        return lowered

    @staticmethod
    def _ensure_terminal_punctuation(sentence):
        s = str(sentence or "").strip()
        if not s:
            return ""

        if s.endswith((".", "!", "?", "।")):
            return s

        return f"{s}."

    @staticmethod
    def _trim_sentence(sentence):
        words = str(sentence or "").split()
        if len(words) <= ResponseAssembler.MAX_SENTENCE_WORDS:
            return ResponseAssembler._ensure_terminal_punctuation(sentence)

        trimmed = " ".join(words[: ResponseAssembler.MAX_SENTENCE_WORDS]).rstrip(",;:")
        return ResponseAssembler._ensure_terminal_punctuation(trimmed)

    @staticmethod
    def _is_greeting(sentence):
        s = str(sentence or "").strip().lower()
        if not s:
            return False

        markers = (
            "hello",
            "hi",
            "namaste",
            "dear",
            "good morning",
            "good evening",
            "नमस्ते",
            "नमस्कार",
        )

        return any(s.startswith(marker) for marker in markers)

    @staticmethod
    def _looks_duplicate(sentence, existing_keys):
        key = ResponseAssembler._normalize_key(sentence)
        if not key:
            return True

        if key in existing_keys:
            return True

        key_tokens = set(key.split())
        if len(key_tokens) < 4:
            return False

        for seen in existing_keys:
            seen_tokens = set(seen.split())
            if not seen_tokens:
                continue

            overlap = len(key_tokens & seen_tokens)
            smaller = min(len(key_tokens), len(seen_tokens))
            if smaller >= 4 and overlap / float(smaller) >= 0.8:
                return True

        return False

    @staticmethod
    def assemble_response(
        persona_intro,
        life_stage_text,
        astrology_reasoning,
        timing_text,
        advice_text,
        llm_lines,
    ):
        deterministic_sections = [
            (persona_intro, 1),
            (life_stage_text, 2),
            (astrology_reasoning, 3),
            (timing_text, 2),
            (advice_text, 2),
        ]

        deterministic_sentences = []
        for section, limit in deterministic_sections:
            section_sentences = ResponseAssembler._split_sentences(section)
            deterministic_sentences.extend(section_sentences[:limit])

        llm_sentences = ResponseAssembler._split_sentences(llm_lines)[: ResponseAssembler.MAX_LLM_SENTENCES]
        llm_target = min(2, len(llm_sentences))
        deterministic_limit = max(0, ResponseAssembler.MAX_TOTAL_SENTENCES - llm_target)

        merged = []
        deferred_deterministic = []
        seen_keys = set()
        greeting_used = False

        for sentence in deterministic_sentences:
            candidate = ResponseAssembler._trim_sentence(sentence)
            if not candidate:
                continue

            if ResponseAssembler._is_greeting(candidate):
                if greeting_used:
                    continue
                greeting_used = True

            if ResponseAssembler._looks_duplicate(candidate, seen_keys):
                continue

            if len(merged) < deterministic_limit:
                seen_keys.add(ResponseAssembler._normalize_key(candidate))
                merged.append(candidate)
            else:
                deferred_deterministic.append(candidate)

        for sentence in llm_sentences:
            candidate = ResponseAssembler._trim_sentence(sentence)
            if not candidate:
                continue

            if ResponseAssembler._is_greeting(candidate):
                continue

            if ResponseAssembler._looks_duplicate(candidate, seen_keys):
                continue

            seen_keys.add(ResponseAssembler._normalize_key(candidate))
            merged.append(candidate)

        for candidate in deferred_deterministic:
            if len(merged) >= ResponseAssembler.MAX_TOTAL_SENTENCES:
                break
            if ResponseAssembler._looks_duplicate(candidate, seen_keys):
                continue
            seen_keys.add(ResponseAssembler._normalize_key(candidate))
            merged.append(candidate)

        if len(merged) > ResponseAssembler.MAX_TOTAL_SENTENCES:
            merged = merged[: ResponseAssembler.MAX_TOTAL_SENTENCES]

        if len(merged) < ResponseAssembler.MIN_TOTAL_SENTENCES:
            # Keep deterministic content first; if still short, return what is available.
            merged = merged[: ResponseAssembler.MAX_TOTAL_SENTENCES]

        return " ".join(merged).strip()
