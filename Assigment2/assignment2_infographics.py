
"""
Assignment 2 infographic generator

Creates four matplotlib infographics that match the concepts asked in the assignment:
1) Confusion matrix for fraud detection
2) Why K-Means fails on concentric rings + linkage intuition
3) Correct pipeline order vs leakage
4) Drift monitoring with KS test / red teaming concept

Run:
    python assignment2_infographics.py

Output:
    assignment2_q1_confusion_matrix.png
    assignment2_q2_rings_and_clustering.png
    assignment2_q3_pipeline_leakage.png
    assignment2_q4_drift_monitoring.png
"""

import matplotlib.pyplot as plt
import os
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Wedge
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def savefig(fig, filename):
    fig.tight_layout()
    outpath = os.path.join(BASE_DIR, filename)
    fig.savefig(outpath, dpi=220, bbox_inches="tight")
    plt.close(fig)


def add_box(ax, x, y, w, h, text, fc="#f5f5f5", ec="#333333", fontsize=10, weight="normal"):
    rect = Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize, weight=weight)


def add_arrow(ax, x1, y1, x2, y2, text=None, fontsize=9, style='-|>', mutation_scale=14):
    arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=mutation_scale,
                          linewidth=1.5, color="#444444")
    ax.add_patch(arr)
    if text:
        ax.text((x1 + x2)/2, (y1 + y2)/2 + 0.03, text, ha="center", va="bottom", fontsize=fontsize)


def q1_confusion_matrix():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([0.5, 1.5])
    ax.set_yticks([0.5, 1.5])
    ax.set_xticklabels(["Predicted Fraud", "Predicted Legitimate"], fontsize=11)
    ax.set_yticklabels(["Actual Fraud", "Actual Legitimate"], fontsize=11)
    ax.set_xlabel("Prediction")
    ax.set_ylabel("Ground Truth")
    ax.set_title("Q1 — Fraud Detection Confusion Matrix", fontsize=14, weight="bold")

    cells = [
        (0, 1, "TP = 0", "#ffd6d6"),
        (1, 1, "FN = 50", "#ffe6b3"),
        (0, 0, "FP = 0", "#ffd6d6"),
        (1, 0, "TN = 9950", "#d9f2d9"),
    ]
    for x, y, label, color in cells:
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor=color, edgecolor="black", linewidth=1.5))
        ax.text(x + 0.5, y + 0.5, label, ha="center", va="center", fontsize=14, weight="bold")

    ax.text(0.5, -0.18, "Model predicts every transaction as legitimate.", transform=ax.transAxes,
            ha="center", fontsize=11)
    ax.text(0.5, -0.27, "Accuracy = 9950 / 10000 = 99.5%   |   Recall = 0 / 50 = 0%",
            transform=ax.transAxes, ha="center", fontsize=11, weight="bold")
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.grid(False)
    savefig(fig, "assignment2_q1_confusion_matrix.png")


