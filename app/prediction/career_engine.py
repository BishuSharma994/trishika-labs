from app.prediction.projection_engine import ProjectionEngine


class CareerEngine:

    @staticmethod
    def analyze(domain_data):

        score = domain_data["score"]
        momentum = domain_data["momentum"]

        projection = ProjectionEngine.yearly_projection(score, momentum)

        return {
            "current_score": score,
            "projection_12_months": projection,
            "trend": "improving" if projection[-1] > score else "stable"
        }