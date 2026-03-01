from typing import List, Optional

import pandas as pd


class PopularityRecommender:
    def __init__(self) -> None:
        self._ranking: Optional[pd.Series] = None

    def fit(self, interactions: pd.DataFrame) -> None:
        counts = (
            interactions["item_id"]
            .value_counts()
            .rename("popularity")
            .reset_index()
            .rename(columns={"index": "item_id"})
        )
        self._ranking = counts.set_index("item_id")["popularity"]

    def recommend(
        self,
        k: int = 10,
        exclude_items: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        if self._ranking is None:
            raise ValueError("Model is not fitted.")

        ranking = self._ranking.copy()
        if exclude_items:
            ranking = ranking.drop(exclude_items, errors="ignore")

        top = ranking.sort_values(ascending=False).head(k)
        return top.reset_index().rename(columns={0: "popularity"})

