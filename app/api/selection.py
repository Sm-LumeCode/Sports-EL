from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps import get_current_active_user
from app.models.user import User
from app.schemas.selection import (
    SelectionRequest, SelectionResponse, SelectedPlayer, ScoreBreakdown,
    SubstitutionRequest, SubstitutionResponse, SubstitutionCandidate,
)
from app.services.selection_service import select_team, suggest_substitution, DEFAULT_WEIGHTS

router = APIRouter()


@router.post("/", response_model=SelectionResponse)
def create_selection(
    request: SelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Select the best team based on scoring and position constraints.

    - For **Cricket**, uses the 5-category weighted formula.
    - For all other sports, uses the generic stats-based formula.

    Requires authentication.
    """
    total_positions = sum(request.position_limits.values())
    if total_positions != request.team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sum of position_limits ({total_positions}) must equal team_size ({request.team_size})",
        )

    weights = request.weights or DEFAULT_WEIGHTS

    selected = select_team(
        db=db,
        sport=request.sport,
        team_size=request.team_size,
        position_limits=request.position_limits,
        weights=weights,
        use_ml=request.use_ml,
    )

    team = [
        SelectedPlayer(
            player_id=entry["player"].id,
            name=entry["player"].name,
            position=entry["player"].position,
            team=entry["player"].team,
            score=entry["score"],
            goals=entry["performance"].goals,
            assists=entry["performance"].assists,
            efficiency=entry["performance"].efficiency,
            score_breakdown=ScoreBreakdown(**entry["breakdown"]),
        )
        for entry in selected
    ]

    scoring_method = selected[0]["scoring_method"] if selected else "deterministic"

    return SelectionResponse(
        sport=request.sport,
        team_size=request.team_size,
        players_selected=len(team),
        scoring_method=scoring_method,
        weights_used=weights,
        team=team,
    )


@router.post("/substitute", response_model=SubstitutionResponse)
def substitute_player(
    request: SubstitutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Find the best substitute for a player in the current team.

    Returns the recommended substitute along with a full score breakdown
    showing **why** this player was chosen over the one being replaced.

    Requires authentication.
    """
    if request.player_to_replace_id not in request.current_team_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="player_to_replace_id must be in current_team_ids",
        )

    try:
        result = suggest_substitution(
            db=db,
            sport=request.sport,
            current_team_ids=request.current_team_ids,
            player_to_replace_id=request.player_to_replace_id,
            allow_versatile=request.allow_versatile,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return SubstitutionResponse(
        replaced_player_id=result["replaced_player_id"],
        replaced_player_name=result["replaced_player_name"],
        replaced_player_score=result["replaced_player_score"],
        replaced_player_breakdown=ScoreBreakdown(**result["replaced_player_breakdown"]),
        substitute=SubstitutionCandidate(**result["substitute"]),
        reason=result["reason"],
    )
