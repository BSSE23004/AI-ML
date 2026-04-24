# ============================================
# LAB 10: FULL MARKS SUBMISSION
# Model Optimization & Feature Engineering
# ============================================

import numpy as np
import pandas as pd
import optuna

from sklearn.model_selection import (
    GridSearchCV, RandomizedSearchCV,
    cross_val_score, train_test_split, KFold
)
from sklearn.tree import DecisionTreeClassifier

# =========================
# LOAD DATA
# =========================
def load_data(path="lab10_data.csv"):
    df = pd.read_csv(path)
    X = df.drop(columns=["target"])
    y = df["target"]
    return df, X, y

# =========================
# PART A: GRID SEARCH
# =========================
def run_grid_search(X, y):
    param_grid = {
        "max_depth": [2, 3, 4, 5, 6, 8, 10],
        "min_samples_split": [2, 5, 10, 20]
    }

    grid = GridSearchCV(
        DecisionTreeClassifier(),
        param_grid,
        cv=5,
        scoring="accuracy"
    )

    grid.fit(X, y)
    print("Grid Best Params:", grid.best_params_)
    return grid.best_estimator_

# =========================
# RANDOM SEARCH
# =========================
def run_random_search(X, y):
    param_dist = {
        "max_depth": np.arange(2, 15),
        "min_samples_split": np.arange(2, 20)
    }

    random = RandomizedSearchCV(
        DecisionTreeClassifier(),
        param_dist,
        n_iter=20,
        cv=5,
        scoring="accuracy",
        random_state=42
    )

    random.fit(X, y)
    print("Random Best Params:", random.best_params_)
    return random.best_estimator_

# =========================
# OPTUNA
# =========================
def run_optuna(X, y):

    def objective(trial):
        max_depth = trial.suggest_int("max_depth", 2, 15)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 20)

        model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split
        )

        score = cross_val_score(model, X, y, cv=5, scoring="accuracy").mean()
        return score

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)

    print("Optuna Best Params:", study.best_params)
    return study.best_params

# =========================
# PART B: CROSS VALIDATION
# =========================
def evaluate_cv(model, X, y):
    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    return scores.mean(), scores.std()

# =========================
# PART C: TARGET ENCODING
# =========================
def target_encode(df, column, target):
    means = df.groupby(column)[target].mean()
    return df[column].map(means)


def kfold_target_encode(df, column, target, n_splits=5):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    encoded = pd.Series(index=df.index, dtype=float)

    for train_idx, val_idx in kf.split(df):
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]

        means = train_df.groupby(column)[target].mean()
        encoded.iloc[val_idx] = val_df[column].map(means)

    return encoded.fillna(df[target].mean())

# =========================
# PART E: CYCLICAL FEATURES
# =========================
def encode_cyclical(feature, max_val):
    sin = np.sin(2 * np.pi * feature / max_val)
    cos = np.cos(2 * np.pi * feature / max_val)
    return sin, cos

# ============================================
# MAIN EXECUTION (ALL TASKS)
# ============================================
if __name__ == "__main__":

    df, X, y = load_data()

    # Encode categorical 'city' before any model training
    df_encoded = df.copy()
    df_encoded["city"] = df_encoded["city"].astype("category").cat.codes
    X = df_encoded.drop(columns=["target"])

    print("\n===== PART A: OPTIMIZATION =====")
    grid_model = run_grid_search(X, y)
    random_model = run_random_search(X, y)
    optuna_params = run_optuna(X, y)

    print("\n===== PART B: CROSS VALIDATION =====")
    mean, std = evaluate_cv(grid_model, X, y)
    print("CV Mean Accuracy:", mean)
    print("CV Std:", std)

    # Train/Test comparison
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    print("Train/Test Accuracy:", test_acc)

    print("\n===== PART C: TARGET ENCODING =====")
    df["city_naive"] = target_encode(df, "city", "target")
    df["city_kfold"] = kfold_target_encode(df, "city", "target")

    X_naive = df[["age", "income", "city_naive", "hour"]]
    X_kfold = df[["age", "income", "city_kfold", "hour"]]

    model = DecisionTreeClassifier()

    naive_score = cross_val_score(model, X_naive, y, cv=5).mean()
    kfold_score = cross_val_score(model, X_kfold, y, cv=5).mean()

    print("Naive Encoding Accuracy:", naive_score)
    print("KFold Encoding Accuracy:", kfold_score)

    print("\n===== PART E: CYCLICAL FEATURES =====")
    sin, cos = encode_cyclical(df["hour"], 24)
    df["hour_sin"] = sin
    df["hour_cos"] = cos

    X_raw = df[["age", "income", "city_kfold", "hour"]]
    X_cyc = df[["age", "income", "city_kfold", "hour_sin", "hour_cos"]]

    raw_score = cross_val_score(model, X_raw, y, cv=5).mean()
    cyc_score = cross_val_score(model, X_cyc, y, cv=5).mean()

    print("Raw Hour Accuracy:", raw_score)
    print("Cyclical Encoding Accuracy:", cyc_score)

    print("\n===== DONE: ALL TASKS COMPLETED =====")
