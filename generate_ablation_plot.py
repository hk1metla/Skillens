"""
Generate ablation study plot from CSV data.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "results", "ablation_study.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "results", "plots", "ablation_study.png")

def generate_ablation_plot():
    """Generate bar chart for ablation study results."""
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found")
        return
    
    df = pd.read_csv(CSV_PATH)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Extract data
    configurations = df["configuration"].values
    ndcg_values = df["ndcg"].values
    improvements = df["ndcg_improvement"].values
    
    # Create bar chart
    bars = ax.bar(range(len(configurations)), ndcg_values, alpha=0.7, edgecolor="black")
    
    # Color bars
    colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12"]
    for i, (bar, color) in enumerate(zip(bars, colors[:len(bars)])):
        bar.set_color(color)
    
    # Add value labels on bars
    for i, (ndcg, improvement) in enumerate(zip(ndcg_values, improvements)):
        label = f"{ndcg:.3f}\n({improvement:+.1f}%)"
        ax.text(i, ndcg + max(ndcg_values) * 0.02, label,
               ha="center", va="bottom", fontsize=9, fontweight="bold")
    
    # Set labels and title
    ax.set_xlabel("Configuration", fontsize=12, fontweight="bold")
    ax.set_ylabel("NDCG@10", fontsize=12, fontweight="bold")
    ax.set_title("Ablation Study: Component Contributions", fontsize=14, fontweight="bold")
    ax.set_xticks(range(len(configurations)))
    ax.set_xticklabels(configurations, rotation=15, ha="right")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(ndcg_values) * 1.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"✓ Saved ablation study plot to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_ablation_plot()
