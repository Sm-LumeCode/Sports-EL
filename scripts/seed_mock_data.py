"""Seed the database with mock player and performance data.

Usage:
    python -m scripts.seed_mock_data            # Add data (idempotent)
    python -m scripts.seed_mock_data --reseed   # Wipe and re-insert all data
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.performance import Performance
from app.models.player import Player
from app.models.user import User
from app.core.security import get_password_hash


MOCK_PLAYERS = [
    # ─── Football (11+ players covering all positions) ───
    {
        "name": "Lionel Messi",
        "age": 36,
        "sport": "Football",
        "position": "FWD",
        "team": "Inter Miami",
        "performance": {
            "matches_played": 28, "minutes_played": 2410,
            "goals": 20, "assists": 16,
            "accuracy": 89.4, "efficiency": 92.1, "win_contribution": 84.7,
        },
    },
    {
        "name": "Aitana Bonmati",
        "age": 26,
        "sport": "Football",
        "position": "MID",
        "team": "Barcelona",
        "performance": {
            "matches_played": 31, "minutes_played": 2650,
            "goals": 12, "assists": 18,
            "accuracy": 91.8, "efficiency": 93.6, "win_contribution": 88.2,
        },
    },
    {
        "name": "Erling Haaland",
        "age": 24,
        "sport": "Football",
        "position": "FWD",
        "team": "Manchester City",
        "performance": {
            "matches_played": 35, "minutes_played": 2980,
            "goals": 36, "assists": 8,
            "accuracy": 85.2, "efficiency": 91.4, "win_contribution": 86.5,
        },
    },
    {
        "name": "Virgil van Dijk",
        "age": 33,
        "sport": "Football",
        "position": "DEF",
        "team": "Liverpool",
        "performance": {
            "matches_played": 34, "minutes_played": 3060,
            "goals": 3, "assists": 2,
            "accuracy": 92.1, "efficiency": 89.8, "win_contribution": 82.3,
        },
    },
    {
        "name": "Thibaut Courtois",
        "age": 32,
        "sport": "Football",
        "position": "GK",
        "team": "Real Madrid",
        "performance": {
            "matches_played": 30, "minutes_played": 2700,
            "goals": 0, "assists": 0,
            "accuracy": 88.5, "efficiency": 90.2, "win_contribution": 80.1,
        },
    },
    {
        "name": "Jude Bellingham",
        "age": 21,
        "sport": "Football",
        "position": "MID",
        "team": "Real Madrid",
        "performance": {
            "matches_played": 33, "minutes_played": 2800,
            "goals": 19, "assists": 11,
            "accuracy": 87.9, "efficiency": 90.7, "win_contribution": 85.6,
        },
    },
    {
        "name": "Antonio Rudiger",
        "age": 31,
        "sport": "Football",
        "position": "DEF",
        "team": "Real Madrid",
        "performance": {
            "matches_played": 32, "minutes_played": 2880,
            "goals": 2, "assists": 1,
            "accuracy": 90.3, "efficiency": 87.5, "win_contribution": 79.8,
        },
    },
    {
        "name": "Pedri",
        "age": 21,
        "sport": "Football",
        "position": "MID",
        "team": "Barcelona",
        "performance": {
            "matches_played": 29, "minutes_played": 2450,
            "goals": 6, "assists": 9,
            "accuracy": 93.2, "efficiency": 91.1, "win_contribution": 83.4,
        },
    },
    {
        "name": "Vinicius Jr",
        "age": 24,
        "sport": "Football",
        "position": "FWD",
        "team": "Real Madrid",
        "performance": {
            "matches_played": 34, "minutes_played": 2900,
            "goals": 22, "assists": 14,
            "accuracy": 84.6, "efficiency": 89.3, "win_contribution": 85.1,
        },
    },
    {
        "name": "Marquinhos",
        "age": 30,
        "sport": "Football",
        "position": "DEF",
        "team": "PSG",
        "performance": {
            "matches_played": 30, "minutes_played": 2700,
            "goals": 4, "assists": 3,
            "accuracy": 91.0, "efficiency": 88.9, "win_contribution": 81.2,
        },
    },
    {
        "name": "Alisson Becker",
        "age": 31,
        "sport": "Football",
        "position": "GK",
        "team": "Liverpool",
        "performance": {
            "matches_played": 28, "minutes_played": 2520,
            "goals": 0, "assists": 1,
            "accuracy": 87.3, "efficiency": 89.5, "win_contribution": 78.9,
        },
    },
    {
        "name": "Bukayo Saka",
        "age": 22,
        "sport": "Football",
        "position": "FWD",
        "team": "Arsenal",
        "performance": {
            "matches_played": 36, "minutes_played": 3100,
            "goals": 16, "assists": 13,
            "accuracy": 86.8, "efficiency": 88.7, "win_contribution": 83.9,
        },
    },
    {
        "name": "Joao Cancelo",
        "age": 30,
        "sport": "Football",
        "position": "DEF",
        "team": "Barcelona",
        "performance": {
            "matches_played": 27, "minutes_played": 2300,
            "goals": 3, "assists": 7,
            "accuracy": 88.1, "efficiency": 86.4, "win_contribution": 77.5,
        },
    },
    # ─── Cricket ───
    {
        "name": "Virat Kohli",
        "age": 35,
        "sport": "Cricket",
        "position": "Batter",
        "team": "India",
        "performance": {
            "matches_played": 24, "minutes_played": 1980,
            "goals": 0, "assists": 0,
            "accuracy": 87.0, "efficiency": 90.4, "win_contribution": 79.5,
        },
    },
    {
        "name": "Jasprit Bumrah",
        "age": 30,
        "sport": "Cricket",
        "position": "Bowler",
        "team": "India",
        "performance": {
            "matches_played": 22, "minutes_played": 1650,
            "goals": 0, "assists": 0,
            "accuracy": 93.5, "efficiency": 94.2, "win_contribution": 85.3,
        },
    },
    {
        "name": "Ravindra Jadeja",
        "age": 35,
        "sport": "Cricket",
        "position": "All-rounder",
        "team": "India",
        "performance": {
            "matches_played": 20, "minutes_played": 1500,
            "goals": 0, "assists": 0,
            "accuracy": 85.8, "efficiency": 88.1, "win_contribution": 81.7,
        },
    },
    {
        "name": "Rishabh Pant",
        "age": 27,
        "sport": "Cricket",
        "position": "Wicket-keeper",
        "team": "India",
        "performance": {
            "matches_played": 18, "minutes_played": 1400,
            "goals": 0, "assists": 0,
            "accuracy": 82.3, "efficiency": 86.9, "win_contribution": 76.4,
        },
    },
    # ─── Basketball ───
    {
        "name": "LeBron James",
        "age": 39,
        "sport": "Basketball",
        "position": "Forward",
        "team": "Los Angeles Lakers",
        "performance": {
            "matches_played": 65, "minutes_played": 2280,
            "goals": 0, "assists": 540,
            "accuracy": 54.0, "efficiency": 88.9, "win_contribution": 82.4,
        },
    },
    {
        "name": "Stephen Curry",
        "age": 36,
        "sport": "Basketball",
        "position": "Guard",
        "team": "Golden State Warriors",
        "performance": {
            "matches_played": 60, "minutes_played": 2100,
            "goals": 0, "assists": 380,
            "accuracy": 47.8, "efficiency": 91.3, "win_contribution": 84.1,
        },
    },
    {
        "name": "Nikola Jokic",
        "age": 29,
        "sport": "Basketball",
        "position": "Center",
        "team": "Denver Nuggets",
        "performance": {
            "matches_played": 70, "minutes_played": 2450,
            "goals": 0, "assists": 620,
            "accuracy": 58.3, "efficiency": 95.1, "win_contribution": 89.7,
        },
    },
    # ─── Hockey ───
    {
        "name": "Harmanpreet Singh",
        "age": 28,
        "sport": "Hockey",
        "position": "Defender",
        "team": "India",
        "performance": {
            "matches_played": 26, "minutes_played": 1720,
            "goals": 18, "assists": 9,
            "accuracy": 82.6, "efficiency": 88.2, "win_contribution": 84.8,
        },
    },
    {
        "name": "Zach Hyman",
        "age": 32,
        "sport": "Hockey",
        "position": "Forward",
        "team": "Edmonton Oilers",
        "performance": {
            "matches_played": 68, "minutes_played": 1540,
            "goals": 27, "assists": 17,
            "accuracy": 79.5, "efficiency": 86.7, "win_contribution": 80.3,
        },
    },
    {
        "name": "Connor McDavid",
        "age": 27,
        "sport": "Hockey",
        "position": "Forward",
        "team": "Edmonton Oilers",
        "performance": {
            "matches_played": 72, "minutes_played": 1620,
            "goals": 44, "assists": 56,
            "accuracy": 83.1, "efficiency": 94.8, "win_contribution": 91.2,
        },
    },
    {
        "name": "Manpreet Singh",
        "age": 32,
        "sport": "Hockey",
        "position": "Midfielder",
        "team": "India",
        "performance": {
            "matches_played": 30, "minutes_played": 1850,
            "goals": 5, "assists": 14,
            "accuracy": 80.2, "efficiency": 85.3, "win_contribution": 78.6,
        },
    },
    {
        "name": "PR Sreejesh",
        "age": 36,
        "sport": "Hockey",
        "position": "Goalkeeper",
        "team": "India",
        "performance": {
            "matches_played": 25, "minutes_played": 1500,
            "goals": 0, "assists": 0,
            "accuracy": 86.9, "efficiency": 87.5, "win_contribution": 82.1,
        },
    },
]

# Default admin user for testing auth
MOCK_USERS = [
    {
        "username": "admin",
        "email": "admin@sportsanalytics.com",
        "password": "admin123",
    },
]


def seed_mock_data(reseed: bool = False):
    """Seed the database with mock data.
    
    Args:
        reseed: If True, wipe all existing data before inserting.
    """
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    created_players = 0
    created_performances = 0
    created_users = 0

    try:
        if reseed:
            print("Reseed flag set — wiping existing data...")
            db.query(Performance).delete()
            db.query(Player).delete()
            db.query(User).delete()
            db.commit()
            print("All existing records deleted.")

        # Seed players and performances
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

        # Seed users
        for user_data in MOCK_USERS:
            existing_user = (
                db.query(User).filter(User.username == user_data["username"]).first()
            )
            if existing_user is None:
                db_user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                )
                db.add(db_user)
                created_users += 1

        db.commit()
    finally:
        db.close()

    print(
        f"Seed complete: {created_players} players, "
        f"{created_performances} performance records, "
        f"and {created_users} users added."
    )
    print(f"\nTotal players in seed data: {len(MOCK_PLAYERS)}")
    print(f"Sports covered: Football, Cricket, Basketball, Hockey")
    if created_users > 0:
        print(f"\nAdmin user created — username: admin, password: admin123")


def main():
    parser = argparse.ArgumentParser(description="Seed the Sports Analytics database")
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="Wipe all existing data and re-insert from scratch",
    )
    args = parser.parse_args()
    seed_mock_data(reseed=args.reseed)


if __name__ == "__main__":
    main()
