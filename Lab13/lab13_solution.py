"""
Lab 13: Drift Detection in Streaming Data
==========================================
Department of Computer and Software Engineering
SE: Machine Learning

Instructions
------------
- Complete EVERY function marked with # TODO.
- Do NOT rename any function or change its parameters or return types.
- Do NOT remove or reorder the import statements.
- You may add private helper functions anywhere below the imports.
- Run   pytest test_student.py -v   to check your work before submission.

Dataset
-------
File   : transactions_with_drift.xlsx
Sheets :
    All_Transactions           full 6-month dataset  (use for batch splitting)
    Baseline_M1_M3             months 1-3 only        (use as reference)
    Drift_Summary_Ground_Truth per-month true stats   (check AFTER all tasks)

Required packages
-----------------
    pip install pandas numpy scipy scikit-learn openpyxl matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------
# Constants — do not change these
# ------------------------------------------------------------------
DATASET_PATH = "transactions_with_drift.xlsx"
FEATURES     = ["transaction_amount", "customer_age",
                "transaction_hour",   "device_risk_score"]
TARGET       = "is_fraud"


# ==================================================================
# PART A — STREAMING DATA SIMULATION
# ==================================================================

def task1_baseline_stats(baseline_df):
    """
    Task 1: Compute summary statistics for the baseline dataset.
    """
    stats = {}
    for feat in FEATURES:
        col = baseline_df[feat]
        stats[feat] = {
            'mean': float(col.mean()),
            'std':  float(col.std()),
            'min':  float(col.min()),
            'max':  float(col.max()),
        }
    stats['fraud_rate'] = float(baseline_df[TARGET].mean())
    return stats


def task2_split_batches(all_df):
    """
    Task 2: Split the full dataset into six monthly batches.
    """
    batches = {}
    for month in range(1, 7):
        batches[month] = all_df[all_df['month'] == month].copy()

    # Plot: mean of transaction_amount and transaction_hour per month
    months = list(range(1, 7))
    amount_means = [batches[m]['transaction_amount'].mean() for m in months]
    hour_means   = [batches[m]['transaction_hour'].mean()   for m in months]

    fig, axes = plt.subplots(2, 1, figsize=(9, 6))
    axes[0].plot(months, amount_means, marker='o', color='steelblue')
    axes[0].set_title('Mean Transaction Amount per Month')
    axes[0].set_xlabel('Month')
    axes[0].set_ylabel('Mean Amount (USD)')
    axes[0].set_xticks(months)

    axes[1].plot(months, hour_means, marker='o', color='darkorange')
    axes[1].set_title('Mean Transaction Hour per Month')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Mean Hour (0-23)')
    axes[1].set_xticks(months)

    plt.tight_layout()
    plt.savefig('task2_batch_means.png', dpi=150)
    plt.close()

    return batches


# ==================================================================
# PART B — THRESHOLD-BASED DRIFT DETECTION
# ==================================================================

def task3_mean_shift_detection(batches, baseline_stats):
    """
    Task 3: Flag monthly batches using the 2-sigma mean-shift rule.
    """
    mu    = baseline_stats['transaction_amount']['mean']
    sigma = baseline_stats['transaction_amount']['std']
    alerts = {}
    for month in range(1, 7):
        batch_mean = batches[month]['transaction_amount'].mean()
        alerts[month] = bool(abs(batch_mean - mu) > 2 * sigma)
    return alerts


def task4_drift_log(batches, baseline_stats, alerts):
    """
    Task 4: Build a structured log of drift events.
    """
    mu    = baseline_stats['transaction_amount']['mean']
    sigma = baseline_stats['transaction_amount']['std']
    log   = []

    for month in sorted(alerts.keys()):
        if alerts[month]:
            batch_mean      = float(batches[month]['transaction_amount'].mean())
            shift_magnitude = abs(batch_mean - mu)
            sigmas_away     = shift_magnitude / sigma
            # Get the most common drift_phase label in this batch
            drift_phase = batches[month]['drift_phase'].mode()[0]
            log.append({
                'month':           month,
                'drift_phase':     drift_phase,
                'batch_mean':      batch_mean,
                'shift_magnitude': float(shift_magnitude),
                'sigmas_away':     float(sigmas_away),
            })

    # Print readable table
    print("\n=== Drift Event Log ===")
    header = f"{'Month':>6}  {'Drift Phase':<20}  {'Batch Mean':>12}  {'Shift Mag':>10}  {'Sigmas Away':>12}"
    print(header)
    print('-' * len(header))
    for e in log:
        print(f"{e['month']:>6}  {e['drift_phase']:<20}  "
              f"{e['batch_mean']:>12.2f}  {e['shift_magnitude']:>10.2f}  "
              f"{e['sigmas_away']:>12.3f}")

    return log


# ==================================================================
# PART C — KS TEST
# ==================================================================

def task5_ks_test(batches, baseline_df):
    """
    Task 5: Apply the KS test to detect distribution shifts.
    """
    baseline_vals = baseline_df['transaction_amount'].values
    ks_results = {}
    for month in range(1, 7):
        batch_vals = batches[month]['transaction_amount'].values
        stat, pval = ks_2samp(baseline_vals, batch_vals)
        ks_results[month] = {
            'ks_stat': float(stat),
            'p_value': float(pval),
            'drifted': bool(pval < 0.05),
        }
    return ks_results


def task6_method_comparison(alerts, ks_results):
    """
    Task 6: Side-by-side comparison of the two detection methods.
    """
    comparison = []
    for month in range(1, 7):
        comparison.append({
            'month':            month,
            'mean_shift_alert': alerts[month],
            'ks_alert':         ks_results[month]['drifted'],
            'ks_stat':          ks_results[month]['ks_stat'],
            'p_value':          ks_results[month]['p_value'],
        })

    # Print readable table
    print("\n=== Method Comparison ===")
    header = f"{'Month':>6}  {'Mean-Shift Alert':>17}  {'KS Alert':>9}  {'KS Stat':>9}  {'p-value':>10}"
    print(header)
    print('-' * len(header))
    for e in comparison:
        print(f"{e['month']:>6}  {str(e['mean_shift_alert']):>17}  "
              f"{str(e['ks_alert']):>9}  {e['ks_stat']:>9.4f}  {e['p_value']:>10.4f}")

    return comparison


# ==================================================================
# PART D — CONCEPT DRIFT
# ==================================================================

def task7_train_baseline_model(baseline_df):
    """
    Task 7: Train a Logistic Regression classifier on the baseline data.
    """
    X = baseline_df[FEATURES].values
    y = baseline_df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    y_pred   = model.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    f1       = float(f1_score(y_test, y_pred))

    return model, scaler, accuracy, f1


def task8_evaluate_on_batches(model, scaler, batches):
    """
    Task 8: Evaluate the baseline model on each monthly batch.
    """
    performance = {}
    for month in range(1, 7):
        X = scaler.transform(batches[month][FEATURES].values)
        y = batches[month][TARGET].values
        y_pred = model.predict(X)
        performance[month] = {
            'accuracy': float(accuracy_score(y, y_pred)),
            'f1':       float(f1_score(y, y_pred, zero_division=0)),
        }
    return performance


# ==================================================================
# PART E — VISUALIZATION
# ==================================================================

def task9_drift_dashboard(batches, baseline_stats, alerts,
                           ks_results, performance):
    """
    Task 9: Produce a 4-subplot drift dashboard and save it.
    """
    months = list(range(1, 7))

    amount_means = [batches[m]['transaction_amount'].mean() for m in months]
    fraud_rates  = [batches[m][TARGET].mean()               for m in months]
    ks_stats     = [ks_results[m]['ks_stat']                for m in months]
    f1_scores    = [performance[m]['f1']                    for m in months]

    mu    = baseline_stats['transaction_amount']['mean']
    sigma = baseline_stats['transaction_amount']['std']
    upper = mu + 2 * sigma
    lower = mu - 2 * sigma

    fig, axes = plt.subplots(4, 1, figsize=(11, 14))
    fig.suptitle('Lab 13 — Drift Detection Dashboard', fontsize=14, fontweight='bold')

    def shade_background(ax):
        # Months 4-5: Feature Drift (light yellow)
        ax.axvspan(3.5, 5.5, alpha=0.25, color='gold',       label='Feature Drift (M4-5)')
        # Month 6: Concept Drift (light red)
        ax.axvspan(5.5, 6.5, alpha=0.25, color='tomato',     label='Concept Drift (M6)')

    # --- Subplot 1: Mean transaction_amount ---
    ax = axes[0]
    shade_background(ax)
    ax.plot(months, amount_means, marker='o', color='steelblue', linewidth=2, label='Batch Mean')
    ax.axhline(upper, linestyle='--', color='red',   linewidth=1.2, label=f'μ+2σ ({upper:.0f})')
    ax.axhline(lower, linestyle='--', color='green', linewidth=1.2, label=f'μ-2σ ({lower:.0f})')
    ax.axhline(mu,    linestyle=':',  color='grey',  linewidth=1.0, label=f'Baseline μ ({mu:.0f})')
    ax.set_title('Mean Transaction Amount per Month')
    ax.set_ylabel('Mean Amount (USD)')
    ax.set_xticks(months)
    ax.legend(fontsize=7, loc='upper left')

    # --- Subplot 2: KS statistic ---
    ax = axes[1]
    shade_background(ax)
    ax.bar(months, ks_stats, color=['tomato' if ks_results[m]['drifted'] else 'steelblue'
                                     for m in months], edgecolor='black', linewidth=0.6)
    ax.axhline(0.05, linestyle='--', color='red', linewidth=1.2, label='p=0.05 boundary')
    for m in months:
        if ks_results[m]['drifted']:
            ax.annotate('DRIFT', xy=(m, ks_stats[m-1]),
                        xytext=(0, 4), textcoords='offset points',
                        ha='center', fontsize=7, color='darkred', fontweight='bold')
    ax.set_title('KS Statistic per Month (red = drifted, p<0.05)')
    ax.set_ylabel('KS Statistic')
    ax.set_xticks(months)
    ax.legend(fontsize=7)

    # --- Subplot 3: Fraud rate ---
    ax = axes[2]
    shade_background(ax)
    ax.plot(months, fraud_rates, marker='s', color='darkorange', linewidth=2, label='Fraud Rate')
    ax.set_title('Fraud Rate per Month')
    ax.set_ylabel('Fraud Rate')
    ax.set_xticks(months)
    ax.legend(fontsize=7)

    # --- Subplot 4: Model F1-score ---
    ax = axes[3]
    shade_background(ax)
    ax.plot(months, f1_scores, marker='^', color='purple', linewidth=2, label='F1-Score')
    ax.set_title('Model F1-Score per Month (baseline model, no retraining)')
    ax.set_ylabel('F1-Score')
    ax.set_xlabel('Month')
    ax.set_xticks(months)
    ax.legend(fontsize=7)

    plt.tight_layout()
    plt.savefig('task9_drift_dashboard.png', dpi=150)
    plt.close()


# ==================================================================
# MAIN — end-to-end pipeline (runs when you execute this file)
# ==================================================================

if __name__ == "__main__":
    # Load sheets
    baseline_df = pd.read_excel(DATASET_PATH, sheet_name="Baseline_M1_M3")
    all_df      = pd.read_excel(DATASET_PATH, sheet_name="All_Transactions")

    # Part A
    stats   = task1_baseline_stats(baseline_df)
    batches = task2_split_batches(all_df)

    print("\n=== Task 1: Baseline Statistics ===")
    for feat in FEATURES:
        s = stats[feat]
        print(f"  {feat}: mean={s['mean']:.3f}, std={s['std']:.3f}, "
              f"min={s['min']:.3f}, max={s['max']:.3f}")
    print(f"  Fraud rate: {stats['fraud_rate']:.4f}")

    print("\n=== Task 2: Monthly Batch Sizes ===")
    for m, df in batches.items():
        print(f"  Month {m}: {len(df)} rows | "
              f"amount_mean={df['transaction_amount'].mean():.2f} | "
              f"hour_mean={df['transaction_hour'].mean():.2f}")

    # Part B
    alerts  = task3_mean_shift_detection(batches, stats)
    log     = task4_drift_log(batches, stats, alerts)

    print("\n=== Task 3: Mean-Shift Alerts ===")
    for m, v in alerts.items():
        print(f"  Month {m}: {'ALERT' if v else 'ok'}")

    # Part C
    ks_results = task5_ks_test(batches, baseline_df)
    comparison = task6_method_comparison(alerts, ks_results)

    print("\n=== Task 5: KS Test Results ===")
    for m, r in ks_results.items():
        print(f"  Month {m}: KS={r['ks_stat']:.4f}, p={r['p_value']:.4f}, "
              f"drifted={r['drifted']}")

    # Part D
    model, scaler, acc, f1 = task7_train_baseline_model(baseline_df)
    performance = task8_evaluate_on_batches(model, scaler, batches)

    print("\n=== Task 8: Model Performance per Month ===")
    for m, p in performance.items():
        print(f"  Month {m}: Accuracy={p['accuracy']:.4f}, F1={p['f1']:.4f}")

    # Part E
    task9_drift_dashboard(batches, stats, alerts, ks_results, performance)

    print("\n--- Pipeline complete ---")
    print(f"Baseline model  Accuracy: {acc:.4f}   F1: {f1:.4f}")
    print(f"Mean-shift alerts : {[m for m, v in alerts.items() if v]}")
    print(f"KS-test alerts    : {[m for m, v in ks_results.items() if v['drifted']]}")

    # ==================================================================
    # RUN PYTEST TESTS (Optional)
    # ==================================================================
    print("\n\n" + "="*70)
    print("Running pytest tests from lab13_student.py...")
    print("="*70)
    
    try:
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "lab13_student.py", "-v"],
            cwd="/home/ibrahim/Git/AI-ML/Lab13",
            capture_output=False
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Warning: Could not run pytest tests: {e}")
        print("To run tests manually, execute: pytest lab13_student.py -v")
