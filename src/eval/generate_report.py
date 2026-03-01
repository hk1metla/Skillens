"""
Generate comprehensive evaluation report.

Creates a detailed report with all metrics, statistical tests, and visualizations.
This is the final output for the evaluation chapter.
"""

import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.eval.comprehensive_eval import run_comprehensive_eval
from src.eval.ablation import run_ablation_study
from src.data.validate_splits import validate_splits


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def generate_evaluation_report(config_path: str) -> str:
    """
    Generate comprehensive evaluation report.
    
    Returns:
        Path to generated report file
    """
    print("Generating Comprehensive Evaluation Report...")
    print("=" * 60)
    
    # Run all evaluations
    print("\n1. Validating data splits...")
    split_validation = validate_splits()
    
    print("\n2. Running comprehensive evaluation...")
    comprehensive_results = run_comprehensive_eval(config_path)
    
    print("\n3. Running ablation study...")
    ablation_results = run_ablation_study(config_path)
    
    # Generate report
    report_lines = []
    report_lines.append("# Skillens Evaluation Report")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append("This report presents comprehensive evaluation results for the Skillens")
    report_lines.append("educational recommendation system, including accuracy, diversity, fairness,")
    report_lines.append("and statistical rigor.")
    report_lines.append("")
    
    # Split validation
    report_lines.append("## 1. Data Split Validation")
    report_lines.append("")
    if len(split_validation) > 0:
        val_row = split_validation.iloc[0]
        report_lines.append(f"- **Global Temporal Ordering**: {'✓ Valid' if val_row['global_ordering'] else '✗ Invalid'}")
        report_lines.append(f"- **Per-User Temporal Ordering**: {'✓ Valid' if val_row['per_user_ordering'] else '✗ Invalid'}")
        report_lines.append(f"- **Train Size**: {int(val_row['train_size'])} ({val_row['train_ratio']:.1%})")
        report_lines.append(f"- **Validation Size**: {int(val_row['val_size'])} ({val_row['val_ratio']:.1%})")
        report_lines.append(f"- **Test Size**: {int(val_row['test_size'])} ({val_row['test_ratio']:.1%})")
        report_lines.append(f"- **Cold-Start Users**: {int(val_row['n_cold_start_users'])}")
        report_lines.append(f"- **New Items**: {int(val_row['n_new_items'])}")
    report_lines.append("")
    
    # Model comparison
    report_lines.append("## 2. Model Performance Comparison")
    report_lines.append("")
    report_lines.append("### Accuracy Metrics")
    report_lines.append("")
    if len(comprehensive_results) > 0:
        acc_metrics = comprehensive_results[["model", "precision_mean", "recall_mean", "ndcg_mean"]]
        report_lines.append(acc_metrics.to_string(index=False))
    report_lines.append("")
    
    report_lines.append("### Diversity & Coverage Metrics")
    report_lines.append("")
    if len(comprehensive_results) > 0:
        div_metrics = comprehensive_results[["model", "diversity_mean", "catalog_coverage", "gini_coefficient"]]
        report_lines.append(div_metrics.to_string(index=False))
    report_lines.append("")
    
    # Ablation study
    report_lines.append("## 3. Ablation Study")
    report_lines.append("")
    report_lines.append("Component contribution analysis:")
    report_lines.append("")
    if len(ablation_results) > 0:
        report_lines.append(ablation_results[["configuration", "ndcg", "ndcg_improvement"]].to_string(index=False))
    report_lines.append("")
    
    # Key findings
    report_lines.append("## 4. Key Findings")
    report_lines.append("")
    if len(comprehensive_results) > 0:
        best_model = comprehensive_results.loc[comprehensive_results["ndcg_mean"].idxmax()]
        report_lines.append(f"- **Best Model**: {best_model['model']} (NDCG: {best_model['ndcg_mean']:.4f})")
        
        if "hybrid" in comprehensive_results["model"].values:
            hybrid_row = comprehensive_results[comprehensive_results["model"] == "hybrid"].iloc[0]
            tfidf_row = comprehensive_results[comprehensive_results["model"] == "tfidf"].iloc[0]
            improvement = ((hybrid_row["ndcg_mean"] - tfidf_row["ndcg_mean"]) / tfidf_row["ndcg_mean"]) * 100
            report_lines.append(f"- **Hybrid Improvement**: {improvement:.1f}% over TF-IDF")
    report_lines.append("")
    
    # Write report
    report_path = os.path.join(RESULTS_DIR, "evaluation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    print(f"\n✅ Report generated: {report_path}")
    return report_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiment.yaml")
    args = parser.parse_args()
    generate_evaluation_report(args.config)
