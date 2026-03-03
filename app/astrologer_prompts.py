import json


class AstrologerPrompts:

    SYSTEM_BASE = """You are a deterministic Parāśari astrology analysis engine.

STRICT RULES:
1. Use ONLY the JSON data provided.
2. Do NOT assume Dasha or Transit unless explicitly present in JSON.
3. Do NOT invent planetary positions.
4. Do NOT infer house placements unless given.
5. If information is missing, state: "Data not available."
6. Do NOT prescribe remedies unless explicitly derived from provided planetary house logic.
7. No speculative language.
"""


QA_PROMPT = """
USER PROFILE & ASTROLOGICAL DATA:
{astro_data_json}

USER QUESTION:
"{user_query}"

INSTRUCTIONS:
- Base interpretation STRICTLY on:
  1) Lagna
  2) Current Mahadasha
  3) Current Antardasha
  4) Transit influence
  5) Planetary dignity and strength
- Mention dasha planet explicitly.
- Mention transit impact explicitly.
- Provide one traditional Parāśari remedy.
- Keep answer concise (2-3 Telegram paragraphs).
"""

    @staticmethod
    def build_qa_prompt(user_query, astro_data):
        return (
            AstrologerPrompts.SYSTEM_BASE
            + "\n"
            + AstrologerPrompts.QA_PROMPT.format(
                user_query=user_query,
                astro_data_json=json.dumps(astro_data, indent=2),
            )
        )