"""
History truncation experiment for cold-start evaluation.

Evaluates models across user history length bins to measure
cold-start performance with real data instead of hardcoded values.

Usage:
    python -m src.eval.history_truncation --out results/final
"""

import argparse
import os
import numpy as np
import pandas as pd

from src.eval.metrics import ndcg_at_k
from src.models.tfidf import TfidfRecommender
from src.models.hybrid import HybridRecommender

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")


def run_history_truncation(out_dir: str = None, k: int = 10):
    """Evaluate models across user history length bins."""
    save_dir = out_dir or os.path.join(BASE_DIR, "results", "final")
    os.makedirs(save_dir, exist_ok=True)

    # Load data
    items = pd.read_csv(os.path.join(DATA_DIR, "items.csv"))
    items = items[items["item_id"].str.startswith("oulad_", na=False)]
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    train = train[train["item_id"].str.startswith("oulad_", na=False)]
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    test = test[test["item_id"].str.startswith("oulad_", na=False)]

    # Fit models
    tfidf = TfidfRecommender()
    tfidf.fit(items)

    hybrid = HybridRecommender(w_content=0.6, w_cf=0.4)
    hybrid.fit(items, train)

    item_lookup = items.set_index("item_id")

    # Count training interactions per user
    user_train_counts = train.groupby("user_id").size()

    bins = [
        (0, 0, "0"),
        (1, 5, "1-5"),
        (6, 20, "6-20"),
        (21, float("inf"), "21+"),
    ]

    results = []

    for lo, hi, label in bins:
        # Find users in this bin
        if lo == 0 and hi == 0:
            # Users in test but not in train
            test_users = set(test["user_id"].unique())
            train_users = set(train["user_id"].unique())
            bin_users = list(test_users - train_users)
        else:
            bin_users = [
                u for u in test["user_id"].unique()
                if u in user_train_counts.index
                and lo <= user_train_counts[u] <= hi
            ]

        if not bin_users:
            # No users in this bin, record zeros
            results.append({"bin": label, "n_users": 0, "model": "hybrid", "ndcg": 0.0})
            results.append({"bin": label, "n_users": 0, "model": "tfidf", "ndcg": 0.0})
            continue

        # Evaluate each model on users in this bin
        for model_name in ["hybrid", "tfidf"]:
            ndcg_scores = []

            for user_id in bin_users:
                user_test = test[test["user_id"] == user_id]
                user_train = train[train["user_id"] == user_id]

                train_items_set = set(user_train["item_id"].tolist()) if len(user_train) > 0 else set()
                relevant = [item for item in user_test["item_id"].tolist() if item not in train_items_set]

                if not relevant:
                    continue

                # Build goal text from training items
                train_items = user_train["item_id"].tolist() if len(user_train) > 0 else []
                goal_text = " ".join(
                    item_lookup.loc[iid, "title"]
                    for iid in train_items[:3]
                    if iid in item_lookup.index
                )

                if not goal_text.strip():
                    # For cold-start users, use a generic goal
                    goal_text = "learning education course"

                if model_name == "tfidf":
                    recs_df = tfidf.recommend(goal_text, k=k)
                elif model_name == "hybrid":
                    recs_df = hybrid.recommend(
                        goal=goal_text,
                        user_id=str(user_id),
                        user_interactions=user_train if len(user_train) > 0 else None,
                        k=k,
                    )

                recs = recs_df["item_id"].tolist()
                ndcg = ndcg_at_k(recs, relevant, k)
                ndcg_scores.append(ndcg)

            mean_ndcg = float(np.mean(ndcg_scores)) if ndcg_scores else 0.0
            results.append({
                "bin": label,
                "n_users": len(bin_users),
                "model": model_name,
                "ndcg": round(mean_ndcg, 4),
            })
            print(f"  Bin {label}: {model_name} NDCG@{k} = {mean_ndcg:.4f} ({len(ndcg_scores)} users evaluated)")

    df = pd.DataFrame(results)
    out_path = os.path.join(save_dir, "history_truncation.csv")
    df.to_csv(out_path, index=False)
    print(f"\nHistory truncation results saved to {out_path}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Run history truncation cold-start experiment")
    parser.add_argument("--out", default=os.path.join(BASE_DIR, "results", "final"))
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()
    run_history_truncation(out_dir=args.out, k=args.k)


if __name__ == "__main__":
    main()
