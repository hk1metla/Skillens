"""
Fairness and diversity audit for recommender evaluation.

Evaluates recommendation bias across demographic groups and item popularity.
Computes per-group accuracy, coverage, Gini inequality, and demographic parity.
"""

from typing import Dict, List, Optional, Set

import numpy as np
import pandas as pd

from src.eval.metrics import gini_coefficient, long_tail_coverage


class FairnessAuditor:
    """
    Audits fairness and diversity in recommendations.
    
    Evaluates:
    - Demographic parity (if demographic data available)
    - Long-tail coverage
    - Popularity bias
    - Gini coefficient (inequality)
    """

    def __init__(
        self,
        items: pd.DataFrame,
        interactions: pd.DataFrame,
        demographics: Optional[pd.DataFrame] = None,
    ):
        """
        Initialize fairness auditor.
        
        Args:
            items: Item metadata
            interactions: Historical interactions
            demographics: Optional student demographics DataFrame (from OULAD)
        """
        self.items = items
        self.interactions = interactions
        self.demographics = demographics
        
        # Identify popular items (top 20% by interaction count)
        item_counts = interactions["item_id"].value_counts()
        n_popular = max(1, int(len(item_counts) * 0.2))
        self.popular_items = set(item_counts.head(n_popular).index)
        self.long_tail_items = set(item_counts.tail(len(item_counts) - n_popular).index)
        
        # Load demographic groups if available
        self.demographic_groups = {}
        if demographics is not None and not demographics.empty:
            from src.data.load_demographics import get_demographic_groups
            self.demographic_groups = get_demographic_groups(demographics)

    def audit_recommendations(
        self, all_recommendations: List[List[str]]
    ) -> Dict[str, float]:
        """
        Comprehensive fairness audit of recommendations.
        
        Args:
            all_recommendations: List of recommendation lists (one per user/query)
            
        Returns:
            Dict with fairness metrics
        """
        # Flatten all recommendations
        all_rec_items = []
        for recs in all_recommendations:
            all_rec_items.extend(recs)
        
        if not all_rec_items:
            return {
                "long_tail_coverage": 0.0,
                "gini_coefficient": 0.0,
                "popularity_bias": 0.0,
            }
        
        # Count recommendations per item
        item_rec_counts = {}
        for item in all_rec_items:
            item_rec_counts[item] = item_rec_counts.get(item, 0) + 1
        
        # Long-tail coverage
        long_tail_recs = [item for item in all_rec_items if item in self.long_tail_items]
        long_tail_cov = len(set(long_tail_recs)) / len(self.long_tail_items) if self.long_tail_items else 0.0
        
        # Gini coefficient (inequality)
        gini = gini_coefficient(item_rec_counts)
        
        # Popularity bias: fraction of recommendations that are popular
        popular_recs = [item for item in all_rec_items if item in self.popular_items]
        popularity_bias = len(popular_recs) / len(all_rec_items) if all_rec_items else 0.0
        
        return {
            "long_tail_coverage": float(long_tail_cov),
            "gini_coefficient": float(gini),
            "popularity_bias": float(popularity_bias),
            "n_popular_recs": len(popular_recs),
            "n_long_tail_recs": len(set(long_tail_recs)),
            "total_recs": len(all_rec_items),
        }

    def audit_by_demographic(
        self,
        recommendations_by_group: Dict[str, List[List[str]]],
    ) -> pd.DataFrame:
        """
        Audit fairness across demographic groups.
        
        Args:
            recommendations_by_group: Dict mapping group name to list of recommendations
            
        Returns:
            DataFrame with fairness metrics per group
        """
        results = []
        
        for group_name, recs in recommendations_by_group.items():
            audit = self.audit_recommendations(recs)
            audit["group"] = group_name
            results.append(audit)
        
        return pd.DataFrame(results)

    def mitigate_popularity_bias(
        self,
        recommendations: pd.DataFrame,
        diversity_weight: float = 0.3,
    ) -> pd.DataFrame:
        """
        Rerank recommendations to reduce popularity bias.
        
        Boosts long-tail items to improve diversity.
        
        Args:
            recommendations: Original recommendations
            diversity_weight: Weight for diversity boost (0-1)
            
        Returns:
            Reranked recommendations
        """
        recommendations = recommendations.copy()
        
        # Compute diversity boost
        diversity_scores = []
        for _, row in recommendations.iterrows():
            item_id = row["item_id"]
            original_score = row["score"]
            
            # Boost long-tail items
            if item_id in self.long_tail_items:
                diversity_boost = diversity_weight
            else:
                diversity_boost = 0.0
            
            final_score = original_score + diversity_boost
            diversity_scores.append(final_score)
        
        recommendations["score"] = diversity_scores
        recommendations = recommendations.sort_values("score", ascending=False).reset_index(drop=True)
        
        return recommendations

    def compute_demographic_parity(
        self,
        recommendations_by_group: Dict[str, List[List[str]]],
    ) -> float:
        """
        Compute demographic parity: how similar are recommendations across groups.
        
        Higher values indicate more fairness (similar recommendations across groups).
        
        Args:
            recommendations_by_group: Dict mapping group to recommendations
            
        Returns:
            Demographic parity score [0, 1]
        """
        if len(recommendations_by_group) < 2:
            return 1.0  # Can't compare with one group
        
        # Compute average recommendation distribution per group
        group_distributions = {}
        
        for group_name, recs in recommendations_by_group.items():
            # Count item frequencies
            all_items = []
            for rec_list in recs:
                all_items.extend(rec_list)
            
            item_counts = {}
            for item in all_items:
                item_counts[item] = item_counts.get(item, 0) + 1
            
            # Normalize to distribution
            total = sum(item_counts.values())
            if total > 0:
                distribution = {item: count / total for item, count in item_counts.items()}
            else:
                distribution = {}
            
            group_distributions[group_name] = distribution
        
        # Compute pairwise similarity between groups
        groups = list(group_distributions.keys())
        similarities = []
        
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                dist1 = group_distributions[groups[i]]
                dist2 = group_distributions[groups[j]]
                
                # Jaccard similarity on top items
                top_items1 = set(sorted(dist1.items(), key=lambda x: x[1], reverse=True)[:10])
                top_items2 = set(sorted(dist2.items(), key=lambda x: x[1], reverse=True)[:10])
                
                if top_items1 or top_items2:
                    intersection = len(top_items1 & top_items2)
                    union = len(top_items1 | top_items2)
                    similarity = intersection / union if union > 0 else 0.0
                    similarities.append(similarity)
        
        return float(np.mean(similarities)) if similarities else 0.0
