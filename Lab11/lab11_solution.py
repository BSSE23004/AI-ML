# ============================================================
# Lab 11: Refactoring, MLflow, Serialization & FastAPI Deployment
# ============================================================

# ============================================================
# Imports
# ============================================================
import os
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from fastapi import FastAPI, HTTPException

# ============================================================
# Constants
# ============================================================
DATA_PATH = "lab10_data.csv"
MODEL_PATH = "model.joblib"
expected_accuracy = 0.8


# ============================================================
# Part A — Refactored ML Pipeline
# ============================================================

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load the dataset from the CSV file.

    Args:
        path (str): Path to the CSV file. Defaults to 'lab10_data.csv'.

    Returns:
        pd.DataFrame: The loaded dataframe.
    """
    df = pd.read_csv(path)
    return df


def preprocess_data(df: pd.DataFrame):
    """
    Preprocess the input dataframe:
      - Drop the categorical 'city' column.
      - Separate features (X) and target (y).

    Args:
        df (pd.DataFrame): Raw dataframe loaded from CSV.

    Returns:
        tuple: (X, y) where X is the feature DataFrame and y is the target Series.
    """
    df = df.drop(columns=["city"])
    X = df.drop(columns=["target"])
    y = df["target"]
    return X, y


def train_model(X, y) -> DecisionTreeClassifier:
    """
    Train a DecisionTreeClassifier on the provided data.

    Args:
        X: Feature matrix (DataFrame or ndarray).
        y: Target vector (Series or ndarray).

    Returns:
        DecisionTreeClassifier: The fitted model.
    """
    model = DecisionTreeClassifier(
        max_depth=5,
        criterion="gini",
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
    )
    model.fit(X, y)
    return model


def evaluate_model(model, X, y) -> float:
    """
    Evaluate the trained model and return the accuracy score.

    Args:
        model: A fitted sklearn model.
        X: Feature matrix.
        y: True target values.

    Returns:
        float: Accuracy score (0.0 – 1.0).
    """
    predictions = model.predict(X)
    acc = accuracy_score(y, predictions)
    return acc


def run_pipeline() -> float:
    """
    Orchestrate the full ML pipeline:
      1. Load data
      2. Preprocess
      3. Train model (logged via MLflow)
      4. Evaluate (logged via MLflow)
      5. Save model to disk with joblib

    Returns:
        float: Training accuracy of the model.
    """
    # --- Load & preprocess ---
    df = load_data()
    X, y = preprocess_data(df)

    # --- MLflow experiment tracking (Part B) ---
    mlflow.set_experiment("lab11_experiment")

    with mlflow.start_run():
        # Train
        model = train_model(X, y)

        # Log hyperparameters
        mlflow.log_param("max_depth", model.max_depth)
        mlflow.log_param("criterion", model.criterion)
        mlflow.log_param("min_samples_split", model.min_samples_split)
        mlflow.log_param("min_samples_leaf", model.min_samples_leaf)
        mlflow.log_param("random_state", model.random_state)

        # Evaluate
        acc = evaluate_model(model, X, y)

        # Log metric
        mlflow.log_metric("accuracy", acc)

        # Log model as MLflow artifact
        mlflow.sklearn.log_model(model, artifact_path="decision_tree_model")

        print(f"[MLflow] Run logged — accuracy: {acc:.4f}")

    # --- Serialization (Part C) ---
    joblib.dump(model, MODEL_PATH)
    print(f"[joblib] Model saved to '{MODEL_PATH}'")

    assert acc >= expected_accuracy, (
        f"Accuracy {acc:.4f} is below the required threshold of {expected_accuracy}"
    )

    return acc


# ============================================================
# Part D — FastAPI Application
# ============================================================

app = FastAPI(title="Lab 11 ML API")

# Load serialized model at startup (Part C)
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print(f"[FastAPI] Model loaded from '{MODEL_PATH}'")
else:
    # Model not on disk yet — will be None until run_pipeline() is called
    model = None


@app.get("/")
def home():
    """Health-check endpoint."""
    return {"message": "ML Model API is running"}


@app.post("/predict")
def predict(data: dict):
    """
    Run inference for a single sample.

    Expected JSON body:
        { "features": [age, income, hour, leak_feature] }

    Returns:
        dict: { "prediction": 0 or 1 }
    """
    # 503 — model not loaded
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run the pipeline first to generate 'model.joblib'.",
        )

    # 422 — missing 'features' key
    if "features" not in data:
        raise HTTPException(
            status_code=422,
            detail="Missing required key 'features' in request body.",
        )

    features = np.array(data["features"]).reshape(1, -1)
    prediction = model.predict(features)
    return {"prediction": int(prediction[0])}

from fastapi.testclient import TestClient

client = TestClient(app)

# ── Test 1: Young low-income person, off-hours → likely class 0
r = client.post("/predict", json={"features": [22, 15000, 2, -0.05]})
print("Test 1 | age=22, income=15000, hour=2,  leak=-0.05 →", r.json())

# ── Test 2: Middle-aged high-income, peak hours → likely class 1
r = client.post("/predict", json={"features": [40, 85000, 14, 1.02]})
print("Test 2 | age=40, income=85000, hour=14, leak=1.02  →", r.json())

# ── Test 3: Senior, moderate income, evening
r = client.post("/predict", json={"features": [60, 42000, 20, 0.50]})
print("Test 3 | age=60, income=42000, hour=20, leak=0.50  →", r.json())

# ── Test 4: Edge case — missing 'features' key, should return 422
r = client.post("/predict", json={"data": [30, 50000, 10, 0.8]})
print("Test 4 | wrong key 'data' → status:", r.status_code, r.json())


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Running ML Pipeline...")
    print("=" * 60)
    acc = run_pipeline()
    print(f"Pipeline complete. Training Accuracy: {acc:.4f}")
    print()
    print("=" * 60)
    print("Starting FastAPI server at http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run("lab11_solution:app", host="127.0.0.1", port=8000, reload=False)
