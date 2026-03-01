from src.eval.metrics import ndcg_at_k, precision_at_k, recall_at_k


def test_precision_at_k():
    recs = ["a", "b", "c"]
    relevant = ["a", "d"]
    assert precision_at_k(recs, relevant, 2) == 0.5


def test_recall_at_k():
    recs = ["a", "b", "c"]
    relevant = ["a", "d"]
    assert recall_at_k(recs, relevant, 3) == 0.5


def test_ndcg_at_k():
    recs = ["a", "b", "c"]
    relevant = ["a", "c"]
    assert ndcg_at_k(recs, relevant, 3) > 0.6

