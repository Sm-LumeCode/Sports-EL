"""
Large Dynamic Mock Dataset Seeder
==================================
Generates 200+ players with realistic randomised metrics for:
  - Cricket   : 6 teams × ~18 players  (Batters, Bowlers, All-rounders, WK)
  - Football  : 6 teams × ~18 players  (GK, DEF, MID, FWD)
  - Basketball: 4 teams × ~15 players  (Guard, Forward, Center)
  - Hockey    : 4 teams × ~14 players  (Goalkeeper, Defender, Midfielder, Forward)

Each player gets randomised performance metrics so scores change every
time --reseed is used, simulating live data fluctuation.

Usage:
    python -m scripts.seed_large_dataset            # add only (idempotent)
    python -m scripts.seed_large_dataset --reseed   # wipe and regenerate
"""

import argparse
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.performance import Performance
from app.models.player import Player
from app.models.user import User
from app.core.security import get_password_hash

random.seed()  # Use true randomness every run

# ─── Helper ───────────────────────────────────────────────────────────────────

def rf(lo: float, hi: float, decimals: int = 1) -> float:
    """Random float in [lo, hi] rounded to `decimals` places."""
    return round(random.uniform(lo, hi), decimals)


def ri(lo: int, hi: int) -> int:
    return random.randint(lo, hi)


# ─── Name pools (mock names) ───────────────────────────────────────────────────

FIRST_NAMES = [
    "Arjun", "Kiran", "Dev", "Rohan", "Sai", "Priya", "Anil", "Rahul", "Vikram", "Ravi",
    "Akash", "Nikhil", "Suresh", "Rajesh", "Amit", "Sanjay", "Deepak", "Manish", "Ankur", "Gaurav",
    "James", "Lucas", "Oliver", "Noah", "Liam", "Ethan", "Mason", "Logan", "Jacob", "Aiden",
    "Mohammed", "Yusuf", "Hassan", "Tariq", "Khalid", "Omar", "Bilal", "Faisal", "Zaid", "Imran",
    "Carlos", "Diego", "Miguel", "Andres", "Roberto", "Felipe", "Paulo", "Gabriel", "Rafael", "Mateus",
    "Wei", "Jian", "Ming", "Tao", "Lei", "Feng", "Hao", "Jun", "Xin", "Chao",
    "Kofi", "Kwame", "Yaw", "Ama", "Abena", "Fiifi", "Nana", "Kojo", "Esi", "Adwoa",
    "Ivan", "Dmitri", "Alexei", "Nikolai", "Sergei", "Boris", "Pavel", "Andrei", "Yuri", "Mikhail",
]

LAST_NAMES = [
    "Kumar", "Singh", "Sharma", "Patel", "Verma", "Nair", "Iyer", "Reddy", "Rao", "Bose",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Khan", "Ahmed", "Ali", "Sheikh", "Malik", "Chaudhry", "Qureshi", "Siddiqui", "Ansari", "Mirza",
    "Silva", "Santos", "Oliveira", "Costa", "Pereira", "Ferreira", "Carvalho", "Rodrigues", "Almeida", "Nunes",
    "Zhang", "Wang", "Li", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou",
    "Mensah", "Asante", "Boateng", "Owusu", "Acheampong", "Amoah", "Appiah", "Osei", "Bonsu", "Frimpong",
    "Petrov", "Ivanov", "Sidorov", "Volkov", "Morozov", "Sokolov", "Popov", "Lebedev", "Kozlov", "Novikov",
]

_used_names: set = set()


def rand_name() -> str:
    for _ in range(100):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in _used_names:
            _used_names.add(name)
            return name
    return f"Player_{random.randint(1000, 9999)}"


# ─── Fitness / Fatigue / Injury helpers ───────────────────────────────────────

def fitness_metrics(profile: str) -> dict:
    """Generate fitness metrics.  profile: 'peak' | 'average' | 'tired'"""
    if profile == "peak":
        return dict(fitness_score=rf(80, 98), stamina=rf(78, 97), speed=rf(75, 95), training_attendance=rf(85, 100))
    elif profile == "tired":
        return dict(fitness_score=rf(40, 65), stamina=rf(35, 60), speed=rf(40, 65), training_attendance=rf(50, 75))
    else:
        return dict(fitness_score=rf(60, 85), stamina=rf(55, 80), speed=rf(58, 82), training_attendance=rf(65, 90))


def fatigue_metrics(profile: str) -> dict:
    """Higher = better (fresher player)."""
    if profile == "peak":
        return dict(fatigue_index=rf(75, 95), recovery_score=rf(78, 97), workload_score=rf(70, 92))
    elif profile == "tired":
        return dict(fatigue_index=rf(25, 50), recovery_score=rf(20, 48), workload_score=rf(30, 55))
    else:
        return dict(fatigue_index=rf(50, 80), recovery_score=rf(48, 78), workload_score=rf(50, 75))


