"""Hypothesis 1: find two-for-one opportunities and score each sequence.

One row per game-period (Q1 to Q3) that has a possession starting inside the window.
Naming: team A has the ball at the start of the window (possession A1), team B gets the
next possession (B), and A2 is A's possession after that, if it happens.
"""

import pandas as pd

from stxntx.config import (
    BASELINE_MIN_START_SECONDS,
    H1_PERIODS,
    TFO_ATTEMPT_THRESHOLD,
    TFO_WINDOW_SECONDS,
)


def _disruption(a1, b, a2, achieved):
    if achieved:
        return None
    if a1["has_oreb"]:
        return "a1_offensive_rebound"
    if b is None:
        return "no_b_possession"
    if a2 is None or a2["start_seconds"] <= 0:
        return "b_ran_out_clock"
    return "other"


def flag_period_ends(poss: pd.DataFrame) -> pd.DataFrame:
    lo, hi = TFO_WINDOW_SECONDS
    rows = []
    q = poss[poss["period"].isin(H1_PERIODS)].sort_values(["game_id", "period", "number"])
    for (game_id, period), g in q.groupby(["game_id", "period"], sort=False):
        g = g.reset_index(drop=True)
        in_window = g[(g["start_seconds"] >= lo) & (g["start_seconds"] <= hi)]
        if in_window.empty:
            continue
        # If several possessions start inside the window, the last one is the
        # team actually facing the two-for-one decision.
        i = in_window.index[-1]
        a1 = g.loc[i]
        team_a = a1["offense_team_id"]
        b = g.loc[i + 1] if i + 1 < len(g) else None
        a2 = g.loc[i + 2] if i + 2 < len(g) else None

        action = a1["first_action_seconds"]
        attempted = pd.notna(action) and action > TFO_ATTEMPT_THRESHOLD
        achieved = (
            b is not None and b["offense_team_id"] != team_a
            and a2 is not None and a2["offense_team_id"] == team_a
            and a2["start_seconds"] > 0
        )
        rest = g.loc[i:]
        a_points = rest.loc[rest["offense_team_id"] == team_a, "points"].sum()
        b_points_all = rest.loc[rest["offense_team_id"] != team_a, "points"].sum()

        rows.append({
            "game_id": game_id,
            "season_type": a1["season_type"],
            "period": period,
            "team_a": team_a,
            "team_b": a1["defense_team_id"],
            "a1_start_seconds": a1["start_seconds"],
            "a1_first_action_seconds": action,
            "a1_start_type": a1["start_type"],
            "a1_points": a1["points"],
            "b_start_seconds": None if b is None else b["start_seconds"],
            "b_points": 0 if b is None else b["points"],
            "a2_start_seconds": a2["start_seconds"] if achieved else None,
            "a2_points": a2["points"] if achieved else 0,
            "tfo_opportunity": True,
            "tfo_attempted": bool(attempted),
            "tfo_achieved": bool(achieved),
            "tfo_disruption": _disruption(a1, b, a2, achieved) if attempted else None,
            # A1 + A2 - B: the three-possession net from the plan
            "net_3": a1["points"] + (a2["points"] if achieved else 0) - (0 if b is None else b["points"]),
            # Every possession from A1 to the buzzer: comparable for attempted and control groups
            "net_to_buzzer": a_points - b_points_all,
            "possessions_to_buzzer": len(rest),
        })
    return pd.DataFrame(rows)


def baseline_possessions(poss: pd.DataFrame) -> pd.DataFrame:
    """Possessions not constrained by the game clock: Q1 to Q3, starting with more than 24 seconds left."""
    return poss[poss["period"].isin(H1_PERIODS) & (poss["start_seconds"] > BASELINE_MIN_START_SECONDS)]