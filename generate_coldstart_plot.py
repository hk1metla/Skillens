"""
Generate cold-start performance plot.
Shows how hybrid and content-only models perform across different user history lengths.
"""
import os
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "results", "plots", "coldstart_performance.png")

def generate_coldstart_plot():
    """Generate line chart for cold-start performance."""
    # Data from the table in the document
    history_labels = ["0\n(cold-start)", "1-5", "6-20", "21+"]
    hybrid_ndcg = [0.18, 0.21, 0.24, 0.27]
    content_ndcg = [0.18, 0.19, 0.20, 0.21]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot lines
    ax.plot(history_labels, hybrid_ndcg, marker="o", linewidth=2, markersize=10, 
            label="Hybrid", color="#2ecc71")
    ax.plot(history_labels, content_ndcg, marker="s", linewidth=2, markersize=10, 
            label="Content-Only", color="#3498db")
    
    # Add value labels on points
    for i, (hyb, cont) in enumerate(zip(hybrid_ndcg, content_ndcg)):
        ax.text(i, hyb + 0.01, f"{hyb:.2f}", ha="center", va="bottom", 
               fontsize=9, fontweight="bold", color="#2ecc71")
        ax.text(i, cont - 0.015, f"{cont:.2f}", ha="center", va="top", 
               fontsize=9, fontweight="bold", color="#3498db")
    
    # Set labels and title
    ax.set_xlabel("User Interaction History Length", fontsize=12, fontweight="bold")
    ax.set_ylabel("NDCG@10", fontsize=12, fontweight="bold")
    ax.set_title("Cold-Start Performance: NDCG@10 by User History Length", 
                fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_ylim(0.15, 0.30)
    
    # Add annotation
    ax.text(0.5, 0.95, "Content-based provides stable cold-start performance\nHybrid improves as history grows", 
           transform=ax.transAxes, ha="center", va="top", 
           bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
           fontsize=10)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"✓ Saved cold-start performance plot to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_coldstart_plot()
