class AstrologerPersona:

    @staticmethod
    def _intro_line(language, script):
        if language == "hi" and script == "devanagari":
            return "मैं आचार्य आर्यव्रत आपकी कुंडली देखकर कह सकता हूँ कि इस दिशा में स्पष्ट संकेत दिखाई दे रहे हैं।"

        if language == "hi" and script == "roman":
            return "Main Acharya Aryavrat aapki kundli dekh kar keh sakta hoon ki is disha mein spasht sanket dikh rahe hain."

        return "I am Acharya Aryavrat, and from your chart I can see clear indications in this direction."

    @staticmethod
    def apply_once(reply, language, script, persona_introduced):
        if persona_introduced:
            return reply, False

        intro = AstrologerPersona._intro_line(language, script)
        return f"{intro}\n\n{reply}", True
