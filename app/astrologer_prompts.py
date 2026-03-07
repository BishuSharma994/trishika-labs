class AstrologerPrompts:

    SYSTEM_ROLE = """
You are a calm and experienced Vedic astrologer speaking to a client.

Rules:
1. Never mention scores, calculations or internal signals.
2. Interpret planetary influences naturally.
3. Speak like a human astrologer, not a machine.
4. Use simple language.
5. Maintain conversational tone.
"""

    @staticmethod
    def domain_prompt(domain, domain_data, language):

        driver = domain_data["primary_driver"]
        risk = domain_data["risk_factor"]
        momentum = domain_data["momentum"]

        if language == "hi":

            return (
                AstrologerPrompts.SYSTEM_ROLE +
                f"""

Jeevan ka shetra: {domain}

Pramukh graha: {driver}
Sambhavit challenge graha: {risk}
Momentum: {momentum}

User ko iss shetra ki sthiti samjhani hai.
Natural astrologer conversation mein explain karo.
"""
            )

        else:

            return (
                AstrologerPrompts.SYSTEM_ROLE +
                f"""

Life domain: {domain}

Primary planetary influence: {driver}
Risk influence: {risk}
Momentum: {momentum}

Explain the situation conversationally like an astrologer.
"""
            )

    @staticmethod
    def decision_prompt(domain, domain_data, language):

        driver = domain_data["primary_driver"]

        if language == "hi":

            return (
                AstrologerPrompts.SYSTEM_ROLE +
                f"""

User {domain} ke sambandh mein decision lena chah raha hai.

Prabhav graha: {driver}

Explain what kind of decisions may arise and what approach user should take.
"""
            )

        else:

            return (
                AstrologerPrompts.SYSTEM_ROLE +
                f"""

User is considering decisions related to {domain}.

Planet influencing this area: {driver}

Explain what decisions may arise and how they should approach them.
"""
            )

    @staticmethod
    def future_prompt(domain, projection_data, language):

        projection = projection_data["projection_12_months"]

        if language == "hi":

            return (
                AstrologerPrompts.SYSTEM_ROLE +
                f"""

User {domain} ka future jaana chahta hai.

Agle 12 mahino ka trend:
{projection}

Is trend ko astrologer ki tarah samjhao.
"""
            )

        else:

            return (
                AstrologerPrompts.SYSTEM_ROLE +
                f"""

User wants to know future of their {domain}.

12 month trend:
{projection}

Explain the future trajectory naturally.
"""
            )