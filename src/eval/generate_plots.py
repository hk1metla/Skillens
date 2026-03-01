"""
Generate comparison plots for evaluation results.

Creates bar charts, significance visualizations, and fairness comparisons.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")

# Set style
plt.style.use("default")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_results():
    """Load evaluation results."""
    metrics_path = os.path.join(RESULTS_DIR, "comprehensive_metrics.csv")
    significance_path = os.path.join(RESULTS_DIR, "significance_matrix.csv")
    
    metrics_df = pd.read_csv(metrics_path)
    significance_df = pd.read_csv(significance_path) if os.path.exists(significance_path) else None
    
    return metrics_df, significance_df


def plot_accuracy_metrics(metrics_df: pd.DataFrame):
    """Create bar chart comparing accuracy metrics across models."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    metrics_to_plot = ["precision_mean", "recall_mean", "ndcg_mean"]
    metric_labels = ["Precision@10", "Recall@10", "NDCG@10"]
    
    for idx, (metric, label) in enumerate(zip(metrics_to_plot, metric_labels)):
        ax = axes[idx]
        
        # Extract data
        models = metrics_df["model"].values
        values = metrics_df[metric].values
        ci_lower = metrics_df[f"{metric.replace('_mean', '')}_ci_lower"].values
        ci_upper = metrics_df[f"{metric.replace('_mean', '')}_ci_upper"].values
        errors = np.array([values - ci_lower, ci_upper - values])
        
        # Create bar plot with error bars
        bars = ax.bar(models, values, yerr=errors, capsize=5, alpha=0.7, edgecolor="black")
        
        # Color bars
        colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12"]
        for bar, color in zip(bars, colors[:len(bars)]):
            bar.set_color(color)
        
        ax.set_ylabel(label, fontsize=12, fontweight="bold")
        ax.set_xlabel("Model", fontsize=12, fontweight="bold")
        ax.set_title(f"{label} Comparison", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1.0)
        ax.grid(axis="y", alpha=0.3)
        
        # Add value labels on bars
        for i, (model, value) in enumerate(zip(models, values)):
            ax.text(i, value + errors[1][i] + 0.01, f"{value:.3f}", 
                   ha="center", va="bottom", fontsize=9)
    
    plt.tight_layout()
    os.makedirs(PLOTS_DIR, exist_ok=True)
    plt.savefig(os.path.join(PLOTS_DIR, "accuracy_metrics_comparison.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved accuracy metrics plot to {PLOTS_DIR}/accuracy_metrics_comparison.png")


def plot_diversity_metrics(metrics_df: pd.DataFrame):
    """Create bar chart comparing diversity metrics."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    metrics_to_plot = ["diversity_mean", "novelty_mean"]
    metric_labels = ["Intra-List Diversity", "Novelty"]
    
    for idx, (metric, label) in enumerate(zip(metrics_to_plot, metric_labels)):
        ax = axes[idx]
        
        models = metrics_df["model"].values
        values = metrics_df[metric].values
        
        bars = ax.bar(models, values, alpha=0.7, edgecolor="black")
        
        colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12"]
        for bar, color in zip(bars, colors[:len(bars)]):
            bar.set_color(color)
        
        ax.set_ylabel(label, fontsize=12, fontweight="bold")
        ax.set_xlabel("Model", fontsize=12, fontweight="bold")
        ax.set_title(f"{label} Comparison", fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        
        # Add value labels
        for i, (model, value) in enumerate(zip(models, values)):
            ax.text(i, value + max(values) * 0.02, f"{value:.3f}", 
                   ha="center", va="bottom", fontsize=9)
    
    plt.tight_layout()
    os.makedirs(PLOTS_DIR, exist_ok=True)
    plt.savefig(os.path.join(PLOTS_DIR, "diversity_metrics_comparison.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved diversity metrics plot to {PLOTS_DIR}/diversity_metrics_comparison.png")


def plot_significance_heatmap(significance_df: pd.DataFrame):
    """Create heatmap showing statistical significance."""
    if significance_df is None or len(significance_df) == 0:
        print("⚠ No significance data available for heatmap")
        return
    
    # Filter to NDCG metric (most important)
    ndcg_df = significance_df[significance_df["metric"] == "ndcg"].copy()
    
    if len(ndcg_df) == 0:
        print("⚠ No NDCG significance data available")
        return
    
    # Create pivot table for p-values
    pivot_data = []
    for _, row in ndcg_df.iterrows():
        pivot_data.append({
            "model_a": row["model_a"],
            "model_b": row["model_b"],
            "pvalue": row["t_pvalue_corrected"],
            "significant": row["t_significant_corrected"],
        })
    
    pivot_df = pd.DataFrame(pivot_data)
    
    # Get unique models
    all_models = sorted(set(pivot_df["model_a"].unique()) | set(pivot_df["model_b"].unique()))
    
    # Create matrix
    matrix = np.ones((len(all_models), len(all_models)))
    matrix_labels = np.empty((len(all_models), len(all_models)), dtype=object)
    
    for _, row in pivot_df.iterrows():
        i = all_models.index(row["model_a"])
        j = all_models.index(row["model_b"])
        
        pval = row["pvalue"]
        sig = row["significant"]
        
        # Store p-value (lower is more significant)
        matrix[i, j] = pval
        matrix[j, i] = pval
        
        # Create label
        label = f"p={pval:.2e}" if pval > 0 else "p<0.001"
        if sig:
            label += "\n*"
        matrix_labels[i, j] = label
        matrix_labels[j, i] = label
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Use log scale for p-values (better visualization)
    matrix_log = np.log10(matrix + 1e-10)
    
    im = ax.imshow(matrix_log, cmap="RdYlGn_r", aspect="auto")
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(all_models)))
    ax.set_yticks(np.arange(len(all_models)))
    ax.set_xticklabels(all_models)
    ax.set_yticklabels(all_models)
    
    # Add text annotations
    for i in range(len(all_models)):
        for j in range(len(all_models)):
            if i != j:
                text = ax.text(j, i, matrix_labels[i, j], 
                             ha="center", va="center", fontsize=8)
    
    ax.set_title("Statistical Significance (NDCG, Bonferroni Corrected)\n* = Significant (p<0.05)", 
                fontsize=14, fontweight="bold")
    plt.colorbar(im, ax=ax, label="log10(p-value)")
    
    plt.tight_layout()
    os.makedirs(PLOTS_DIR, exist_ok=True)
    plt.savefig(os.path.join(PLOTS_DIR, "significance_heatmap.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved significance heatmap to {PLOTS_DIR}/significance_heatmap.png")


def plot_fairness_comparison():
    """Create fairness comparison plots if available."""
    fairness_path = os.path.join(RESULTS_DIR, "fairness_metrics.csv")
    
    if not os.path.exists(fairness_path):
        print("⚠ No fairness metrics available")
        return
    
    fairness_df = pd.read_csv(fairness_path)
    
    # Plot by demographic category
    categories = fairness_df["demographic_category"].unique()
    
    for category in categories[:3]:  # Limit to first 3 categories
        cat_df = fairness_df[fairness_df["demographic_category"] == category]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Long-tail coverage by group
        ax1 = axes[0]
        for model in cat_df["model"].unique():
            model_df = cat_df[cat_df["model"] == model]
            ax1.plot(model_df["group"], model_df["long_tail_coverage"], 
                    marker="o", label=model, linewidth=2, markersize=8)
        
        ax1.set_xlabel("Demographic Group", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Long-Tail Coverage", fontsize=12, fontweight="bold")
        ax1.set_title(f"Long-Tail Coverage by {category}", fontsize=14, fontweight="bold")
        ax1.legend()
        ax1.grid(alpha=0.3)
        ax1.tick_params(axis="x", rotation=45)
        
        # Plot 2: Gini coefficient by group
        ax2 = axes[1]
        for model in cat_df["model"].unique():
            model_df = cat_df[cat_df["model"] == model]
            ax2.plot(model_df["group"], model_df["gini_coefficient"], 
                    marker="s", label=model, linewidth=2, markersize=8)
        
        ax2.set_xlabel("Demographic Group", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Gini Coefficient", fontsize=12, fontweight="bold")
        ax2.set_title(f"Inequality (Gini) by {category}", fontsize=14, fontweight="bold")
        ax2.legend()
        ax2.grid(alpha=0.3)
        ax2.tick_params(axis="x", rotation=45)
        
        plt.tight_layout()
        os.makedirs(PLOTS_DIR, exist_ok=True)
        safe_category = category.replace(" ", "_").replace("/", "_")
        plt.savefig(os.path.join(PLOTS_DIR, f"fairness_{safe_category}.png"), 
                   dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved fairness plot for {category} to {PLOTS_DIR}/fairness_{safe_category}.png")


def main():
    """Generate all plots."""
    print("Generating evaluation plots...")
    
    metrics_df, significance_df = load_results()
    
    plot_accuracy_metrics(metrics_df)
    plot_diversity_metrics(metrics_df)
    plot_significance_heatmap(significance_df)
    plot_fairness_comparison()
    
    print(f"\n✅ All plots saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
