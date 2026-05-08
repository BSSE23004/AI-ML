"""
Lab 12: Model Deployment using Flask
Converted from Lab 11 FastAPI implementation.
"""

import os
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template

# ──────────────────────────────────────────
# Constants
# ──────────────────────────────────────────
MODEL_PATH = "model.joblib"

# ──────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────
app = Flask(__name__)

# Load the serialized model produced by Lab 11's run_pipeline()
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print(f"[Flask] Model loaded from '{MODEL_PATH}'")
else:
    model = None
    print(f"[Flask] WARNING: '{MODEL_PATH}' not found. Run Lab 11 pipeline first.")


# ──────────────────────────────────────────
# Routes
# ──────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    """
    Serve the prediction input form.
    On a fresh GET the result context is empty.
    """
    return render_template("./index.html", prediction=None, error=None, form_data=None)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accept form data or JSON, run inference, and return the result.

    Form fields  : age, income, hour, leak_feature
    JSON body    : { "features": [age, income, hour, leak_feature] }

    Returns HTML page (form POST) or JSON (Content-Type: application/json).
    """
    is_json = request.is_json

    # ── Model availability guard ──────────────────────────────────────────
    if model is None:
        msg = "Model not loaded. Generate 'model.joblib' by running Lab 11 pipeline."
        if is_json:
            return jsonify({"error": msg}), 503
        return render_template("index.html", prediction=None, error=msg, form_data=None)

    # ── Parse input ───────────────────────────────────────────────────────
    try:
        if is_json:
            data = request.get_json(force=True)
            if "features" not in data:
                return jsonify({"error": "Missing required key 'features'."}), 422
            features = np.array(data["features"], dtype=float).reshape(1, -1)
        else:
            age          = float(request.form["age"])
            income       = float(request.form["income"])
            hour         = float(request.form["hour"])
            leak_feature = float(request.form["leak_feature"])
            features     = np.array([[age, income, hour, leak_feature]])
            form_data    = {
                "age": age,
                "income": income,
                "hour": hour,
                "leak_feature": leak_feature,
            }

    except (KeyError, ValueError) as exc:
        err_msg = f"Invalid input: {exc}"
        if is_json:
            return jsonify({"error": err_msg}), 422
        return render_template("index.html", prediction=None, error=err_msg, form_data=None)

    # ── Inference ─────────────────────────────────────────────────────────
    prediction = int(model.predict(features)[0])
    label = "Class 1 — Positive" if prediction == 1 else "Class 0 — Negative"

    if is_json:
        return jsonify({"prediction": prediction})

    return render_template(
        "./index.html",
        prediction={"value": prediction, "label": label},
        error=None,
        form_data=form_data,
    )


# ──────────────────────────────────────────
# JSON API endpoint (mirrors FastAPI behaviour)
# ──────────────────────────────────────────

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Pure JSON prediction endpoint — mirrors the FastAPI /predict route from Lab 11.

    Expected body: { "features": [age, income, hour, leak_feature] }
    Returns      : { "prediction": 0 or 1 }
    """
    if model is None:
        return jsonify({"error": "Model not loaded."}), 503

    data = request.get_json(force=True, silent=True)
    if data is None or "features" not in data:
        return jsonify({"error": "Missing required key 'features' in request body."}), 422

    try:
        features = np.array(data["features"], dtype=float).reshape(1, -1)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid feature values: {exc}"}), 422

    prediction = int(model.predict(features)[0])
    return jsonify({"prediction": prediction})


# ──────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
