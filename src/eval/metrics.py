"""
Comprehensive evaluation metrics for recommender systems.

Includes accuracy, diversity, coverage, novelty, and fairness metrics.
"""

import numpy as np
from typing import List, Set, Dict


def precision_at_k(recommended, relevant, k: int) -> float:
    """Precision@K: fraction of recommended items that are relevant."""
    if k == 0:
        return 0.0
    rec_k = recommended[:k]
    hits = len(set(rec_k) & set(relevant))
    return hits / k


def recall_at_k(recommended, relevant, k: int) -> float:
    """Recall@K: fraction of relevant items that are recommended."""
    if not relevant:
        return 0.0
    rec_k = recommended[:k]
    hits = len(set(rec_k) & set(relevant))
    return hits / len(set(relevant))


def ndcg_at_k(recommended, relevant, k: int) -> float:
    """NDCG@K with binary relevance (implicit feedback)."""
    if k <= 0:
        return 0.0
    rel = set(relevant)
    if not rel:
        return 0.0
    rec_k = recommended[:k]
    gains = [1.0 if item in rel else 0.0 for item in rec_k]
    dcg = float(np.sum([g / np.log2(i + 2) for i, g in enumerate(gains)]))
    ideal_len = min(len(rel), k)
    idcg = float(np.sum([1.0 / np.log2(i + 2) for i in range(ideal_len)]))
    return 0.0 if idcg == 0.0 else dcg / idcg


def intra_list_diversity(recommended: List[str], item_features: Dict[str, List[float]], k: int) -> float:
    """
    Intra-list diversity: average pairwise distance between recommended items.
    
    Measures how diverse the recommendations are within a single list.
    Higher values indicate more diversity.
    
    Args:
        recommended: List of recommended item IDs
        item_features: Dict mapping item_id to feature vector
        k: Number of items to consider
        
    Returns:
        Average pairwise cosine distance (1 - cosine similarity)
    """
    if len(recommended) < 2 or k < 2:
        return 0.0
    
    rec_k = recommended[:k]
    valid_items = [item for item in rec_k if item in item_features]
    
    if len(valid_items) < 2:
        return 0.0
    
    # Compute pairwise distances
    distances = []
    features = np.array([item_features[item] for item in valid_items])
    
    for i in range(len(valid_items)):
        for j in range(i + 1, len(valid_items)):
            # Cosine distance = 1 - cosine similarity
            dot_product = np.dot(features[i], features[j])
            norm_i = np.linalg.norm(features[i])
            norm_j = np.linalg.norm(features[j])
            
            if norm_i > 0 and norm_j > 0:
                cosine_sim = dot_product / (norm_i * norm_j)
                cosine_dist = 1.0 - cosine_sim
                distances.append(cosine_dist)
    
    return float(np.mean(distances)) if distances else 0.0


def catalog_coverage(all_recommendations: List[List[str]], catalog_size: int) -> float:
    """
    Catalog coverage: fraction of catalog items that appear in recommendations.
    
    Measures how well the system explores the item catalog.
    
    Args:
        all_recommendations: List of recommendation lists (one per user/query)
        catalog_size: Total number of items in catalog
        
    Returns:
        Coverage ratio [0, 1]
    """
    if catalog_size == 0:
        return 0.0
    
    unique_recommended = set()
    for recs in all_recommendations:
        unique_recommended.update(recs)
    
    return len(unique_recommended) / catalog_size


def novelty(recommended: List[str], item_popularity: Dict[str, float], k: int) -> float:
    """
    Novelty: average negative log popularity of recommended items.
    
    Higher values indicate recommendations of less popular (more novel) items.
    
    Args:
        recommended: List of recommended item IDs
        item_popularity: Dict mapping item_id to popularity score (0-1)
        k: Number of items to consider
        
    Returns:
        Average novelty score
    """
    if k == 0:
        return 0.0
    
    rec_k = recommended[:k]
    novelty_scores = []
    
    for item in rec_k:
        # Use small epsilon to avoid log(0)
        popularity = item_popularity.get(item, 0.0001)
        novelty = -np.log2(popularity + 1e-10)
        novelty_scores.append(novelty)
    
    return float(np.mean(novelty_scores)) if novelty_scores else 0.0


def gini_coefficient(item_counts: Dict[str, int]) -> float:
    """
    Gini coefficient: measures inequality in recommendation distribution.
    
    Lower values indicate more equal distribution (better for fairness).
    Range: [0, 1] where 0 = perfect equality, 1 = perfect inequality.
    
    Args:
        item_counts: Dict mapping item_id to recommendation count
        
    Returns:
        Gini coefficient
    """
    if not item_counts:
        return 0.0
    
    counts = np.array(sorted(item_counts.values()))
    n = len(counts)
    
    if n == 0 or counts.sum() == 0:
        return 0.0
    
    # Normalize to proportions
    proportions = counts / counts.sum()
    
    # Compute Gini coefficient
    cumsum = np.cumsum(proportions)
    gini = (n + 1 - 2 * np.sum((n + 1 - np.arange(1, n + 1)) * proportions)) / n
    
    return float(gini)


def long_tail_coverage(
    recommended: List[str],
    popular_items: Set[str],
    k: int
) -> float:
    """
    Long-tail coverage: fraction of recommendations from long-tail (non-popular) items.
    
    Measures how well the system recommends less popular items.
    
    Args:
        recommended: List of recommended item IDs
        popular_items: Set of popular item IDs (e.g., top 20% by popularity)
        k: Number of items to consider
        
    Returns:
        Long-tail coverage ratio [0, 1]
    """
    if k == 0:
        return 0.0
    
    rec_k = recommended[:k]
    long_tail_items = [item for item in rec_k if item not in popular_items]
    
    return len(long_tail_items) / len(rec_k)


def serendipity(
    recommended: List[str],
    relevant: List[str],
    expected_items: Set[str],
    k: int
) -> float:
    """
    Serendipity: fraction of relevant items that are unexpected.
    
    Measures how well the system recommends surprising but relevant items.
    
    Args:
        recommended: List of recommended item IDs
        relevant: List of relevant item IDs
        expected_items: Set of items user would expect (e.g., popular items)
        k: Number of items to consider
        
    Returns:
        Serendipity score [0, 1]
    """
    if k == 0 or not relevant:
        return 0.0
    
    rec_k = set(recommended[:k])
    relevant_set = set(relevant)
    expected_set = set(expected_items)
    
    # Relevant and unexpected items
    serendipitous = rec_k & relevant_set - expected_set
    
    return len(serendipitous) / len(relevant_set) if relevant_set else 0.0

