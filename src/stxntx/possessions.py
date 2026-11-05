"""Turn a pbpstats game into a flat table: one row per possession."""

import pandas as pd
from pbpstats.resources.enhanced_pbp import FieldGoal, Foul, FreeThrow, Rebound, Turnover


def clock_to_seconds(clock: str) -> float:
    """'0:38.4' -> 38.4"""
    minutes, seconds = clock.split(":")
    return int(minutes) * 60 + float(seconds)


def season_type(game_id: str) -> str:
    """The third digit of a game ID says the game type: 2 = regular season, 4 = playoffs."""
    return {"2": "Regular Season", "4": "Playoffs", "5": "Play-In"}.get(game_id[2], "Other")


def first_action_seconds(possession, offense_team_id):
    """Clock time of the offense's first shot, turnover, free throw, or drawn shooting foul.

    This is the moment the offense "used" its possession, which decides whether a
    two-for-one was attempted. Returns None if the possession had none of these.
    """
    for event in possession.events:
        if isinstance(event, FieldGoal) and event.team_id == offense_team_id:
            return event.seconds_remaining
        if isinstance(event, Turnover) and not event.is_no_turnover and event.team_id == offense_team_id:
            return event.seconds_remaining
        if isinstance(event, Foul) and event.is_shooting_foul and event.team_id != offense_team_id:
            return event.seconds_remaining
        if isinstance(event, FreeThrow) and event.team_id == offense_team_id:
            return event.seconds_remaining
    return None


def has_offensive_rebound(possession, offense_team_id) -> bool:
    return any(
        isinstance(e, Rebound) and e.is_real_rebound and e.oreb and e.team_id == offense_team_id
        for e in possession.events
    )


def possession_table(game, game_id: str) -> pd.DataFrame:
    rows = []
    for p in game.possessions.items:
        offense = p.offense_team_id
        start_score = p.previous_possession.events[-1].score if p.previous_possession else p.events[0].score
        end_score = p.events[-1].score
        teams = [t for t in end_score.keys() if t != offense]
        rows.append({
            "game_id": game_id,
            "season_type": season_type(game_id),
            "period": p.period,
            "number": p.number,
            "offense_team_id": offense,
            "defense_team_id": teams[0] if teams else None,
            "start_seconds": clock_to_seconds(p.start_time),
            "end_seconds": clock_to_seconds(p.end_time),
            "start_type": p.possession_start_type,
            "first_action_seconds": first_action_seconds(p, offense),
            "has_oreb": has_offensive_rebound(p, offense),
            "points": end_score.get(offense, 0) - start_score.get(offense, 0),
        })
    return pd.DataFrame(rows)