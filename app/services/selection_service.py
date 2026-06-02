"""
Selection Service
=================
Implements two scoring modes:

1. **Cricket formula** (when sport == "Cricket"):
   - Fitness Category    = 0.4·fitness_score + 0.3·stamina + 0.2·speed + 0.1·training_attendance
   - Fatigue Category    = 0.5·fatigue_index  + 0.3·recovery_score + 0.2·workload_score
   - Injury Category     = 0.5·current_injury_status + 0.3·injury_history + 0.2·days_since_last_injury
   - Performance Category= 0.3·last_3_score   + 0.3·last_5_score + 0.4·consistency
   - Team Req Category   = 0.5·role_match      + 0.3·team_balance_need + 0.2·versatility
   - Player Score        = 0.30·Fit + 0.20·Fat + 0.15·Inj + 0.25·Perf + 0.10·TeamReq

2. **Generic formula** (all other sports):
   - Weighted goals, assists, efficiency, minutes per match.
"""

from sqlalchemy.orm import Session, joinedload
from typing import Dict, List, Optional
import logging

from app.models.player import Player
from app.models.performance import Performance

logger = logging.getLogger(__name__)

# ─── Generic weights ──────────────────────────────────────────────────────────

DEFAULT_WEIGHTS: Dict[str, float] = {
    "goals": 3.0,
    "assists": 2.0,
    "efficiency": 1.5,
    "minutes": 0.5,
}

# ─── Score Breakdown helper ───────────────────────────────────────────────────

def _make_breakdown(fit: float, fat: float, inj: float, perf: float, team: float, overall: float, reason: str) -> dict:
    return {
        "fitness_category": round(fit, 3),
        "fatigue_category": round(fat, 3),
        "injury_category": round(inj, 3),
        "performance_category": round(perf, 3),
        "team_requirement_category": round(team, 3),
        "overall_score": round(overall, 4),
        "selection_reason": reason,
    }


# ─── Cricket Scoring ──────────────────────────────────────────────────────────

def score_cricket_player(performance: Performance) -> tuple[float, dict]:
    """
    Compute cricket player score using the 5-category formula.
    Returns (overall_score, breakdown_dict).

    NOTE: Fatigue and Injury are inverted — lower raw values = WORSE for the player.
    We treat all stored values as 0-100 where higher = better already (normalised at seed time).
    """
    p = performance

    # Category scores (all 0-100 scale)
    fitness = 0.4 * p.fitness_score + 0.3 * p.stamina + 0.2 * p.speed + 0.1 * p.training_attendance
    fatigue  = 0.5 * p.fatigue_index + 0.3 * p.recovery_score + 0.2 * p.workload_score
    injury   = 0.5 * p.current_injury_status + 0.3 * p.injury_history + 0.2 * p.days_since_last_injury
    perf_cat = 0.3 * p.last_3_score + 0.3 * p.last_5_score + 0.4 * p.consistency
    team_req = 0.5 * p.role_match + 0.3 * p.team_balance_need + 0.2 * p.versatility

    overall = (
        0.30 * fitness
        + 0.20 * fatigue
        + 0.15 * injury
        + 0.25 * perf_cat
        + 0.10 * team_req
    )

    # Build a human-readable reason
    reason_parts = []
    if fitness >= 75:
        reason_parts.append(f"high fitness ({fitness:.1f}/100)")
    elif fitness < 50:
        reason_parts.append(f"low fitness ({fitness:.1f}/100)")

    if fatigue >= 70:
        reason_parts.append(f"good recovery ({fatigue:.1f}/100)")
    elif fatigue < 45:
        reason_parts.append(f"fatigued ({fatigue:.1f}/100)")

    if injury >= 70:
        reason_parts.append("fully fit (no injury risk)")
    elif injury < 45:
        reason_parts.append("injury concern")

    if perf_cat >= 75:
        reason_parts.append(f"strong recent form ({perf_cat:.1f}/100)")
    elif perf_cat < 50:
        reason_parts.append(f"poor recent form ({perf_cat:.1f}/100)")

    reason = "Selected because: " + ", ".join(reason_parts) if reason_parts else "Balanced profile across all categories"

    breakdown = _make_breakdown(fitness, fatigue, injury, perf_cat, team_req, overall, reason)
    return round(overall, 4), breakdown


# ─── Generic Scoring ──────────────────────────────────────────────────────────

def score_generic_player(player: Player, performance: Performance, weights: Dict[str, float]) -> tuple[float, dict]:
    """Score a player for non-cricket sports using weighted stats."""
    w = {**DEFAULT_WEIGHTS, **weights}

    base = (
        performance.goals * w.get("goals", 0)
        + performance.assists * w.get("assists", 0)
        + performance.efficiency * w.get("efficiency", 0)
        + (performance.minutes_played / 90.0) * w.get("minutes", 0)
    )
    matches = max(performance.matches_played, 1)
    overall = round(base / matches, 4)

    # Use stored advanced metrics as proxies if they exist, else fall back to 50
    fitness  = performance.fitness_score or 50.0
    fatigue  = performance.fatigue_index or 50.0
    injury   = performance.current_injury_status or 50.0
    perf_cat = performance.consistency or 50.0
    team_req = performance.role_match or 50.0

    reason_parts = []
    if performance.goals > 0:
        reason_parts.append(f"{performance.goals} goals")
    if performance.assists > 0:
        reason_parts.append(f"{performance.assists} assists")
    if performance.efficiency >= 85:
        reason_parts.append(f"high efficiency ({performance.efficiency:.1f}%)")
    reason = "Selected because: " + ", ".join(reason_parts) if reason_parts else "Best available for position"

    breakdown = _make_breakdown(fitness, fatigue, injury, perf_cat, team_req, overall, reason)
    return overall, breakdown


