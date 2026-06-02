"""ML predictor module for player scoring.

Loads a trained model from disk and exposes a prediction interface
used by the selection service when use_ml=True.
"""

import os
import pickle
import logging
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "selection_model.pkl",
)

# Feature order must match what the training script uses
FEATURE_ORDER = [
    "goals",
    "assists",
    "efficiency",
    "minutes_played",
    "matches_played",
    "accuracy",
    "win_contribution",
]

_model = None
_model_loaded = False


def _load_model():
    """Lazy-load the model from disk."""
    global _model, _model_loaded
    if _model_loaded:
        return _model

    _model_loaded = True
    if not os.path.exists(MODEL_PATH):
        logger.info(f"No model file found at {MODEL_PATH}")
        _model = None
        return _model

    try:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        logger.info(f"ML model loaded from {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        _model = None

    return _model


def is_model_available() -> bool:
    """Check whether a trained model is available."""
    model = _load_model()
    return model is not None


def predict_score(features: Dict[str, float]) -> float:
    """Predict a player score from performance features.

    Args:
        features: Dict with keys matching FEATURE_ORDER.

    Returns:
        Predicted score as a float, or 0.0 if the model is unavailable.
    """
    model = _load_model()
    if model is None:
        return 0.0

    try:
        X = np.array([[features.get(f, 0.0) for f in FEATURE_ORDER]])
        prediction = model.predict(X)[0]
        return round(float(prediction), 4)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return 0.0


def reload_model() -> bool:
    """Force reload the model from disk. Returns True if loaded successfully."""
    global _model, _model_loaded
    _model = None
    _model_loaded = False
    return is_model_available()