def q2_rings_and_clustering():
    rng = np.random.default_rng(7)

    # Generate concentric rings
    n_inner, n_outer = 180, 260
    theta_i = rng.uniform(0, 2*np.pi, n_inner)
    theta_o = rng.uniform(0, 2*np.pi, n_outer)
    r_i = 1.2 + rng.normal(0, 0.05, n_inner)
    r_o = 2.6 + rng.normal(0, 0.06, n_outer)
    inner = np.c_[r_i*np.cos(theta_i), r_i*np.sin(theta_i)]
    outer = np.c_[r_o*np.cos(theta_o), r_o*np.sin(theta_o)]

    # KMeans-style radial split illustration (schematic)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    titles = ["True geometry: concentric rings", "Why K-Means struggles", "Single-linkage intuition"]
    for ax, title in zip(axes, titles):
        ax.set_title(title, fontsize=12, weight="bold")
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-3.5, 3.5)

    # Panel 1
    ax = axes[0]
    ax.scatter(inner[:, 0], inner[:, 1], s=12, alpha=0.8, label="Class A")
    ax.scatter(outer[:, 0], outer[:, 1], s=12, alpha=0.8, label="Class B")
    ax.legend(loc="upper right", frameon=False, fontsize=9)

    # Panel 2
    ax = axes[1]
    ax.scatter(inner[:, 0], inner[:, 1], s=12, alpha=0.8, color="#4c78a8")
    ax.scatter(outer[:, 0], outer[:, 1], s=12, alpha=0.8, color="#f58518")
    # two centroids and a schematic boundary
    ax.scatter([-1.1, 1.1], [0, 0], s=120, marker="X", color="black")
    ax.plot([0, 0], [-3.2, 3.2], "--", color="crimson", linewidth=2)
    ax.text(0.03, 0.98, "K-Means minimizes within-cluster\nsquared distance to centroids.",
            transform=ax.transAxes, ha="left", va="top", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbbbbb"))
    ax.text(0.5, 0.06, "Centroid-based boundaries are convex-ish,\nso rings get cut the wrong way.",
            transform=ax.transAxes, ha="center", fontsize=10)

    # Panel 3
    ax = axes[2]
    ax.scatter(inner[:, 0], inner[:, 1], s=12, alpha=0.8, color="#4c78a8")
    ax.scatter(outer[:, 0], outer[:, 1], s=12, alpha=0.8, color="#f58518")
    # chain-like path across inner ring
    chain_x = np.linspace(-1.2, 1.2, 8)
    chain_y = 0.25*np.sin(np.linspace(0, 3*np.pi, 8))
    ax.plot(chain_x, chain_y, color="#2f2f2f", linewidth=2.2, marker="o", markersize=4)
    ax.add_patch(Circle((0, 0), 1.35, fill=False, linestyle="--", linewidth=1.8, edgecolor="#2ca02c"))
    ax.add_patch(Circle((0, 0), 2.7, fill=False, linestyle="--", linewidth=1.8, edgecolor="#2ca02c"))
    ax.text(0.5, 0.07, "Single-linkage joins nearest points first,\nso it can follow non-convex shapes.",
            transform=ax.transAxes, ha="center", fontsize=10)
    savefig(fig, "assignment2_q2_rings_and_clustering.png")


def q3_pipeline_leakage():
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Q3 — Correct pipeline order and leakage", fontsize=15, weight="bold", pad=10)

    # Bad pipeline top row
    ax.text(0.16, 0.88, "Incorrect", fontsize=13, weight="bold", color="crimson")
    add_box(ax, 0.05, 0.68, 0.16, 0.12, "Full dataset", fc="#fff0f0")
    add_box(ax, 0.25, 0.68, 0.18, 0.12, "Fit scaler\n& target encoder", fc="#fff0f0")
    add_box(ax, 0.47, 0.68, 0.14, 0.12, "Split train/\ntest", fc="#fff0f0")
    add_box(ax, 0.65, 0.68, 0.14, 0.12, "Train model", fc="#fff0f0")
    add_box(ax, 0.83, 0.68, 0.12, 0.12, "Evaluate", fc="#fff0f0")
    add_arrow(ax, 0.21, 0.74, 0.25, 0.74)
    add_arrow(ax, 0.43, 0.74, 0.47, 0.74)
    add_arrow(ax, 0.61, 0.74, 0.65, 0.74)
    add_arrow(ax, 0.79, 0.74, 0.83, 0.74)
    ax.text(0.5, 0.58, "Leakage: the scaler and TargetEncoder see test-set information before the split.",
            ha="center", fontsize=11, color="crimson", weight="bold")

    # Good pipeline bottom row
    ax.text(0.17, 0.40, "Correct", fontsize=13, weight="bold", color="#1b7f3a")
    add_box(ax, 0.05, 0.20, 0.14, 0.12, "Split first", fc="#f0fff0")
    add_box(ax, 0.23, 0.20, 0.16, 0.12, "Fit on train\nonly", fc="#f0fff0")
    add_box(ax, 0.43, 0.20, 0.16, 0.12, "Transform train", fc="#f0fff0")
    add_box(ax, 0.63, 0.20, 0.16, 0.12, "Apply same\ntransform to test", fc="#f0fff0")
    add_box(ax, 0.83, 0.20, 0.12, 0.12, "Train model", fc="#f0fff0")
    add_arrow(ax, 0.19, 0.26, 0.23, 0.26)
    add_arrow(ax, 0.39, 0.26, 0.43, 0.26)
    add_arrow(ax, 0.59, 0.26, 0.63, 0.26)
    add_arrow(ax, 0.79, 0.26, 0.83, 0.26)
    ax.text(0.5, 0.08, "Fit = learn parameters from train only.  Apply = use those learned parameters on unseen data.",
            ha="center", fontsize=11)
    savefig(fig, "assignment2_q3_pipeline_leakage.png")


def q4_drift_monitoring():
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Q4 — Drift monitoring, KS test, and red-teaming idea", fontsize=15, weight="bold", pad=10)

    # Left side: distributions compared
    add_box(ax, 0.04, 0.68, 0.18, 0.15, "Baseline\n(training window)", fc="#eef5ff")
    add_box(ax, 0.04, 0.46, 0.18, 0.15, "Live data\n(current window)", fc="#eef5ff")
    add_box(ax, 0.29, 0.58, 0.22, 0.16, "KS test\nD = max|F_train(x) - F_live(x)|", fc="#f7f7f7", weight="bold")
    add_arrow(ax, 0.22, 0.755, 0.29, 0.66)
    add_arrow(ax, 0.22, 0.535, 0.29, 0.66)
    ax.text(0.40, 0.40, "If p < 0.05: alert, investigate feature drift,\nretrain or rollback if needed.",
            ha="center", fontsize=11, color="crimson", weight="bold")

    # Right side: drift / red team
    add_box(ax, 0.60, 0.68, 0.16, 0.15, "Data drift\nP(X) changes", fc="#fff5e6")
    add_box(ax, 0.80, 0.68, 0.16, 0.15, "Concept drift\nP(Y|X) changes", fc="#fff5e6")
    ax.text(0.68, 0.55, "Red-teaming example:\nstress test with extreme but plausible events\n(e.g., festivals, storms, holidays, road closures)",
            ha="center", fontsize=11)
    add_box(ax, 0.63, 0.18, 0.30, 0.15, "Adversarial input in tabular regression:\n\nA plausible feature vector crafted to cause a large prediction error\nwhile staying within business / physical constraints.", fc="#f0fff0")
    savefig(fig, "assignment2_q4_drift_monitoring.png")


def main():
    q1_confusion_matrix()
    q2_rings_and_clustering()
    q3_pipeline_leakage()
    q4_drift_monitoring()
    print("Created 4 infographic PNG files in the current directory.")


if __name__ == "__main__":
    main()
