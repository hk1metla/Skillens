"""
ItemKNN Collaborative Filtering Recommender.

Uses item-item similarity based on user interaction patterns.
This is a key component for the hybrid recommender system.
"""

from typing import List, Optional

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


class ItemKNNRecommender:
    """
    Item-based Collaborative Filtering using K-Nearest Neighbors.
    
    For each item, finds similar items based on user interaction patterns,
    then recommends items similar to those the user has interacted with.
    """

    def __init__(self, k: int = 50, min_interactions: int = 2):
        """
        Initialize ItemKNN recommender.
        
        Args:
            k: Number of nearest neighbors to consider
            min_interactions: Minimum interactions required for an item to be considered
        """
        self.k = k
        self.min_interactions = min_interactions
        self.item_similarity_matrix = None
        self.item_ids = None
        self.user_item_matrix = None
        self.item_to_idx = None
        self.idx_to_item = None

    def fit(self, interactions: pd.DataFrame) -> None:
        """
        Fit the ItemKNN model on interaction data.
        
        Args:
            interactions: DataFrame with columns ['user_id', 'item_id', 'timestamp']
        """
        # Create user-item interaction matrix
        users = interactions["user_id"].unique()
        items = interactions["item_id"].unique()
        
        self.item_ids = sorted(items)
        self.item_to_idx = {item: idx for idx, item in enumerate(self.item_ids)}
        self.idx_to_item = {idx: item for item, idx in self.item_to_idx.items()}
        
        user_to_idx = {user: idx for idx, user in enumerate(users)}
        
        # Build sparse matrix (users x items)
        rows = []
        cols = []
        data = []
        
        for _, row in interactions.iterrows():
            user_idx = user_to_idx[row["user_id"]]
            item_idx = self.item_to_idx[row["item_id"]]
            rows.append(user_idx)
            cols.append(item_idx)
            data.append(1.0)  # Binary implicit feedback
        
        self.user_item_matrix = csr_matrix(
            (data, (rows, cols)), shape=(len(users), len(self.item_ids))
        )
        
        # Compute item-item similarity matrix
        # Transpose to get items x users, then compute cosine similarity
        item_user_matrix = self.user_item_matrix.T
        
        # Filter items with too few interactions
        item_counts = np.array(item_user_matrix.sum(axis=1)).flatten()
        valid_items = item_counts >= self.min_interactions
        
        if valid_items.sum() == 0:
            raise ValueError("No items meet minimum interaction threshold")
        
        # Compute cosine similarity between items
        self.item_similarity_matrix = cosine_similarity(item_user_matrix)
        
        # Set diagonal to 0 (items are not similar to themselves)
        np.fill_diagonal(self.item_similarity_matrix, 0)

    def recommend(
        self,
        user_id: str,
        interactions: pd.DataFrame,
        k: int = 10,
        exclude_items: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Generate recommendations for a user.
        
        Args:
            user_id: User ID to recommend for
            interactions: User's historical interactions
            k: Number of recommendations to return
            exclude_items: Item IDs to exclude from recommendations
            
        Returns:
            DataFrame with columns ['item_id', 'score']
        """
        if self.item_similarity_matrix is None:
            raise ValueError("Model is not fitted.")
        
        # Get items the user has interacted with
        user_items = set(interactions[interactions["user_id"] == user_id]["item_id"])
        
        if not user_items:
            # Cold-start: return empty recommendations
            return pd.DataFrame({"item_id": [], "score": []})
        
        # Convert user items to indices
        user_item_indices = [
            self.item_to_idx[item] for item in user_items if item in self.item_to_idx
        ]
        
        if not user_item_indices:
            return pd.DataFrame({"item_id": [], "score": []})
        
        # Aggregate similarity scores from all user's items
        # For each candidate item, sum similarities to all user's items
        item_scores = np.zeros(len(self.item_ids))
        
        for user_item_idx in user_item_indices:
            # Get similarities to this item
            similarities = self.item_similarity_matrix[user_item_idx, :]
            item_scores += similarities
        
        # Normalize by number of user items (average similarity)
        item_scores = item_scores / len(user_item_indices)
        
        # Convert to item IDs and create DataFrame
        item_scores_dict = {
            self.idx_to_item[idx]: float(score)
            for idx, score in enumerate(item_scores)
        }
        
        # Exclude items user has already interacted with
        for item in user_items:
            item_scores_dict.pop(item, None)
        
        # Exclude specified items
        if exclude_items:
            for item in exclude_items:
                item_scores_dict.pop(item, None)
        
        # Sort by score and return top k
        sorted_items = sorted(
            item_scores_dict.items(), key=lambda x: x[1], reverse=True
        )[:k]
        
        return pd.DataFrame(
            {"item_id": [item for item, _ in sorted_items], "score": [score for _, score in sorted_items]}
        )

    def recommend_for_new_user(
        self, goal_items: List[str], k: int = 10
    ) -> pd.DataFrame:
        """
        Recommend for a new user based on goal items (cold-start).
        
        Args:
            goal_items: List of item IDs that match user's goal
            k: Number of recommendations to return
            
        Returns:
            DataFrame with columns ['item_id', 'score']
        """
        if self.item_similarity_matrix is None:
            raise ValueError("Model is not fitted.")
        
        if not goal_items:
            return pd.DataFrame({"item_id": [], "score": []})
        
        # Get indices for goal items
        goal_indices = [
            self.item_to_idx[item]
            for item in goal_items
            if item in self.item_to_idx
        ]
        
        if not goal_indices:
            return pd.DataFrame({"item_id": [], "score": []})
        
        # Aggregate similarities
        item_scores = np.zeros(len(self.item_ids))
        for goal_idx in goal_indices:
            similarities = self.item_similarity_matrix[goal_idx, :]
            item_scores += similarities
        
        item_scores = item_scores / len(goal_indices)
        
        # Convert to DataFrame
        item_scores_dict = {
            self.idx_to_item[idx]: float(score)
            for idx, score in enumerate(item_scores)
        }
        
        # Exclude goal items
        for item in goal_items:
            item_scores_dict.pop(item, None)
        
        sorted_items = sorted(
            item_scores_dict.items(), key=lambda x: x[1], reverse=True
        )[:k]
        
        return pd.DataFrame(
            {"item_id": [item for item, _ in sorted_items], "score": [score for _, score in sorted_items]}
        )
