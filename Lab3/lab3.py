import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC


# ==========================================================
# PART A — DATASET
# ==========================================================

def generate_dataset(n=100, seed=42):
    """
    Generate a 2D linearly separable dataset.

    Requirements:
    - Use fixed random seed
    - Labels must be {-1, +1}
    - Return X (n,2), y (n,)
    """

    # TODO: Implement dataset generation
    pass


# ==========================================================
# PART B — TRAIN MAXIMUM MARGIN CLASSIFIER
# ==========================================================

def train_linear_svm(X, y):
    """
    Train a linear SVM using sklearn.

    Instructions:
    - Use kernel='linear'
    - Fit the model
    - Return trained model

    DO NOT modify dataset.
    """

    # TODO: Implement training
    pass


# ==========================================================
# PART C — EXTRACT PARAMETERS
# ==========================================================

def extract_parameters(model):
    """
    Extract:
        w (weight vector)
        b (bias term)

    Hint:
        model.coef_
        model.intercept_

    Return:
        w, b
    """

    # TODO
    pass


# ==========================================================
# PART D — CONSTRAINT VERIFICATION
# ==========================================================

def compute_margins(X, y, w, b):
    """
    Compute:
        y_i (w^T x_i + b)

    Return:
        array of margins
    """

    # TODO
    pass


def verify_constraints(margins):
    """
    Print:
        - Minimum margin value
        - Whether all margins >= 1

    DO NOT modify margins.
    """

    # TODO
    pass


# ==========================================================
# PART E — GEOMETRIC MARGIN WIDTH
# ==========================================================

def compute_margin_width(w):
    """
    Compute geometric margin width:

        2 / ||w||

    Return scalar.
    """

    # TODO
    pass


# ==========================================================
# PART F — SUPPORT VECTORS
# ==========================================================

def analyze_support_vectors(model, X, y, w, b):
    """
    Tasks:

    1. Print indices of support vectors.
    2. Print number of support vectors.
    3. Verify numerically that support vectors
       approximately satisfy:

            y_i (w^T x_i + b) ≈ 1

    """

    # TODO
    pass


# ==========================================================
# PART G — REMOVE ONE SUPPORT VECTOR
# ==========================================================

def remove_one_support_vector(model, X, y):
    """
    Remove the first support vector from dataset.

    Steps:
    1. Identify index using model.support_
    2. Remove from X and y
    3. Return new X, y

    DO NOT retrain inside this function.
    """

    # TODO
    pass


# ==========================================================
# PART H — SCALING EXPERIMENT
# ==========================================================

def scale_dataset(X, factor):
    """
    Multiply features by scaling factor.

    Return scaled X.
    """

    # TODO
    pass


# ==========================================================
# PLOTTING UTILITY (Provided)
# ==========================================================

def plot_model(X, y, model, title="Model"):
    """
    Provided plotting function.
    Students should call this,
    not modify it.
    """

    plt.figure()

    plt.scatter(X[:, 0], X[:, 1], c=y)

    w = model.coef_[0]
    b = model.intercept_[0]

    x_vals = np.linspace(X[:, 0].min(), X[:, 0].max(), 100)
    y_vals = -(w[0] * x_vals + b) / w[1]

    plt.plot(x_vals, y_vals)

    # Margin lines
    y_margin1 = -(w[0]*x_vals + b - 1) / w[1]
    y_margin2 = -(w[0]*x_vals + b + 1) / w[1]

    plt.plot(x_vals, y_margin1, linestyle='--')
    plt.plot(x_vals, y_margin2, linestyle='--')

    # Highlight support vectors
    plt.scatter(model.support_vectors_[:, 0],
                model.support_vectors_[:, 1],
                s=150,
                facecolors='none',
                edgecolors='black')

    plt.title(title)
    plt.show()


# ==========================================================
# MAIN BLOCK (Students Complete Sequentially)
# ==========================================================

if __name__ == "__main__":

    # Step 1
    X, y = generate_dataset()

    # Step 2
    model = train_linear_svm(X, y)

    # Step 3
    w, b = extract_parameters(model)

    # Step 4
    margins = compute_margins(X, y, w, b)
    verify_constraints(margins)

    # Step 5
    margin_width = compute_margin_width(w)
    print("Geometric margin width:", margin_width)

    # Step 6
    analyze_support_vectors(model, X, y, w, b)

    # Step 7
    X_new, y_new = remove_one_support_vector(model, X, y)
    model_new = train_linear_svm(X_new, y_new)
    plot_model(X_new, y_new, model_new, title="After Removing Support Vector")

    # Step 8
    X_scaled = scale_dataset(X, factor=10)
    model_scaled = train_linear_svm(X_scaled, y)
    plot_model(X_scaled, y, model_scaled, title="After Scaling")