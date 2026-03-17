"""
Learning-to-Rank (LTR) using LightGBM LambdaMART.

Learns optimal feature combinations for ranking using gradient boosted
decision trees with a lambdarank objective, going beyond fixed-weight fusion.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split


class LearningToRankRecommender:
    """
    Learning-to-Rank recommender using LambdaMART.
    
    Learns optimal feature combinations for ranking items,
    rather than using fixed weights.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.05,
        max_depth: int = 7,
        random_seed: int = 42,
    ):
        """
        Initialize LTR model.
        
        Args:
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate
            max_depth: Maximum tree depth
            random_seed: Random seed for reproducibility
        """
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_seed = random_seed
        self.model = None
        self.feature_names = None

    def _extract_features(
        self,
        item_id: str,
        content_score: float,
        cf_score: float,
        popularity_score: float,
        diversity_score: float,
        novelty_score: float,
        item_metadata: Optional[Dict] = None,
    ) -> np.ndarray:
        """
        Extract features for LTR model.
        
        Args:
            item_id: Item ID
            content_score: Content-based similarity score
            cf_score: Collaborative filtering score
            popularity_score: Popularity score
            diversity_score: Diversity score
            novelty_score: Novelty score
            item_metadata: Optional item metadata
            
        Returns:
            Feature vector
        """
        features = [
            content_score,
            cf_score,
            popularity_score,
            diversity_score,
            novelty_score,
            # Interaction features
            content_score * cf_score,  # Interaction
            content_score * popularity_score,
            # Normalized features
            content_score / (popularity_score + 1e-10),
            cf_score / (popularity_score + 1e-10),
        ]
        
        if item_metadata:
            # Add metadata features if available
            features.append(item_metadata.get("difficulty_level", 0.5))
            features.append(item_metadata.get("estimated_duration", 0.0))
        
        return np.array(features)

    def fit(
        self,
        training_data: List[Dict],
        validation_data: Optional[List[Dict]] = None,
    ) -> None:
        """
        Train LTR model on ranking data.
        
        Args:
            training_data: List of training examples, each with:
                - 'query_id': Query/user ID
                - 'item_id': Item ID
                - 'features': Feature vector
                - 'relevance': Relevance label (0 or 1)
            validation_data: Optional validation data
        """
        # Convert to DataFrame for easier handling
        train_df = pd.DataFrame(training_data)
        
        # Group by query
        query_groups = train_df.groupby("query_id")
        
        # Prepare data for LightGBM
        X_train = []
        y_train = []
        query_groups_train = []
        
        for query_id, group in query_groups:
            features = np.vstack(group["features"].values)
            relevance = group["relevance"].values
            
            X_train.append(features)
            y_train.append(relevance)
            query_groups_train.append(len(group))
        
        X_train = np.vstack(X_train)
        y_train = np.hstack(y_train)
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(
            X_train,
            label=y_train,
            group=query_groups_train,
        )
        
        # Validation data
        valid_sets = [train_data]
        if validation_data:
            val_df = pd.DataFrame(validation_data)
            val_query_groups = val_df.groupby("query_id")
            
            X_val = []
            y_val = []
            query_groups_val = []
            
            for query_id, group in val_query_groups:
                features = np.vstack(group["features"].values)
                relevance = group["relevance"].values
                
                X_val.append(features)
                y_val.append(relevance)
                query_groups_val.append(len(group))
            
            X_val = np.vstack(X_val)
            y_val = np.hstack(y_val)
            
            val_data = lgb.Dataset(
                X_val,
                label=y_val,
                group=query_groups_val,
            )
            valid_sets.append(val_data)
        
        # Train model
        params = {
            "objective": "lambdarank",
            "metric": "ndcg",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": self.learning_rate,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "random_state": self.random_seed,
        }
        
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=self.n_estimators,
            valid_sets=valid_sets,
            callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)],
        )
        
        # Store feature names
        self.feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]

    def predict(
        self,
        query_id: str,
        candidate_items: List[Dict],
    ) -> pd.DataFrame:
        """
        Predict relevance scores for candidate items.
        
        Args:
            query_id: Query/user ID
            candidate_items: List of candidate items with features
            
        Returns:
            DataFrame with item_id and score, sorted by score
        """
        if self.model is None:
            raise ValueError("Model is not fitted.")
        
        # Extract features
        features_list = []
        item_ids = []
        
        for item in candidate_items:
            item_ids.append(item["item_id"])
            if isinstance(item["features"], np.ndarray):
                features_list.append(item["features"])
            else:
                features_list.append(np.array(item["features"]))
        
        X = np.vstack(features_list)
        
        # Predict
        scores = self.model.predict(X)
        
        # Create results DataFrame
        results = pd.DataFrame({
            "item_id": item_ids,
            "score": scores,
        })
        
        return results.sort_values("score", ascending=False).reset_index(drop=True)
