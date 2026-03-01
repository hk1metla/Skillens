import pandas as pd


def test_item_schema():
    items = pd.DataFrame(
        {
            "item_id": ["id1"],
            "title": ["Course A"],
            "description": ["Sample description"],
        }
    )
    assert items["item_id"].isnull().sum() == 0
    assert items["title"].isnull().sum() == 0

