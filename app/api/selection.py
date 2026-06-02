from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps import get_current_active_user
from app.models.user import User
from app.schemas.selection import SelectionRequest, SelectionResponse, SelectedPlayer
from app.services.selection_service import select_team, DEFAULT_WEIGHTS

router = APIRouter()


@router.post("/", response_model=SelectionResponse)
def create_selection(
    request: SelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Select the best team based on scoring and position constraints.
    
    Requires authentication.
    """
    # Validate that position limits sum matches team_size
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

    # Build response
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
        )
        for entry in selected
    ]

    # Determine scoring method from first entry, default to deterministic
    scoring_method = selected[0]["scoring_method"] if selected else "deterministic"

    return SelectionResponse(
        sport=request.sport,
        team_size=request.team_size,
        players_selected=len(team),
        scoring_method=scoring_method,
        weights_used=weights,
        team=team,
    )
