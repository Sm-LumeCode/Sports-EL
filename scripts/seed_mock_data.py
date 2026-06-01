from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.performance import Performance
from app.models.player import Player


MOCK_PLAYERS = [
    {
        "name": "Lionel Messi",
        "age": 36,
        "sport": "Football",
        "position": "Forward",
        "team": "Inter Miami",
        "performance": {
            "matches_played": 28,
            "minutes_played": 2410,
            "goals": 20,
            "assists": 16,
            "accuracy": 89.4,
            "efficiency": 92.1,
            "win_contribution": 84.7,
        },
    },
    {
        "name": "Aitana Bonmati",
        "age": 26,
        "sport": "Football",
        "position": "Midfielder",
        "team": "Barcelona",
        "performance": {
            "matches_played": 31,
            "minutes_played": 2650,
            "goals": 12,
            "assists": 18,
            "accuracy": 91.8,
            "efficiency": 93.6,
            "win_contribution": 88.2,
        },
    },
    {
        "name": "Virat Kohli",
        "age": 35,
        "sport": "Cricket",
        "position": "Batter",
        "team": "India",
        "performance": {
            "matches_played": 24,
            "minutes_played": 1980,
            "goals": 0,
            "assists": 0,
            "accuracy": 87.0,
            "efficiency": 90.4,
            "win_contribution": 79.5,
        },
    },
    {
        "name": "LeBron James",
        "age": 39,
        "sport": "Basketball",
        "position": "Forward",
        "team": "Los Angeles Lakers",
        "performance": {
            "matches_played": 65,
            "minutes_played": 2280,
            "goals": 0,
            "assists": 540,
            "accuracy": 54.0,
            "efficiency": 88.9,
            "win_contribution": 82.4,
        },
    },
    {
        "name": "Harmanpreet Singh",
        "age": 28,
        "sport": "Hockey",
        "position": "Defender",
        "team": "India",
        "performance": {
            "matches_played": 26,
            "minutes_played": 1720,
            "goals": 18,
            "assists": 9,
            "accuracy": 82.6,
            "efficiency": 88.2,
            "win_contribution": 84.8,
        },
    },
    {
        "name": "Zach Hyman",
        "age": 32,
        "sport": "Hockey",
        "position": "Forward",
        "team": "Edmonton Oilers",
        "performance": {
            "matches_played": 68,
            "minutes_played": 1540,
            "goals": 27,
            "assists": 17,
            "accuracy": 79.5,
            "efficiency": 86.7,
            "win_contribution": 80.3,
        },
    },
]


def seed_mock_data():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    created_players = 0
    created_performances = 0

    try:
        for item in MOCK_PLAYERS:
            performance_data = item["performance"]
            player_data = {
                "name": item["name"],
                "age": item["age"],
                "sport": item["sport"],
                "position": item["position"],
                "team": item["team"],
            }
            player = (
                db.query(Player)
                .filter(Player.name == player_data["name"], Player.team == player_data["team"])
                .first()
            )

            if player is None:
                player = Player(**player_data)
                db.add(player)
                db.flush()
                created_players += 1

            existing_performance = (
                db.query(Performance).filter(Performance.player_id == player.id).first()
            )
            if existing_performance is None:
                db.add(Performance(player_id=player.id, **performance_data))
                created_performances += 1

        db.commit()
    finally:
        db.close()

    print(
        f"Seed complete: {created_players} players and "
        f"{created_performances} performance records added."
    )


if __name__ == "__main__":
    seed_mock_data()
