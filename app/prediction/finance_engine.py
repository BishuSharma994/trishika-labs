from app.prediction.projection_engine import ProjectionEngine


class FinanceEngine:

    @staticmethod
    def analyze(domain_data):

        score = domain_data["score"]
        momentum = domain_data["momentum"]

        projection = ProjectionEngine.yearly_projection(score, momentum)

        volatility = abs(projection[-1] - projection[0])

        return {
            "current_score": score,
            "projection_12_months": projection,
            "volatility_index": volatility
        }