# ─── Team Selection ───────────────────────────────────────────────────────────

def select_team(
    db: Session,
    sport: str,
    team_size: int,
    position_limits: Dict[str, int],
    weights: Optional[Dict[str, float]] = None,
    use_ml: bool = False,
) -> List[dict]:
    """
    Select the best team based on scores and position constraints.

    Uses a greedy approach: score all players, sort descending, then fill
    each position slot with the highest-scoring available player.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    players = (
        db.query(Player)
        .options(joinedload(Player.performances))
        .filter(Player.sport == sport)
        .all()
    )

    scored_players = []
    for player in players:
        if not player.performances:
            continue

        best_perf = max(player.performances, key=lambda p: p.matches_played)

        if sport == "Cricket":
            score, breakdown = score_cricket_player(best_perf)
            scoring_method = "cricket_formula"
        else:
            score, breakdown = score_generic_player(player, best_perf, weights)
            scoring_method = "generic_formula"

        scored_players.append({
            "player": player,
            "performance": best_perf,
            "score": score,
            "breakdown": breakdown,
            "scoring_method": scoring_method,
        })

    scored_players.sort(key=lambda x: x["score"], reverse=True)

    selected = []
    position_slots = dict(position_limits)

    for entry in scored_players:
        if len(selected) >= team_size:
            break
        player_position = entry["player"].position
        if position_slots.get(player_position, 0) > 0:
            selected.append(entry)
            position_slots[player_position] -= 1

    return selected


# ─── Substitution ─────────────────────────────────────────────────────────────

def suggest_substitution(
    db: Session,
    sport: str,
    current_team_ids: List[int],
    player_to_replace_id: int,
    allow_versatile: bool = True,
) -> dict:
    """
    Find the best substitute for a player in the current team.

    Steps:
      1. Load the player being replaced and their score.
      2. Find all players of the same sport NOT in the current team.
      3. Filter by same position (+ All-rounder if allow_versatile=True for Cricket).
      4. Score each candidate and pick the best.
      5. Return full breakdown showing WHY the substitute is better.
    """
    # Load the player to be replaced
    replaced = db.query(Player).options(joinedload(Player.performances)).filter(
        Player.id == player_to_replace_id
    ).first()
    if not replaced:
        raise ValueError(f"Player {player_to_replace_id} not found")

    replaced_perf = max(replaced.performances, key=lambda p: p.matches_played) if replaced.performances else None
    if replaced_perf is None:
        raise ValueError(f"Player {replaced.name} has no performance data")

    if sport == "Cricket":
        replaced_score, replaced_breakdown = score_cricket_player(replaced_perf)
    else:
        replaced_score, replaced_breakdown = score_generic_player(replaced, replaced_perf, DEFAULT_WEIGHTS)

    # Find eligible candidates
    candidates_query = (
        db.query(Player)
        .options(joinedload(Player.performances))
        .filter(Player.sport == sport)
        .filter(~Player.id.in_(current_team_ids))
    )
    candidates = candidates_query.all()

    # Filter by position
    target_position = replaced.position
    valid_positions = {target_position}
    if allow_versatile and sport == "Cricket":
        valid_positions.add("All-rounder")  # Versatile players can fill any role

    eligible = [p for p in candidates if p.position in valid_positions and p.performances]

    if not eligible:
        raise ValueError(
            f"No eligible substitute found for position '{target_position}' outside the current team"
        )

    # Score all candidates
    scored_candidates = []
    for player in eligible:
        best_perf = max(player.performances, key=lambda p: p.matches_played)
        if sport == "Cricket":
            score, breakdown = score_cricket_player(best_perf)
        else:
            score, breakdown = score_generic_player(player, best_perf, DEFAULT_WEIGHTS)

        scored_candidates.append({
            "player": player,
            "score": score,
            "breakdown": breakdown,
        })

    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    best = scored_candidates[0]

    improvement = round(best["score"] - replaced_score, 4)

    # Build substitution reason
    sub_bd = best["breakdown"]
    rep_bd = replaced_breakdown

    reasons = []
    if sub_bd["fitness_category"] > rep_bd["fitness_category"]:
        diff = sub_bd["fitness_category"] - rep_bd["fitness_category"]
        reasons.append(f"better fitness (+{diff:.1f})")
    if sub_bd["fatigue_category"] > rep_bd["fatigue_category"]:
        diff = sub_bd["fatigue_category"] - rep_bd["fatigue_category"]
        reasons.append(f"fresher (less fatigue, +{diff:.1f})")
    if sub_bd["injury_category"] > rep_bd["injury_category"]:
        diff = sub_bd["injury_category"] - rep_bd["injury_category"]
        reasons.append(f"lower injury risk (+{diff:.1f})")
    if sub_bd["performance_category"] > rep_bd["performance_category"]:
        diff = sub_bd["performance_category"] - rep_bd["performance_category"]
        reasons.append(f"better recent form (+{diff:.1f})")

    if not reasons:
        reason = (
            f"{best['player'].name} is the best available {target_position} "
            f"with overall score {best['score']:.2f} vs {replaced_score:.2f}"
        )
    else:
        reason = (
            f"{best['player'].name} replaces {replaced.name} due to: "
            + ", ".join(reasons)
            + f". Overall improvement: {improvement:+.2f}"
        )

    return {
        "replaced_player_id": replaced.id,
        "replaced_player_name": replaced.name,
        "replaced_player_score": replaced_score,
        "replaced_player_breakdown": replaced_breakdown,
        "substitute": {
            "player_id": best["player"].id,
            "name": best["player"].name,
            "position": best["player"].position,
            "team": best["player"].team,
            "score": best["score"],
            "score_breakdown": sub_bd,
            "improvement_over_replaced": improvement,
        },
        "reason": reason,
    }
