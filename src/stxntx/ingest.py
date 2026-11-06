"""Build the possession table for whole seasons and save it as Parquet.

Run from the project folder, with the venv active:

    python -m stxntx.ingest 2016            # one season (2016-17)
    python -m stxntx.ingest 2009 2025       # a range of seasons, 2009-10 through 2025-26
    python -m stxntx.ingest 2016 --overwrite

Output, per season:
    data/clean/possessions_2016.parquet     one row per possession, regular season + playoffs
    data/clean/failures_2016.csv            games that could not be parsed, with the error
"""

import argparse
import time
import traceback

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog
from pbpstats.client import Client

from stxntx.config import CLEAN_DIR, RAW_DIR, REQUEST_PAUSE_SECONDS
from stxntx.possessions import possession_table
from stxntx.sources import LIVE_FIRST_SEASON, make_client, prepare_season

GAME_TYPE_CODES = {"Regular Season": "002", "Playoffs": "004"}


def season_label(start_year: int) -> str:
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def game_ids(start_year: int) -> list[str]:
    """Every regular-season and playoff game ID for a season."""
    yy = str(start_year)[-2:]
    if start_year < LIVE_FIRST_SEASON:
        # Older seasons: the converted files on disk are the list.
        prepare_season(start_year)
        prepare_season(start_year, playoffs=True)
        ids = []
        for code in GAME_TYPE_CODES.values():
            ids += [p.stem[6:] for p in (RAW_DIR / "pbp").glob(f"stats_{code}{yy}*.json")]
        return sorted(ids)
    # Live-feed seasons: ask NBA.com for the season's game log, then cache it.
    cache = RAW_DIR / "schedule" / f"game_ids_{start_year}.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype=str)["game_id"].tolist()
    ids = []
    for season_type in GAME_TYPE_CODES:
        log = leaguegamelog.LeagueGameLog(
            season=season_label(start_year),
            season_type_all_star=season_type,
            player_or_team_abbreviation="T",
            timeout=60,
        ).get_data_frames()[0]
        ids += log["GAME_ID"].unique().tolist()
        time.sleep(REQUEST_PAUSE_SECONDS)
    ids = sorted(set(ids))
    cache.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"game_id": ids}).to_csv(cache, index=False)
    return ids


def _client_for(start_year: int, cached: bool) -> Client:
    """Live-feed games already on disk are read from file, so reruns don't download again."""
    if cached:
        return Client({"dir": str(RAW_DIR), "Possessions": {"source": "file", "data_provider": "live"}})
    return make_client(start_year)


def build_season(start_year: int, overwrite: bool = False) -> pd.DataFrame | None:
    out = CLEAN_DIR / f"possessions_{start_year}.parquet"
    if out.exists() and not overwrite:
        print(f"{season_label(start_year)}: already built, skipping (use --overwrite to rebuild)")
        return None

    ids = game_ids(start_year)
    live = start_year >= LIVE_FIRST_SEASON
    # pbpstats stores a client's settings on a class shared by every client, so creating a
    # second client silently changes the first. Keep one client, and rebuild it only when
    # switching between reading from file and downloading.
    client, client_mode = None, None

    tables, failures = [], []
    started = time.time()
    for n, gid in enumerate(ids, start=1):
        cached = live and (RAW_DIR / "pbp" / f"live_{gid}.json").exists()
        if cached != client_mode:
            client, client_mode = _client_for(start_year, cached), cached
        try:
            tables.append(possession_table(client.Game(gid), gid))
        except Exception as e:
            failures.append({"game_id": gid, "error": type(e).__name__, "message": str(e)[:300]})
            if len(failures) <= 3:  # show the first few errors in full while the run continues
                print(f"  FAILED {gid} ({'cached file' if cached else 'web'}):")
                traceback.print_exc(limit=6)
        if live and not cached:
            time.sleep(REQUEST_PAUSE_SECONDS / 4)
        if n % 100 == 0:
            print(f"  {season_label(start_year)}: {n}/{len(ids)} games, {len(failures)} failed, {time.time() - started:.0f}s")

    if not tables:
        print(f"{season_label(start_year)}: no games parsed, nothing saved")
        return None
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    poss = pd.concat(tables, ignore_index=True)
    poss.insert(0, "season", season_label(start_year))
    poss.to_parquet(out, index=False)
    pd.DataFrame(failures, columns=["game_id", "error", "message"]).to_csv(
        CLEAN_DIR / f"failures_{start_year}.csv", index=False
    )
    print(f"{season_label(start_year)}: {len(tables)} games, {len(poss)} possessions, "
          f"{len(failures)} failed, {time.time() - started:.0f}s -> {out.name}")
    return poss


def main():
    parser = argparse.ArgumentParser(description="Build possession tables by season.")
    parser.add_argument("first", type=int, help="starting year of the first season, e.g. 2016 for 2016-17")
    parser.add_argument("last", type=int, nargs="?", help="starting year of the last season (default: same as first)")
    parser.add_argument("--overwrite", action="store_true", help="rebuild seasons that already have a Parquet file")
    args = parser.parse_args()
    for year in range(args.first, (args.last or args.first) + 1):
        build_season(year, overwrite=args.overwrite)


if __name__ == "__main__":
    main()