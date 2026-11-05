"""Decisions frozen before looking at results. Change them here, nowhere else."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"
PUBLISHED_DIR = ROOT / "data" / "published"
REFERENCE_DIR = ROOT / "data" / "reference"
SITE_CHARTS_DIR = ROOT / "site" / "charts"

# Seasons
PULL_SEASONS = [f"{y}-{str(y + 1)[-2:]}" for y in range(2009, 2026)]  # 2009-10 .. 2025-26
H1_SEASONS = [s for s in PULL_SEASONS if int(s[:4]) >= 2014]          # Kerr era
SEASON_TYPES = ["Regular Season", "Playoffs"]

# Hypothesis 1: two-for-one
H1_PERIODS = (1, 2, 3)                # Q4 and overtime excluded
TFO_WINDOW_SECONDS = (36.0, 45.0)     # game clock at the change of possession
TFO_ATTEMPT_THRESHOLD = 24.0          # A1 shot, turnover or shooting foul with more than this left
BASELINE_MIN_START_SECONDS = 24.0     # baseline = possessions starting with more than this left
SHOOTING_FOUL_COUNTS_AS_ATTEMPT = True
INCLUDE_INTERIM_COACH_GAMES = True    # Walton 2015-16, Brown 2017 playoffs count as Kerr era

# Hypothesis 2: Curry teammates (minutes, games), pooled per player per scenario
THRESHOLDS = {
    "S1_with_curry": (500, 25),
    "S2_gsw_without_curry": (150, 20),
    "S3_elsewhere": (500, 25),
}
REQUEST_PAUSE_SECONDS = 1.0           # pause between stats.nba.com requests
