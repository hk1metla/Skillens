from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfRecommender:
    def __init__(self, max_features: int = 5000) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
        )
        self.item_ids: List[str] = []
        self.item_matrix = None

    def fit(self, items: pd.DataFrame) -> None:
        items = items.copy()
        tags = (
            items["tags"]
            if "tags" in items.columns
            else pd.Series([""] * len(items), index=items.index)
        )
        items["text"] = (
            items["title"].fillna("")
            + " "
            + items["description"].fillna("")
            + " "
            + tags.fillna("").astype(str)
        )

        self.item_ids = items["item_id"].tolist()
        self.item_matrix = self.vectorizer.fit_transform(items["text"])

    def recommend(self, goal: str, k: int = 10, exclude_items: Optional[List[str]] = None) -> pd.DataFrame:
        if self.item_matrix is None:
            raise ValueError("Model is not fitted.")

        goal_vec = self.vectorizer.transform([goal])
        scores = cosine_similarity(goal_vec, self.item_matrix).flatten()

        # Create item_id to score mapping
        item_scores = {self.item_ids[i]: float(scores[i]) for i in range(len(self.item_ids))}
        
        # Exclude specified items
        if exclude_items:
            for item in exclude_items:
                item_scores.pop(item, None)
        
        # Sort by score and return top k
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        return pd.DataFrame(
            {
                "item_id": [item for item, _ in sorted_items],
                "score": [score for _, score in sorted_items],
            }
        )

