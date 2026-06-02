from sqlalchemy.orm import Session, joinedload
from typing import Dict, List, Optional
import logging

from app.models.player import Player
from app.models.performance import Performance

logger = logging.getLogger(__name__)

# Default scoring weights
DEFAULT_WEIGHTS: Dict[str, float] = {
    "goals": 3.0,
    "assists": 2.0,
    "efficiency": 1.5,
    "minutes": 0.5,
}


def score_player(
    player: Player, performance: Performance, weights: Dict[str, float]
) -> float:
    """Calculate a deterministic score for a player based on performance data.

    Formula:
        base = goals*Wg + assists*Wa + efficiency*We + (minutes_played/90)*Wm
        score = base / max(matches_played, 1)
    """
    w = {**DEFAULT_WEIGHTS, **weights}  # merge with defaults

    base_score = (
        performance.goals * w.get("goals", 0)
        + performance.assists * w.get("assists", 0)
        + performance.efficiency * w.get("efficiency", 0)
        + (performance.minutes_played / 90.0) * w.get("minutes", 0)
    )

    matches = max(performance.matches_played, 1)
    return round(base_score / matches, 4)


def _score_player_ml(performance: Performance) -> float:
    """Score a player using the ML model. Falls back to 0.0 if unavailable."""
    try:
        from app.ml.predictor import predict_score, is_model_available

        if not is_model_available():
            logger.warning("ML model not available, returning 0.0")
            return 0.0

        features = {
            "goals": performance.goals,
            "assists": performance.assists,
            "efficiency": performance.efficiency,
            "minutes_played": performance.minutes_played,
            "matches_played": performance.matches_played,
            "accuracy": performance.accuracy,
            "win_contribution": performance.win_contribution,
        }
        return predict_score(features)
    except Exception as e:
        logger.error(f"ML prediction failed: {e}")
        return 0.0


def select_team(
    db: Session,
    sport: str,
    team_size: int,
    position_limits: Dict[str, int],
    weights: Optional[Dict[str, float]] = None,
    use_ml: bool = False,
) -> List[dict]:
    """Select the best team based on scores and position constraints.

    Uses a greedy approach: score all players, sort descending, then fill
    each position slot with the highest-scoring available player.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Query players for the given sport with their performances
    players = (
        db.query(Player)
        .options(joinedload(Player.performances))
        .filter(Player.sport == sport)
        .all()
    )

    # Score each player using their best (most recent) performance
    scored_players = []
    for player in players:
        if not player.performances:
            continue

        # Use the performance with the most matches played (most data)
        best_perf = max(player.performances, key=lambda p: p.matches_played)

        if use_ml:
            score = _score_player_ml(best_perf)
            # If ML returned 0, fall back to deterministic
            if score == 0.0:
                score = score_player(player, best_perf, weights)
                scoring_method = "deterministic_fallback"
            else:
                scoring_method = "ml"
        else:
            score = score_player(player, best_perf, weights)
            scoring_method = "deterministic"

        scored_players.append({
            "player": player,
            "performance": best_perf,
            "score": score,
            "scoring_method": scoring_method,
        })

    # Sort by score descending
    scored_players.sort(key=lambda x: x["score"], reverse=True)

    # Greedy position-constrained selection
    selected = []
    position_slots = dict(position_limits)  # copy

    for entry in scored_players:
        if len(selected) >= team_size:
            break

        player_position = entry["player"].position
        if position_slots.get(player_position, 0) > 0:
            selected.append(entry)
            position_slots[player_position] -= 1

    return selected
