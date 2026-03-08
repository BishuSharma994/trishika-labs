class AstrologyResponseTemplate:

    @staticmethod
    def _clean(text):
        return (text or "").strip()

    @staticmethod
    def build_response(consultation_payload):
        payload = consultation_payload or {}

        observation = AstrologyResponseTemplate._clean(payload.get("observation", ""))
        reasoning = AstrologyResponseTemplate._clean(payload.get("planetary_reasoning", ""))
        timing = AstrologyResponseTemplate._clean(payload.get("timing_interpretation", ""))
        advice = AstrologyResponseTemplate._clean(payload.get("practical_advice", ""))
        followup = AstrologyResponseTemplate._clean(payload.get("followup_question", ""))

        parts = []

        if observation:
            parts.append(observation)
        if reasoning:
            parts.append(reasoning)
        if timing:
            parts.append(timing)
        if advice:
            parts.append(advice)
        if followup:
            parts.append(followup)

        return "\n\n".join(parts).strip()
