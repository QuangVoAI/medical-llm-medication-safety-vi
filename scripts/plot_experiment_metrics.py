#!/usr/bin/env python3
"""Plot observed experiment metrics for the lab presentation."""

from __future__ import annotations

import csv
import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluator import score_answer


OUT = ROOT / "outputs"
CHART_DIR = OUT / "charts"
LOSS_CSV = OUT / "observed_sft_debug_loss.csv"
OUTPUTS_CSV = OUT / "observed_sft_debug_outputs.csv"
SCORED_CSV = OUT / "observed_sft_debug_scored.csv"


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "#f8fafc",
            "axes.edgecolor": "#cbd5e1",
            "axes.labelcolor": "#0f172a",
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "font.size": 10,
            "grid.color": "#e2e8f0",
            "grid.linestyle": "-",
            "grid.linewidth": 1,
        }
    )


def plot_loss() -> None:
    df = pd.read_csv(LOSS_CSV)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df["step"], df["training_loss"], marker="o", linewidth=2.5, color="#0f766e")
    ax.set_title("SFT Debug Training Loss (10 Steps)")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Training loss")
    ax.set_xticks(df["step"])
    ax.grid(True)
    ax.annotate(
        f"start {df['training_loss'].iloc[0]:.2f}",
        xy=(df["step"].iloc[0], df["training_loss"].iloc[0]),
        xytext=(1.5, df["training_loss"].iloc[0] + 0.12),
        arrowprops={"arrowstyle": "->", "color": "#334155"},
    )
    ax.annotate(
        f"end {df['training_loss'].iloc[-1]:.2f}",
        xy=(df["step"].iloc[-1], df["training_loss"].iloc[-1]),
        xytext=(7.4, df["training_loss"].iloc[-1] + 0.28),
        arrowprops={"arrowstyle": "->", "color": "#334155"},
    )
    fig.tight_layout()
    fig.savefig(CHART_DIR / "sft_debug_loss_curve.png", dpi=180)
    plt.close(fig)


def score_outputs() -> pd.DataFrame:
    rows = []
    with OUTPUTS_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            scores = score_answer(row["question"], row["answer"])
            rows.append({**row, **scores})
    df = pd.DataFrame(rows)
    df.to_csv(SCORED_CSV, index=False)
    return df


def plot_rubric_by_prompt(df: pd.DataFrame) -> None:
    labels = [textwrap.fill(x.replace("_", " "), 14) for x in df["prompt_id"]]
    metrics = ["safety", "uncertainty", "actionability", "factuality"]
    metric_labels = {
        "safety": "safety",
        "uncertainty": "uncertainty",
        "actionability": "actionability",
        "factuality": "keyword proxy",
    }
    colors = ["#0f766e", "#2563eb", "#ca8a04", "#dc2626"]

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    x = range(len(df))
    width = 0.18
    for i, (metric, color) in enumerate(zip(metrics, colors)):
        offsets = [v + (i - 1.5) * width for v in x]
        ax.bar(offsets, df[metric], width=width, label=metric_labels[metric], color=color)
    ax.set_title("SFT Debug Output Scores By Prompt")
    ax.set_ylabel("Heuristic score (0-3)")
    ax.set_ylim(0, 3.2)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.grid(axis="y")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "sft_debug_scores_by_prompt.png", dpi=180)
    plt.close(fig)


def plot_average_scores(df: pd.DataFrame) -> None:
    metrics = ["safety", "uncertainty", "actionability", "factuality", "vietnamese_quality"]
    means = df[metrics].mean().sort_values(ascending=False)
    label_map = {
        "factuality": "keyword proxy",
        "vietnamese_quality": "vietnamese quality",
    }

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#0f766e" if value >= 2 else "#ca8a04" for value in means]
    ax.barh([label_map.get(m, m.replace("_", " ")) for m in means.index], means.values, color=colors)
    ax.set_title("Average SFT Debug Rubric Scores")
    ax.set_xlabel("Average heuristic score (0-3)")
    ax.set_xlim(0, 3.0)
    ax.grid(axis="x")
    for idx, value in enumerate(means.values):
        ax.text(value + 0.04, idx, f"{value:.2f}", va="center", color="#0f172a")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "sft_debug_average_scores.png", dpi=180)
    plt.close(fig)


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    style()
    plot_loss()
    scored = score_outputs()
    plot_rubric_by_prompt(scored)
    plot_average_scores(scored)
    print(f"Wrote scored outputs: {SCORED_CSV}")
    print(f"Wrote charts to: {CHART_DIR}")


if __name__ == "__main__":
    main()
