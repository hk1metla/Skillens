import pandas as pd

from src.data.make_splits import _split_user_history


def test_split_user_history_ordered():
    data = pd.DataFrame(
        {
            "user_id": ["u1"] * 5,
            "item_id": ["a", "b", "c", "d", "e"],
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        }
    )

    train, val, test = _split_user_history(data, 0.6, 0.2)
    assert len(train) == 3
    assert len(val) == 1
    assert len(test) == 1

