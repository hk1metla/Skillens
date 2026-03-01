"""
SHAP-based Attribution Explanations.

Provides feature-level explanations for hybrid recommendations,
showing which features contributed most to each recommendation.

This addresses Explainability: Advanced attribution-based explanations
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import shap


class SHAPExplainer:
    """
    SHAP explainer for hybrid recommender models.
    
    Provides feature attribution to explain why items were recommended.
    """

    def __init__(self, model, feature_names: List[str]):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model (LightGBM or similar)
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = None

    def fit_explainer(self, background_data: np.ndarray) -> None:
        """
        Fit SHAP explainer on background data.
        
        Args:
            background_data: Background dataset for SHAP (sample of items)
        """
        # Use TreeExplainer for tree-based models (LightGBM)
        if hasattr(self.model, "predict"):
            self.explainer = shap.TreeExplainer(self.model)
        else:
            # Fallback to KernelExplainer for other models
            self.explainer = shap.KernelExplainer(
                self.model.predict,
                background_data[:100]  # Sample for efficiency
            )

    def explain_recommendation(
        self,
        item_features: np.ndarray,
        top_n_features: int = 5,
    ) -> Dict[str, float]:
        """
        Explain a single recommendation.
        
        Args:
            item_features: Feature vector for the item
            top_n_features: Number of top features to return
            
        Returns:
            Dict mapping feature names to SHAP values
        """
        if self.explainer is None:
            raise ValueError("Explainer is not fitted. Call fit_explainer() first.")
        
        # Compute SHAP values
        shap_values = self.explainer.shap_values(item_features.reshape(1, -1))
        
        # Handle multi-output case
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Get feature contributions
        feature_contributions = {}
        for i, feature_name in enumerate(self.feature_names):
            if i < len(shap_values[0]):
                feature_contributions[feature_name] = float(shap_values[0][i])
        
        # Sort by absolute value and return top N
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:top_n_features]
        
        return dict(sorted_features)

    def explain_batch(
        self,
        item_features_list: List[np.ndarray],
        top_n_features: int = 5,
    ) -> List[Dict[str, float]]:
        """
        Explain multiple recommendations at once (more efficient).
        
        Args:
            item_features_list: List of feature vectors
            top_n_features: Number of top features per item
            
        Returns:
            List of explanation dicts
        """
        if self.explainer is None:
            raise ValueError("Explainer is not fitted. Call fit_explainer() first.")
        
        # Stack features
        X = np.vstack(item_features_list)
        
        # Compute SHAP values for all items
        shap_values = self.explainer.shap_values(X)
        
        # Handle multi-output case
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        explanations = []
        for item_shap in shap_values:
            feature_contributions = {}
            for i, feature_name in enumerate(self.feature_names):
                if i < len(item_shap):
                    feature_contributions[feature_name] = float(item_shap[i])
            
            # Sort and get top N
            sorted_features = sorted(
                feature_contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:top_n_features]
            
            explanations.append(dict(sorted_features))
        
        return explanations

    def format_explanation(
        self,
        explanation: Dict[str, float],
        include_values: bool = True,
    ) -> str:
        """
        Format SHAP explanation as human-readable text.
        
        Args:
            explanation: Dict of feature -> SHAP value
            include_values: Whether to include numerical values
            
        Returns:
            Formatted explanation string
        """
        if not explanation:
            return "No explanation available."
        
        parts = []
        for feature, value in explanation.items():
            # Format feature name (remove underscores, capitalize)
            feature_name = feature.replace("_", " ").title()
            
            if include_values:
                parts.append(f"{feature_name} ({value:+.3f})")
            else:
                direction = "positively" if value > 0 else "negatively"
                parts.append(f"{feature_name} contributed {direction}")
        
        return "This recommendation is driven by: " + ", ".join(parts) + "."
