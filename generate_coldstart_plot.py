"""
Generate cold-start performance plot from canonical CSV data.
Shows how hybrid and content-only models perform across different user history lengths.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "results", "final", "history_truncation.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "results", "final", "plots", "coldstart_performance.png")

def generate_coldstart_plot():
    """Generate line chart for cold-start performance from canonical CSV."""
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found")
        return

    df = pd.read_csv(CSV_PATH)

    # Filter out bins with zero users
    df = df[df["n_users"] > 0]

    # Pivot to get hybrid and tfidf as columns
    hybrid_df = df[df["model"] == "hybrid"].sort_values("bin")
    tfidf_df = df[df["model"] == "tfidf"].sort_values("bin")

    history_labels = hybrid_df["bin"].values
    hybrid_ndcg = hybrid_df["ndcg"].values
    content_ndcg = tfidf_df["ndcg"].values

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot lines
    x = np.arange(len(history_labels))
    ax.plot(x, hybrid_ndcg, marker="o", linewidth=2, markersize=10,
            label="Hybrid", color="#2ecc71")
    ax.plot(x, content_ndcg, marker="s", linewidth=2, markersize=10,
            label="Content-Only", color="#3498db")

    # Add value labels on points
    for i, (hyb, cont) in enumerate(zip(hybrid_ndcg, content_ndcg)):
        ax.text(i, hyb + 0.01, f"{hyb:.3f}", ha="center", va="bottom",
               fontsize=9, fontweight="bold", color="#2ecc71")
        offset = -0.015 if hyb != cont else 0.01
        va = "top" if hyb != cont else "bottom"
        ax.text(i, cont + offset, f"{cont:.3f}", ha="center", va=va,
               fontsize=9, fontweight="bold", color="#3498db")

    # Set labels and title
    ax.set_xlabel("User Interaction History Length", fontsize=12, fontweight="bold")
    ax.set_ylabel("NDCG@10", fontsize=12, fontweight="bold")
    ax.set_title("Cold-Start Performance: NDCG@10 by User History Length",
                fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(history_labels)
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(alpha=0.3, linestyle="--")

    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✓ Saved cold-start performance plot to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_coldstart_plot()
