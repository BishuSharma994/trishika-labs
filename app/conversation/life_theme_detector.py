class LifeThemeDetector:

    @staticmethod
    def detect(chart):

        scores = chart.get("domain_scores", {})

        dominant = None
        best_score = -1

        for domain, data in scores.items():

            s = data.get("score", 0)

            if s > best_score:
                best_score = s
                dominant = domain

        return dominant