"""Train a simple ML model for player scoring.

Reads performance data from the database, trains a RandomForestRegressor,
and saves the model to models/selection_model.pkl.

Usage:
    python -m scripts.train_model
"""

import os
import sys
import pickle

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal
from app.models.performance import Performance


FEATURE_COLUMNS = [
    "goals",
    "assists",
    "efficiency",
    "minutes_played",
    "matches_played",
    "accuracy",
    "win_contribution",
]

# Target: win_contribution is used as the label for scoring predictions
TARGET_COLUMN = "win_contribution"

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "selection_model.pkl")


def load_data():
    """Load all performance records from the database."""
    db = SessionLocal()
    try:
        performances = db.query(Performance).all()
        if not performances:
            print("No performance data found. Run seed_mock_data.py first.")
            sys.exit(1)

        X = []
        y = []
        for p in performances:
            features = [getattr(p, col) for col in FEATURE_COLUMNS]
            target = getattr(p, TARGET_COLUMN)
            X.append(features)
            y.append(target)

        return np.array(X), np.array(y)
    finally:
        db.close()


def train():
    """Train the model and save to disk."""
    print("Loading data from database...")
    X, y = load_data()
    print(f"Loaded {len(X)} performance records with {len(FEATURE_COLUMNS)} features")

    if len(X) < 4:
        print(f"Warning: Only {len(X)} samples — training on all data (no test split)")
        X_train, X_test, y_train, y_test = X, X, y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )

    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"\nResults:")
    print(f"  R² Score:           {r2:.4f}")
    print(f"  Mean Absolute Error: {mae:.4f}")
    print(f"  Training samples:   {len(X_train)}")
    print(f"  Test samples:       {len(X_test)}")

    # Feature importance
    print(f"\nFeature Importances:")
    for name, importance in sorted(
        zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:20s} {importance:.4f}")

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
