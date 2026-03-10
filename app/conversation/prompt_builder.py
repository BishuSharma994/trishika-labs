import json
from app.conversation.memory_engine import MemoryEngine


class AstrologerPrompts:

    SYSTEM_CONTEXT = """
You are assisting an astrologer with concise follow-on reasoning.
"""

    @staticmethod
    def _language_instruction(language, script):

        if language != "hi":
            return ""

        if script == "devanagari":
            return "\nRespond in Hindi using Devanagari script."

        if script == "roman":
            return "\nRespond in Hindi using Roman script (Hinglish)."

        return "\nRespond in Hindi."

    @staticmethod
    def _strict_reasoning_rules():
        return (
            "You are assisting an astrologer.\n"
            "Generate ONLY 3 short reasoning sentences that extend the provided astrology context.\n"
            "Do not repeat the explanation.\n\n"
            "Rules:\n"
            "- Maximum 3 sentences total.\n"
            "- No greeting or introduction.\n"
            "- No repetition of persona intro, life stage, planet explanation, timing, or advice already provided.\n"
            "- Do not restate astrology explanation that is already present.\n"
            "- Only expand reasoning with concise, practical continuation.\n"
            "- No bullet points, headings, or labels.\n"
        )

    @staticmethod
    def build_domain_prompt(
        domain,
        domain_data,
        language,
        script,
        user_id,
        question,
        structured_context=None,
    ):

        context = MemoryEngine.build_context(user_id)

        signals = {
            "domain": domain,
            "primary_driver": domain_data.get("primary_driver"),
            "risk_factor": domain_data.get("risk_factor"),
            "momentum": domain_data.get("momentum"),
        }

        consultation_context = {
            "persona_intro": "",
            "life_stage_text": "",
            "astrology_reasoning": "",
            "timing_text": "",
            "advice_text": "",
        }

        if isinstance(structured_context, dict):
            for key in consultation_context:
                consultation_context[key] = structured_context.get(key, "")

        prompt = f"""
{AstrologerPrompts.SYSTEM_CONTEXT}

Conversation so far:
{context}

User question:
{question}

Astrology signals:
{json.dumps(signals, indent=2, ensure_ascii=False)}

Existing consultation context (already written for the user):
{json.dumps(consultation_context, indent=2, ensure_ascii=False)}

{AstrologerPrompts._strict_reasoning_rules()}
"""

        prompt += AstrologerPrompts._language_instruction(language, script)

        return prompt

    @staticmethod
    def build_general_prompt(chart_data, question, language, script, user_id):

        context = MemoryEngine.build_context(user_id)

        chart_summary = {
            "lagna": chart_data.get("lagna"),
            "moon_sign": chart_data.get("moon_sign"),
            "current_dasha": chart_data.get("current_dasha"),
        }

        prompt = f"""
{AstrologerPrompts.SYSTEM_CONTEXT}

Conversation so far:
{context}

User question:
{question}

Birth chart summary:
{json.dumps(chart_summary, indent=2, ensure_ascii=False)}

Answer conversationally.
"""

        prompt += AstrologerPrompts._language_instruction(language, script)

        return prompt
