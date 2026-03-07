from app.conversation.life_theme_detector import LifeThemeDetector
from app.conversation.astrology_reason_engine import AstrologyReasonEngine


class ConsultationEngine:

    @staticmethod
    def build_opening(chart):

        theme = LifeThemeDetector.detect(chart)

        if not theme:
            return None

        return f"Looking at your birth chart overall, a strong life focus appears around {theme}."

    @staticmethod
    def enrich_domain_response(domain_data):

        reason = AstrologyReasonEngine.build_reason(domain_data)

        return reason