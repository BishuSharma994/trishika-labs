class CrossDomainMatrix:

    @staticmethod
    def apply(domain_scores):

        finance = domain_scores["finance"]["score"]
        career = domain_scores["career"]["score"]

        marriage = domain_scores["marriage"]["score"]
        health = domain_scores["health"]["score"]

        domain_scores["finance"]["score"] = round(
            (finance * 0.85) + (career * 0.15)
        )

        domain_scores["marriage"]["score"] = round(
            (marriage * 0.90) + (health * 0.10)
        )

        domain_scores["health"]["score"] = round(
            (health * 0.90) + (marriage * 0.10)
        )

        return domain_scores