"""
Statistical evaluation utilities for recommender systems.

Provides bootstrap confidence intervals, paired significance tests,
effect size computation, and multiple comparison correction.
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy import stats


def bootstrap_confidence_interval(
    values: List[float],
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    random_seed: int = 42,
) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for a metric.
    
    Args:
        values: List of metric values (one per user/query)
        confidence: Confidence level (default 0.95 for 95% CI)
        n_bootstrap: Number of bootstrap samples
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuple of (mean, lower_bound, upper_bound)
    """
    if not values:
        return 0.0, 0.0, 0.0
    
    np.random.seed(random_seed)
    values = np.array(values)
    n = len(values)
    
    # Bootstrap sampling
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(values, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))
    
    bootstrap_means = np.array(bootstrap_means)
    
    # Compute confidence interval
    alpha = 1 - confidence
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(bootstrap_means, lower_percentile)
    upper_bound = np.percentile(bootstrap_means, upper_percentile)
    mean_value = np.mean(values)
    
    return float(mean_value), float(lower_bound), float(upper_bound)


def paired_t_test(
    metric_a: List[float],
    metric_b: List[float],
    alpha: float = 0.05,
) -> Dict[str, float]:
    """
    Perform paired t-test to compare two models.
    
    Tests if the difference between models is statistically significant.
    
    Args:
        metric_a: Metric values for model A (one per user/query)
        metric_b: Metric values for model B (same order as A)
        alpha: Significance level (default 0.05)
        
    Returns:
        Dict with keys: 'statistic', 'pvalue', 'significant', 'mean_diff'
    """
    if len(metric_a) != len(metric_b):
        raise ValueError("Metric lists must have the same length")
    
    metric_a = np.array(metric_a)
    metric_b = np.array(metric_b)
    
    # Compute differences
    differences = metric_a - metric_b
    mean_diff = np.mean(differences)
    
    # Paired t-test
    statistic, pvalue = stats.ttest_rel(metric_a, metric_b)
    
    significant = pvalue < alpha
    
    return {
        "statistic": float(statistic),
        "pvalue": float(pvalue),
        "significant": significant,
        "mean_diff": float(mean_diff),
        "mean_a": float(np.mean(metric_a)),
        "mean_b": float(np.mean(metric_b)),
    }


def wilcoxon_signed_rank_test(
    metric_a: List[float],
    metric_b: List[float],
    alpha: float = 0.05,
) -> Dict[str, float]:
    """
    Perform Wilcoxon signed-rank test (non-parametric alternative to t-test).
    
    More robust to outliers and non-normal distributions.
    
    Args:
        metric_a: Metric values for model A
        metric_b: Metric values for model B
        alpha: Significance level
        
    Returns:
        Dict with test results
    """
    if len(metric_a) != len(metric_b):
        raise ValueError("Metric lists must have the same length")
    
    statistic, pvalue = stats.wilcoxon(metric_a, metric_b, alternative='two-sided')
    
    significant = pvalue < alpha
    
    return {
        "statistic": float(statistic),
        "pvalue": float(pvalue),
        "significant": significant,
        "mean_a": float(np.mean(metric_a)),
        "mean_b": float(np.mean(metric_b)),
    }


def compute_effect_size(metric_a: List[float], metric_b: List[float]) -> float:
    """
    Compute Cohen's d effect size.
    
    Measures the magnitude of difference between two models.
    Interpretation:
    - |d| < 0.2: negligible
    - 0.2 <= |d| < 0.5: small
    - 0.5 <= |d| < 0.8: medium
    - |d| >= 0.8: large
    
    Args:
        metric_a: Metric values for model A
        metric_b: Metric values for model B
        
    Returns:
        Cohen's d
    """
    metric_a = np.array(metric_a)
    metric_b = np.array(metric_b)
    
    mean_a = np.mean(metric_a)
    mean_b = np.mean(metric_b)
    
    std_a = np.std(metric_a, ddof=1)
    std_b = np.std(metric_b, ddof=1)
    
    # Pooled standard deviation
    n_a = len(metric_a)
    n_b = len(metric_b)
    pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))
    
    if pooled_std == 0:
        return 0.0
    
    cohens_d = (mean_a - mean_b) / pooled_std
    return float(cohens_d)


def multiple_comparison_correction(
    pvalues: List[float],
    method: str = "bonferroni",
) -> List[float]:
    """
    Apply multiple comparison correction to p-values.
    
    Reduces false positives when testing multiple hypotheses.
    
    Args:
        pvalues: List of p-values
        method: Correction method ('bonferroni' or 'fdr_bh' for Benjamini-Hochberg)
        
    Returns:
        List of corrected p-values
    """
    pvalues = np.array(pvalues)
    
    if method == "bonferroni":
        # Bonferroni correction: multiply by number of tests
        corrected = pvalues * len(pvalues)
        corrected = np.clip(corrected, 0, 1)
    elif method == "fdr_bh":
        # Benjamini-Hochberg FDR correction
        try:
            from statsmodels.stats.multitest import multipletests
            _, corrected, _, _ = multipletests(pvalues, alpha=0.05, method='fdr_bh')
        except ImportError:
            # Fallback if statsmodels not available
            corrected = pvalues * len(pvalues)  # Simple Bonferroni
            corrected = np.clip(corrected, 0, 1)
    else:
        raise ValueError(f"Unknown correction method: {method}")
    
    return corrected.tolist()
