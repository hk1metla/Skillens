import os

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_PATH = os.path.join(BASE_DIR, "results", "metrics.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "results", "plots")


def make_plots() -> None:
    results = pd.read_csv(RESULTS_PATH)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    metrics = ["precision", "recall", "ndcg"]
    for metric in metrics:
        ax.plot(results["model"], results[metric], marker="o", label=metric)

    ax.set_title("Model Comparison (Top-K)")
    ax.set_ylabel("Score")
    ax.set_xlabel("Model")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "metrics.png"), dpi=160)


if __name__ == "__main__":
    make_plots()

