import argparse
import os
from typing import Dict

import pandas as pd
import yaml

from src.eval.metrics import ndcg_at_k, precision_at_k, recall_at_k
from src.models.popularity import PopularityRecommender
from src.models.tfidf import TfidfRecommender


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def _load_items() -> pd.DataFrame:
    """
    Load items and filter to OULAD-only for evaluation.
    
    Per dual-dataset strategy: OULAD is PRIMARY for all evaluation.
    Coursera items are excluded from evaluation (used for demo UI only).
    """
    items = pd.read_csv(os.path.join(DATA_DIR, "items.csv"))
    # Filter to OULAD items only (item_id starts with "oulad_")
    oulad_items = items[items["item_id"].str.startswith("oulad_", na=False)]
    if len(oulad_items) == 0:
        print("WARNING: No OULAD items found! Falling back to all items.")
        return items
    return oulad_items


def _load_split(name: str) -> pd.DataFrame:
    """
    Load train/val/test split and filter to OULAD-only interactions.
    
    Per dual-dataset strategy: All evaluation uses OULAD data only.
    """
    split_df = pd.read_csv(os.path.join(DATA_DIR, f"{name}.csv"))
    # Filter to OULAD interactions only (item_id starts with "oulad_")
    oulad_split = split_df[split_df["item_id"].str.startswith("oulad_", na=False)]
    if len(oulad_split) == 0:
        print(f"WARNING: No OULAD interactions in {name} split! Falling back to all interactions.")
        return split_df
    return oulad_split


def _evaluate_popularity(
    model: PopularityRecommender, test_df: pd.DataFrame, k: int
) -> Dict[str, float]:
    metrics = {"precision": [], "recall": [], "ndcg": []}

    for user_id, user_df in test_df.groupby("user_id"):
        relevant = user_df["item_id"].tolist()
        recs = model.recommend(k=k)["item_id"].tolist()
        metrics["precision"].append(precision_at_k(recs, relevant, k))
        metrics["recall"].append(recall_at_k(recs, relevant, k))
        metrics["ndcg"].append(ndcg_at_k(recs, relevant, k))

    return {key: float(pd.Series(vals).mean()) for key, vals in metrics.items()}


def _evaluate_tfidf(
    model: TfidfRecommender,
    items: pd.DataFrame,
    test_df: pd.DataFrame,
    train_df: pd.DataFrame,
    k: int,
) -> Dict[str, float]:
    """
    Evaluate TF-IDF model using training data to build queries.
    
    CRITICAL FIX: Build queries from train_df (user's training history),
    not test_df, to avoid data leakage. Then evaluate on held-out test items.
    """
    metrics = {"precision": [], "recall": [], "ndcg": []}
    item_lookup = items.set_index("item_id")

    for user_id, user_df in test_df.groupby("user_id"):
        relevant = user_df["item_id"].tolist()  # Test items (held-out)
        
        # FIX: Build query from TRAIN history, not test items
        user_train = train_df[train_df["user_id"] == user_id]
        if len(user_train) == 0:
            # Skip cold-start users (no training history for TF-IDF)
            continue
        
        # Use training items to build goal text
        train_items = user_train["item_id"].tolist()
        goal_text = " ".join(
            item_lookup.loc[item_id, "title"]
            for item_id in train_items[:3]
            if item_id in item_lookup.index
        )
        
        if not goal_text.strip():
            continue
        
        # Get recommendations based on training history
        # Note: In temporal splits, users may interact with same items at different times.
        # We don't exclude training items because they may legitimately appear in test.
        recs = model.recommend(goal_text, k=k)["item_id"].tolist()
        
        # Evaluate against held-out test items
        metrics["precision"].append(precision_at_k(recs, relevant, k))
        metrics["recall"].append(recall_at_k(recs, relevant, k))
        metrics["ndcg"].append(ndcg_at_k(recs, relevant, k))

    return {key: float(pd.Series(vals).mean()) for key, vals in metrics.items()}


def run(config_path: str) -> pd.DataFrame:
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    k = config["eval"]["k"]

    items = _load_items()
    train_df = _load_split("train")
    test_df = _load_split("test")

    popularity = PopularityRecommender()
    popularity.fit(train_df)
    pop_metrics = _evaluate_popularity(popularity, test_df, k)

    tfidf = TfidfRecommender()
    tfidf.fit(items)
    tfidf_metrics = _evaluate_tfidf(tfidf, items, test_df, train_df, k)

    results = pd.DataFrame(
        [
            {"model": "popularity", **pop_metrics},
            {"model": "tfidf", **tfidf_metrics},
        ]
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    results.to_csv(os.path.join(RESULTS_DIR, "metrics.csv"), index=False)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiment.yaml")
    args = parser.parse_args()
    run(args.config)

