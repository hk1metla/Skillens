# Skillens Evaluation Report
Generated: 2026-02-06 01:11:01

## Executive Summary

This report presents comprehensive evaluation results for the Skillens
educational recommendation system, including accuracy, diversity, fairness,
and statistical rigor.

## 1. Data Split Validation

- **Global Temporal Ordering**: ✗ Invalid
- **Per-User Temporal Ordering**: ✓ Valid
- **Train Size**: 6382979 (59.9%)
- **Validation Size**: 2130988 (20.0%)
- **Test Size**: 2141313 (20.1%)
- **Cold-Start Users**: 0
- **New Items**: 0

## 2. Model Performance Comparison

### Accuracy Metrics

     model  precision_mean  recall_mean  ndcg_mean
popularity        0.063127     0.580203   0.289137
     tfidf        0.104334     0.983008   0.980489
   itemknn        0.000167     0.000924   0.000897
    hybrid        0.103353     0.977478   0.707356

### Diversity & Coverage Metrics

     model  diversity_mean  catalog_coverage  gini_coefficient
popularity        0.664359          0.454545          0.000000
     tfidf        0.683448          1.000000          0.153895
   itemknn        0.681483          1.000000          0.188174
    hybrid        0.675138          1.000000          0.135763

## 3. Ablation Study

Component contribution analysis:

                   configuration     ndcg  ndcg_improvement
           Baseline (Popularity) 0.289137          0.000000
              Content-Based Only 0.980489        239.108293
    Collaborative Filtering Only 0.000897        -99.689732
Hybrid (w_content=0.6, w_cf=0.4) 0.707356        144.643516

## 4. Statistical Significance Testing

Statistical comparisons between all model pairs:

- **Tests performed**: Paired t-test, Wilcoxon signed-rank test
- **Correction**: Bonferroni correction for multiple comparisons
- **Total comparisons**: 18
- **Significant differences (p<0.05, corrected)**: 18

All model comparisons show statistically significant differences across all metrics.

**Key Comparison: TF-IDF vs Hybrid (NDCG)**
- Mean difference: 0.2731
- p-value (corrected): 0.00e+00
- Effect size (Cohen's d): 1.412

## 5. Key Findings

- **Best Model**: tfidf (NDCG: 0.9805, 95% CI: [0.9792, 0.9817])
- **Hybrid vs TF-IDF**: -27.9% change (Hybrid: 0.7074, TF-IDF: 0.9805)

**Evaluation Methodology Notes:**
- Queries for content-based models built exclusively from training data (prevents data leakage)
- Temporal split ensures training interactions precede test interactions per user
- All metrics include 95% bootstrap confidence intervals
- Statistical significance testing with Bonferroni correction applied
