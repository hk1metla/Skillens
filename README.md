# Skillens -- Educational Content Recommender

CM3070 Final Year Project | University of London

Shahzaib Naeem | BSc Computer Science (ML & AI)

## Setup

```bash
pip install -r requirements.txt
```

## Data Preparation

Place OULAD `anonymisedData/` folder in repo root, then:

```bash
python -m src.eval.pipeline --config configs/experiment.yaml --prepare-data
```

## Run Evaluation (regenerates ALL report tables and figures)

```bash
python -m src.eval.pipeline --config configs/experiment.yaml --out results/final
```

## Launch UI

```bash
streamlit run src/app/app.py
```

## Expected Outputs

| File | Report Reference |
|------|-----------------|
| `results/final/comprehensive_metrics.csv` | Table 9 (Baseline comparison) |
| `results/final/ablation_study.csv` | Table 10 (Ablation study) |
| `results/final/significance_matrix.csv` | Figure 9 (Significance heatmap) |
| `results/final/fairness_accuracy.csv` | Table 11 (Fairness analysis) |
| `results/final/history_truncation.csv` | Table 12 (Cold-start performance) |
| `results/final/run_manifest.json` | Reproducibility log |
| `results/final/plots/*.png` | All report figures |