def injury_metrics(profile: str) -> dict:
    """Higher = healthier."""
    if profile == "peak":
        return dict(current_injury_status=rf(85, 100), injury_history=rf(80, 100), days_since_last_injury=rf(80, 100))
    elif profile == "tired":
        return dict(current_injury_status=rf(30, 60), injury_history=rf(25, 55), days_since_last_injury=rf(20, 50))
    else:
        return dict(current_injury_status=rf(60, 88), injury_history=rf(55, 85), days_since_last_injury=rf(55, 85))


def perf_metrics(profile: str) -> dict:
    if profile == "peak":
        return dict(last_3_score=rf(78, 98), last_5_score=rf(75, 96), consistency=rf(80, 97))
    elif profile == "tired":
        return dict(last_3_score=rf(30, 58), last_5_score=rf(35, 62), consistency=rf(28, 55))
    else:
        return dict(last_3_score=rf(55, 82), last_5_score=rf(52, 80), consistency=rf(50, 80))


def team_req_metrics() -> dict:
    return dict(role_match=rf(55, 98), team_balance_need=rf(50, 95), versatility=rf(40, 92))


def profile_for(idx: int, total: int) -> str:
    """Distribute profiles: top third = peak, bottom fifth = tired, rest = average."""
    if idx < total // 3:
        return "peak"
    elif idx >= total - total // 5:
        return "tired"
    return "average"


def make_perf(position: str, sport: str, profile: str, team_idx: int) -> dict:
    """Build a full performance record for a player."""
    base: dict = {}

    if sport == "Cricket":
        matches = ri(8, 30)
        minutes = matches * ri(40, 90)
        if position == "Batter":
            goals, assists = 0, 0
            accuracy = rf(55, 92)
            efficiency = rf(60, 95)
        elif position == "Bowler":
            goals, assists = 0, 0
            accuracy = rf(65, 96)
            efficiency = rf(62, 94)
        elif position == "All-rounder":
            goals, assists = 0, 0
            accuracy = rf(58, 90)
            efficiency = rf(60, 92)
        else:  # Wicket-keeper
            goals, assists = 0, 0
            accuracy = rf(70, 95)
            efficiency = rf(65, 93)
        base = dict(matches_played=matches, minutes_played=minutes,
                    goals=goals, assists=assists,
                    accuracy=accuracy, efficiency=efficiency,
                    win_contribution=rf(50, 92))

    elif sport == "Football":
        matches = ri(15, 38)
        minutes = matches * ri(45, 95)
        if position == "FWD":
            goals, assists = ri(5, 35), ri(2, 18)
        elif position == "MID":
            goals, assists = ri(2, 18), ri(5, 22)
        elif position == "DEF":
            goals, assists = ri(0, 5), ri(0, 8)
        else:  # GK
            goals, assists = 0, ri(0, 2)
        base = dict(matches_played=matches, minutes_played=minutes,
                    goals=goals, assists=assists,
                    accuracy=rf(72, 96), efficiency=rf(65, 95),
                    win_contribution=rf(55, 92))

    elif sport == "Basketball":
        matches = ri(40, 82)
        minutes = matches * ri(20, 38)
        if position in ("Guard", "Forward"):
            assists = ri(100, 700)
        else:
            assists = ri(50, 350)
        base = dict(matches_played=matches, minutes_played=minutes,
                    goals=0, assists=assists,
                    accuracy=rf(38, 62), efficiency=rf(70, 97),
                    win_contribution=rf(60, 93))

    else:  # Hockey
        matches = ri(18, 72)
        minutes = matches * ri(15, 60)
        if position == "Forward":
            goals, assists = ri(5, 45), ri(5, 35)
        elif position == "Midfielder":
            goals, assists = ri(2, 20), ri(5, 28)
        elif position == "Defender":
            goals, assists = ri(0, 10), ri(2, 15)
        else:  # Goalkeeper
            goals, assists = 0, 0
        base = dict(matches_played=matches, minutes_played=minutes,
                    goals=goals, assists=assists,
                    accuracy=rf(68, 94), efficiency=rf(62, 93),
                    win_contribution=rf(52, 90))

    base.update(fitness_metrics(profile))
    base.update(fatigue_metrics(profile))
    base.update(injury_metrics(profile))
    base.update(perf_metrics(profile))
    base.update(team_req_metrics())
    return base


# ─── Team Definitions ─────────────────────────────────────────────────────────

