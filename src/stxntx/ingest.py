"""Pull games and possessions from stats.nba.com via nba_api and pbpstats.

Steps to build here (Roadmap phases 2 and 3):
1. List every game ID for each season in config.PULL_SEASONS and config.SEASON_TYPES.
2. For each game, load possessions with pbpstats, caching raw JSON in config.RAW_DIR.
3. Pause config.REQUEST_PAUSE_SECONDS between requests; log games that fail parsing.
4. Write one Parquet file per season to config.CLEAN_DIR.
"""
