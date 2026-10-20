"""
Evaluation Engine – Weighted Sum Model (WSM)

Formula:
    S(Aᵢ) = Σⱼ [ wⱼ_norm × rᵢⱼ ]  ×  10

where:
    S(Aᵢ)     = final WSM score for framework i  (0–100)
    wⱼ_norm   = normalized weight of criterion j  (sums to 1)
    rᵢⱼ       = raw score of framework i on criterion j (1–10)
"""

from data import EA_FRAMEWORKS


class EvaluationEngine:
    """
    Core decision-support engine.

    Parameters
    ----------
    frameworks : list[str]
        Names of EA frameworks to evaluate (must exist in EA_FRAMEWORKS).
    criteria : dict
        Criteria metadata dict (from data.py DEFAULT_CRITERIA).
    weights : dict
        User-defined weights {criterion_key: int(0–10)}.
    """

    def __init__(self, frameworks: list, criteria: dict, weights: dict):
        self.frameworks = frameworks
        self.criteria = criteria
        self.weights = weights

    
    def _normalize_weights(self) -> dict:
        total = sum(self.weights.get(c, 0) for c in self.criteria)
        if total == 0:
            n = len(self.criteria)
            return {c: 1 / n for c in self.criteria}
        return {c: self.weights.get(c, 0) / total for c in self.criteria}

    
    def evaluate(self) -> dict:
        """
        Run WSM evaluation.

        Returns
        -------
        dict  { framework_name: {
                    "final_score": float,          # 0–100
                    "raw_scores": {crit: float},   # 1–10
                    "weighted_scores": {crit: float},
                    "top_criteria": [str, ...],
               }}
        """
        norm_weights = self._normalize_weights()
        results = {}

        for fw in self.frameworks:
            fw_data = EA_FRAMEWORKS[fw]
            raw_scores = {}
            weighted_scores = {}

            for crit in self.criteria:
                raw = fw_data.get(crit, 5)          
                raw_scores[crit] = raw
                weighted_scores[crit] = norm_weights[crit] * raw * 10  

            final_score = sum(weighted_scores.values())

            
            top = sorted(weighted_scores, key=weighted_scores.get, reverse=True)
            top_labels = [self.criteria[c]["label"] for c in top[:3]]

            results[fw] = {
                "final_score": final_score,
                "raw_scores": raw_scores,
                "weighted_scores": weighted_scores,
                "top_criteria": top_labels,
                "norm_weights": norm_weights,
            }

        return results


    def sensitivity(self, target_criterion: str, steps: int = 11) -> dict:
        """
        Vary a single criterion weight from 0→10 and return scores.

        Returns
        -------
        dict  { weight_value: {fw: score, ...} }
        """
        sensitivity_results = {}
        for w_val in range(0, steps + 1):
            modified_weights = dict(self.weights)
            modified_weights[target_criterion] = w_val
            engine = EvaluationEngine(self.frameworks, self.criteria, modified_weights)
            res = engine.evaluate()
            sensitivity_results[w_val] = {fw: res[fw]["final_score"] for fw in self.frameworks}
        return sensitivity_results
