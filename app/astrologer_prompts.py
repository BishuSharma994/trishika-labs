import json


class AstrologerPrompts:

    SYSTEM_BASE = """You are an expert, traditional, deterministic Parāśari Vedic astrologer.

STRICT RULES:
1) Use only provided structured data.
2) Base interpretation on Lagna, Dasha, Transit, Dignity, and Strength.
3) Never invent planetary positions.
4) Never predict death or medical diagnosis.
"""

    QA_PROMPT = """
USER PROFILE & ASTROLOGICAL DATA:
{astro_data_json}

USER QUESTION:
"{user_query}"

INSTRUCTIONS:
- Primary determinant: Mahadasha lord.
- Secondary: Antardasha lord.
- Tertiary: Pratyantardasha lord.
- Then evaluate natal placement of these planets.
- Then apply transit of these same planets.
- Lagna provides structural context only.
- Do not equalize all factors.
- Weight analysis in descending hierarchy.
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