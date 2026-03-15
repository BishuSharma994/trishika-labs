class AstrologerPersona:

    @staticmethod
    def _intro_line(language, script):
        if language == "hi" and script == "roman":
            return "Namaste, main Hemant hoon. Aapki kundli dekh kar is disha mein kuchh spasht sanket dikh rahe hain."

        return "Hi, I'm Arjun. From your chart, I can see clear indications in this direction."

    @staticmethod
    def apply_once(reply, language, script, persona_introduced):
        if persona_introduced:
            return reply, False

        intro = AstrologerPersona._intro_line(language, script)
        return f"{intro}\n\n{reply}", True