CRICKET_TEAMS = [
    ("India", ["Batter"]*5 + ["Bowler"]*5 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
    ("Australia", ["Batter"]*5 + ["Bowler"]*5 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
    ("England", ["Batter"]*5 + ["Bowler"]*4 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
    ("South Africa", ["Batter"]*4 + ["Bowler"]*5 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
    ("New Zealand", ["Batter"]*5 + ["Bowler"]*4 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
    ("Pakistan", ["Batter"]*5 + ["Bowler"]*5 + ["All-rounder"]*2 + ["Wicket-keeper"]*2),
    ("West Indies", ["Batter"]*5 + ["Bowler"]*4 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
    ("Sri Lanka", ["Batter"]*4 + ["Bowler"]*5 + ["All-rounder"]*3 + ["Wicket-keeper"]*2),
]

FOOTBALL_TEAMS = [
    ("Real Madrid", ["GK"]*2 + ["DEF"]*5 + ["MID"]*5 + ["FWD"]*5),
    ("Manchester City", ["GK"]*2 + ["DEF"]*5 + ["MID"]*5 + ["FWD"]*5),
    ("Barcelona", ["GK"]*2 + ["DEF"]*5 + ["MID"]*5 + ["FWD"]*4),
    ("Liverpool", ["GK"]*2 + ["DEF"]*5 + ["MID"]*5 + ["FWD"]*4),
    ("Bayern Munich", ["GK"]*2 + ["DEF"]*4 + ["MID"]*5 + ["FWD"]*5),
    ("PSG", ["GK"]*2 + ["DEF"]*4 + ["MID"]*5 + ["FWD"]*5),
]

BASKETBALL_TEAMS = [
    ("Los Angeles Lakers", ["Guard"]*5 + ["Forward"]*5 + ["Center"]*3),
    ("Golden State Warriors", ["Guard"]*6 + ["Forward"]*4 + ["Center"]*3),
    ("Boston Celtics", ["Guard"]*5 + ["Forward"]*5 + ["Center"]*3),
    ("Denver Nuggets", ["Guard"]*5 + ["Forward"]*4 + ["Center"]*4),
    ("Milwaukee Bucks", ["Guard"]*5 + ["Forward"]*5 + ["Center"]*3),
]

HOCKEY_TEAMS = [
    ("India", ["Goalkeeper"]*2 + ["Defender"]*5 + ["Midfielder"]*5 + ["Forward"]*5),
    ("Netherlands", ["Goalkeeper"]*2 + ["Defender"]*5 + ["Midfielder"]*5 + ["Forward"]*4),
    ("Australia", ["Goalkeeper"]*2 + ["Defender"]*4 + ["Midfielder"]*5 + ["Forward"]*5),
    ("Belgium", ["Goalkeeper"]*2 + ["Defender"]*5 + ["Midfielder"]*4 + ["Forward"]*5),
    ("Germany", ["Goalkeeper"]*2 + ["Defender"]*5 + ["Midfielder"]*5 + ["Forward"]*4),
]


# ─── Build MOCK_PLAYERS ────────────────────────────────────────────────────────

def build_players() -> list:
    players = []
    sport_teams = [
        ("Cricket",    CRICKET_TEAMS),
        ("Football",   FOOTBALL_TEAMS),
        ("Basketball", BASKETBALL_TEAMS),
        ("Hockey",     HOCKEY_TEAMS),
    ]

    for sport, teams in sport_teams:
        for team_idx, (team_name, positions) in enumerate(teams):
            total = len(positions)
            random.shuffle(positions)  # randomise position order per team
            for i, position in enumerate(positions):
                profile = profile_for(i, total)
                age = ri(19, 38)
                perf = make_perf(position, sport, profile, team_idx)
                players.append({
                    "name": rand_name(),
                    "age": age,
                    "sport": sport,
                    "position": position,
                    "team": team_name,
                    "performance": perf,
                })

    return players


# ─── Seeder ────────────────────────────────────────────────────────────────────

def seed_large_dataset(reseed: bool = False):
    if reseed:
        print("Reseed flag set — dropping and recreating all tables (fresh schema)...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

    Base.metadata.create_all(bind=engine)
    print("Tables ready.")

    db = SessionLocal()

    try:
        if reseed:
            print("Inserting fresh data...")

        mock_players = build_players()
        created_players = 0
        created_performances = 0

        for item in mock_players:
            perf_data = item["performance"]
            player = (
                db.query(Player)
                .filter(Player.name == item["name"], Player.team == item["team"])
                .first()
            )
            if player is None:
                player = Player(
                    name=item["name"],
                    age=item["age"],
                    sport=item["sport"],
                    position=item["position"],
                    team=item["team"],
                )
                db.add(player)
                db.flush()
                created_players += 1

            existing_perf = db.query(Performance).filter(Performance.player_id == player.id).first()
            if existing_perf is None:
                db.add(Performance(player_id=player.id, **perf_data))
                created_performances += 1

        # Seed admin user
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                email="admin@sportsanalytics.com",
                hashed_password=get_password_hash("admin123"),
            ))

        db.commit()
    finally:
        db.close()

    sport_counts = {}
    for p in mock_players:
        sport_counts[p["sport"]] = sport_counts.get(p["sport"], 0) + 1

    print(f"\n[OK] Seed complete!")
    print(f"   Players created : {created_players}")
    print(f"   Performances    : {created_performances}")
    print(f"\nBreakdown by sport:")
    for sport, count in sport_counts.items():
        print(f"   {sport:<12} {count} players")
    print(f"\n   Total players   : {sum(sport_counts.values())}")
    print(f"\n   Admin login  ->  username: admin  |  password: admin123")


def main():
    parser = argparse.ArgumentParser(description="Seed large dynamic dataset")
    parser.add_argument("--reseed", action="store_true", help="Wipe and regenerate all data")
    args = parser.parse_args()
    seed_large_dataset(reseed=args.reseed)


if __name__ == "__main__":
    main()
