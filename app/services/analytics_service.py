from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Dict, List, Optional, Any

from app.models.player import Player
from app.models.performance import Performance


def get_player_metrics(db: Session, player_id: int) -> Optional[Dict[str, Any]]:
    """Compute advanced metrics for a player across all their performance records.

    Returns None if the player or their performances are not found.
    """
    player = (
        db.query(Player)
        .options(joinedload(Player.performances))
        .filter(Player.id == player_id)
        .first()
    )

    if not player:
        return None

    if not player.performances:
        return {
            "player_id": player.id,
            "name": player.name,
            "sport": player.sport,
            "position": player.position,
            "goals_per_90": 0.0,
            "assists_per_90": 0.0,
            "avg_efficiency": 0.0,
            "total_goal_contributions": 0,
            "minutes_per_match": 0.0,
            "avg_accuracy": 0.0,
            "avg_win_contribution": 0.0,
        }

    total_goals = sum(p.goals for p in player.performances)
    total_assists = sum(p.assists for p in player.performances)
    total_minutes = sum(p.minutes_played for p in player.performances)
    total_matches = sum(p.matches_played for p in player.performances)
    num_records = len(player.performances)

    goals_per_90 = round((total_goals / max(total_minutes, 1)) * 90, 4)
    assists_per_90 = round((total_assists / max(total_minutes, 1)) * 90, 4)
    avg_efficiency = round(sum(p.efficiency for p in player.performances) / num_records, 4)
    minutes_per_match = round(total_minutes / max(total_matches, 1), 2)
    avg_accuracy = round(sum(p.accuracy for p in player.performances) / num_records, 4)
    avg_win_contribution = round(
        sum(p.win_contribution for p in player.performances) / num_records, 4
    )

    return {
        "player_id": player.id,
        "name": player.name,
        "sport": player.sport,
        "position": player.position,
        "goals_per_90": goals_per_90,
        "assists_per_90": assists_per_90,
        "avg_efficiency": avg_efficiency,
        "total_goal_contributions": total_goals + total_assists,
        "minutes_per_match": minutes_per_match,
        "avg_accuracy": avg_accuracy,
        "avg_win_contribution": avg_win_contribution,
    }


# Metrics that map directly to Performance columns
_COLUMN_METRICS = {
    "goals": Performance.goals,
    "assists": Performance.assists,
    "efficiency": Performance.efficiency,
    "win_contribution": Performance.win_contribution,
    "accuracy": Performance.accuracy,
    "minutes_played": Performance.minutes_played,
}

# Computed metrics that require Python-level calculation
_COMPUTED_METRICS = {"goals_per_90", "assists_per_90"}

VALID_METRICS = set(_COLUMN_METRICS.keys()) | _COMPUTED_METRICS


def get_leaderboard(
    db: Session,
    metric: str,
    sport: Optional[str] = None,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """Return the top N players ranked by the given metric.

    For column-based metrics, ordering is done in SQL.
    For computed metrics (goals_per_90, assists_per_90), calculation is done in Python.
    """
    if metric not in VALID_METRICS:
        raise ValueError(
            f"Invalid metric '{metric}'. Valid metrics: {sorted(VALID_METRICS)}"
        )

    # Base query: join Player with Performance
    query = db.query(Player, Performance).join(
        Performance, Player.id == Performance.player_id
    )

    if sport:
        query = query.filter(Player.sport == sport)

    if metric in _COLUMN_METRICS:
        # SQL-level ordering
        column = _COLUMN_METRICS[metric]
        results = query.order_by(desc(column)).limit(top_n).all()

        return [
            {
                "rank": idx + 1,
                "player_id": player.id,
                "name": player.name,
                "sport": player.sport,
                "position": player.position,
                "value": round(getattr(perf, metric), 4),
            }
            for idx, (player, perf) in enumerate(results)
        ]

    # Computed metrics
    all_results = query.all()

    computed = []
    for player, perf in all_results:
        minutes = max(perf.minutes_played, 1)
        if metric == "goals_per_90":
            value = round((perf.goals / minutes) * 90, 4)
        elif metric == "assists_per_90":
            value = round((perf.assists / minutes) * 90, 4)
        else:
            value = 0.0

        computed.append({
            "rank": 0,  # will be set after sorting
            "player_id": player.id,
            "name": player.name,
            "sport": player.sport,
            "position": player.position,
            "value": value,
        })

    # Sort descending by value and take top_n
    computed.sort(key=lambda x: x["value"], reverse=True)
    for idx, entry in enumerate(computed[:top_n]):
        entry["rank"] = idx + 1

    return computed[:top_n]
