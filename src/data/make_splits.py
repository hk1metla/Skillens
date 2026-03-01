import os
from typing import Dict, Tuple

import numpy as np
import pandas as pd


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INTERACTIONS_PATH = os.path.join(BASE_DIR, "data", "processed", "interactions.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")


def _split_user_history(
    user_df: pd.DataFrame, train_ratio: float, val_ratio: float
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    user_df = user_df.sort_values("timestamp")
    n = len(user_df)

    if n < 3:
        return user_df, user_df.iloc[0:0], user_df.iloc[0:0]

    train_end = int(np.floor(n * train_ratio))
    val_end = int(np.floor(n * (train_ratio + val_ratio)))

    train = user_df.iloc[:train_end]
    val = user_df.iloc[train_end:val_end]
    test = user_df.iloc[val_end:]
    return train, val, test


def make_splits(
    train_ratio: float = 0.6, val_ratio: float = 0.2
) -> Dict[str, pd.DataFrame]:
    interactions = pd.read_csv(INTERACTIONS_PATH)
    interactions = interactions.sort_values(["user_id", "timestamp"])

    train_rows = []
    val_rows = []
    test_rows = []

    for _, user_df in interactions.groupby("user_id"):
        train, val, test = _split_user_history(user_df, train_ratio, val_ratio)
        train_rows.append(train)
        val_rows.append(val)
        test_rows.append(test)

    splits = {
        "train": pd.concat(train_rows, ignore_index=True),
        "val": pd.concat(val_rows, ignore_index=True),
        "test": pd.concat(test_rows, ignore_index=True),
    }

    splits["train"].to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    splits["val"].to_csv(os.path.join(OUTPUT_DIR, "val.csv"), index=False)
    splits["test"].to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)

    return splits


if __name__ == "__main__":
    make_splits()

