"""
Pedagogical-aware ranking module.

Optimises for learning progression rather than just engagement by modelling
learner skill gaps and re-ranking items to prioritise those teaching
unmastered skills.
"""

from typing import Dict, List, Optional, Set

import pandas as pd


class PedagogicalRanker:
    """
    Pedagogical-aware reranker that optimizes for learning progression.
    
    Key innovation: Instead of just maximizing engagement, we optimize
    for teaching skills the learner hasn't mastered yet.
    """

    def __init__(self, skill_threshold: float = 0.7):
        """
        Initialize pedagogical ranker.
        
        Args:
            skill_threshold: Minimum interaction score to consider a skill "mastered"
        """
        self.skill_threshold = skill_threshold
        self.item_skills: Dict[str, Set[str]] = {}
        self.user_skills: Dict[str, Dict[str, float]] = {}

    def extract_skills_from_items(self, items: pd.DataFrame) -> None:
        """
        Extract skills from item metadata.
        
        In a real implementation, this would use NLP to extract skills from
        descriptions, or use structured skill tags. For now, we use a heuristic
        based on keywords in titles/descriptions.
        
        Args:
            items: Item metadata DataFrame
        """
        # Simple keyword-based skill extraction
        # In production, this would use NLP or structured skill ontologies
        skill_keywords = {
            "python": {"programming", "python", "coding"},
            "machine_learning": {"machine learning", "ml", "ai", "neural"},
            "data_science": {"data", "analytics", "statistics", "analysis"},
            "web_development": {"web", "html", "css", "javascript", "frontend"},
            "databases": {"database", "sql", "nosql", "data storage"},
            "cloud": {"cloud", "aws", "azure", "gcp", "infrastructure"},
            "business": {"business", "management", "strategy", "leadership"},
        }
        
        items = items.copy()
        items["text"] = (
            items["title"].fillna("").str.lower()
            + " "
            + items["description"].fillna("").str.lower()
        )
        
        for _, row in items.iterrows():
            item_id = row["item_id"]
            text = row["text"]
            skills = set()
            
            for skill_name, keywords in skill_keywords.items():
                if any(keyword in text for keyword in keywords):
                    skills.add(skill_name)
            
            self.item_skills[item_id] = skills

    def model_user_skills(
        self, user_id: str, interactions: pd.DataFrame, items: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Model user's skill mastery from interaction history.
        
        Skills are weighted by interaction strength and recency.
        
        Args:
            user_id: User ID
            interactions: User's interaction history
            items: Item metadata
            
        Returns:
            Dict mapping skill to mastery score [0, 1]
        """
        user_interactions = interactions[interactions["user_id"] == user_id]
        
        if len(user_interactions) == 0:
            return {}
        
        skill_scores: Dict[str, List[float]] = {}
        
        for _, interaction in user_interactions.iterrows():
            item_id = interaction["item_id"]
            if item_id not in self.item_skills:
                continue
            
            # Interaction strength (could be based on completion, time spent, etc.)
            # For now, assume binary: 1.0 for any interaction
            interaction_strength = 1.0
            
            # Get skills taught by this item
            item_skills = self.item_skills.get(item_id, set())
            
            for skill in item_skills:
                if skill not in skill_scores:
                    skill_scores[skill] = []
                skill_scores[skill].append(interaction_strength)
        
        # Aggregate skill mastery (average interaction strength)
        user_skill_mastery = {
            skill: sum(scores) / len(scores) if scores else 0.0
            for skill, scores in skill_scores.items()
        }
        
        return user_skill_mastery

    def rerank_for_learning(
        self,
        recommendations: pd.DataFrame,
        user_skill_mastery: Dict[str, float],
        items: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Rerank recommendations to prioritize items teaching unmastered skills.
        
        This is the core innovation: we boost items that teach skills
        the user hasn't mastered yet.
        
        Args:
            recommendations: Original recommendations with 'item_id' and 'score'
            user_skill_mastery: User's current skill mastery levels
            items: Item metadata
            
        Returns:
            Reranked recommendations with pedagogical boost applied
        """
        if len(recommendations) == 0:
            return recommendations
        
        # Compute pedagogical boost for each item
        pedagogical_scores = []
        
        for _, row in recommendations.iterrows():
            item_id = row["item_id"]
            original_score = row["score"]
            
            # Get skills taught by this item
            item_skills = self.item_skills.get(item_id, set())
            
            if not item_skills:
                # No skills identified: no boost
                pedagogical_scores.append(original_score)
                continue
            
            # Compute skill gap score
            # Higher for skills the user hasn't mastered
            skill_gap_score = 0.0
            for skill in item_skills:
                user_mastery = user_skill_mastery.get(skill, 0.0)
                # Gap = 1 - mastery (higher gap = more valuable to learn)
                skill_gap = 1.0 - user_mastery
                skill_gap_score += skill_gap
            
            # Average gap across skills
            avg_gap = skill_gap_score / len(item_skills) if item_skills else 0.0
            
            # Combine original score with pedagogical boost
            # Weight: 70% original, 30% pedagogical
            pedagogical_boost = 0.3 * avg_gap
            final_score = original_score + pedagogical_boost
            
            pedagogical_scores.append(final_score)
        
        # Update scores and rerank
        recommendations = recommendations.copy()
        recommendations["score"] = pedagogical_scores
        recommendations = recommendations.sort_values("score", ascending=False).reset_index(drop=True)
        
        return recommendations

    def compute_prerequisite_violation_rate(
        self,
        recommendations: pd.DataFrame,
        user_skill_mastery: Dict[str, float],
    ) -> float:
        """
        Measure how often recommendations violate prerequisites.
        
        Lower is better. This metric validates pedagogical quality.
        
        Args:
            recommendations: Recommended items
            user_skill_mastery: User's skill mastery
            
        Returns:
            Prerequisite violation rate [0, 1]
        """
        if len(recommendations) == 0:
            return 0.0
        
        violations = 0
        total = 0
        
        # Simple heuristic: if item requires a skill user hasn't mastered,
        # and user has no related skills, it's a violation
        for _, row in recommendations.iterrows():
            item_id = row["item_id"]
            item_skills = self.item_skills.get(item_id, set())
            
            if not item_skills:
                continue
            
            total += 1
            # Check if user has any related skills
            has_related_skill = any(
                skill in user_skill_mastery and user_skill_mastery[skill] > 0.3
                for skill in item_skills
            )
            
            if not has_related_skill and len(user_skill_mastery) > 0:
                # User has some skills but none related to this item
                violations += 1
        
        return violations / total if total > 0 else 0.0

    def compute_skill_coverage(
        self,
        recommendations: pd.DataFrame,
        user_skill_mastery: Dict[str, float],
    ) -> float:
        """
        Measure how well recommendations cover unmastered skills.
        
        Higher is better. Measures pedagogical value.
        
        Args:
            recommendations: Recommended items
            user_skill_mastery: User's skill mastery
            
        Returns:
            Skill coverage score [0, 1]
        """
        if len(recommendations) == 0:
            return 0.0
        
        # Get all unmastered skills
        unmastered_skills = {
            skill
            for skill, mastery in user_skill_mastery.items()
            if mastery < self.skill_threshold
        }
        
        if not unmastered_skills:
            # User has mastered all skills: perfect coverage
            return 1.0
        
        # Get skills covered by recommendations
        covered_skills = set()
        for _, row in recommendations.iterrows():
            item_id = row["item_id"]
            item_skills = self.item_skills.get(item_id, set())
            covered_skills.update(item_skills)
        
        # Coverage = fraction of unmastered skills that are covered
        covered_unmastered = covered_skills & unmastered_skills
        coverage = len(covered_unmastered) / len(unmastered_skills)
        
        return coverage
