from app.conversation.life_theme_detector import LifeThemeDetector


class ConsultationEngine:

    @staticmethod
    def build_opening(chart, language, script):

        theme = LifeThemeDetector.detect(chart)

        if not theme:
            return None

        if language == "hi" and script == "devanagari":
            return f"आपकी कुंडली देखने पर जीवन का मुख्य फोकस {theme} से जुड़ा दिखाई देता है।"

        if language == "hi" and script == "roman":
            return f"Aapki kundli dekhne par jeevan ka mukhya focus {theme} par dikh raha hai."

        return f"Looking at your birth chart overall, a strong life focus appears around {theme}."