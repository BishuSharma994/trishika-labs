class ProjectionEngine:

    @staticmethod
    def yearly_projection(base_score, momentum):

        trajectory = []

        adjustment = 0

        if momentum == "Positive":
            adjustment = 2

        elif momentum == "Challenging":
            adjustment = -1

        score = base_score

        for month in range(12):

            score = max(0, min(100, score + adjustment))
            trajectory.append(score)

        return trajectory