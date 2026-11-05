<<<<<<< HEAD
# stxntx

NBA analytics behind [Sticks and Ticks](https://sticksandticks.com/). Two questions:

1. **Two-for-one.** Does rushing the first possession of an end-of-quarter two-for-one actually win the three-possession sequence? Are the Kerr-era Warriors worse at it than other teams? (2014-15 to 2025-26, Q1 to Q3, regular season and playoffs.)
2. **Curry's teammates.** Do players perform worse without Steph Curry, on the Warriors and on other teams, after adjusting for age? How does that compare to teammates of other ball-dominant stars?

## Stack

| Step | Tool |
| --- | --- |
| Data | `nba_api`, `pbpstats` (NBA.com play-by-play and possessions) |
| Storage | Parquet files |
| Query | DuckDB (SQL over Parquet) |
| Charts | Plotly, exported as standalone HTML |
| Hosting | GitHub Pages from `site/`, embedded in WordPress with an iframe |

## Layout

```text
data/raw/          JSON response cache per game (git-ignored)
data/clean/        possessions, events, player_seasons as Parquet (git-ignored)
data/published/    small aggregates that feed charts (committed)
data/reference/    hand-built lookup tables (committed)
src/stxntx/        reusable Python: ingest, possessions, flags, teammates
sql/               one .sql file per published number
notebooks/         exploration
charts/            Plotly build scripts
site/charts/       generated chart HTML, served by GitHub Pages
tests/             checks on flags and reconciliation
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Run data pulls from your own computer. stats.nba.com throttles fast requests and often ignores cloud IP addresses.

## Data and terms

Data comes from NBA.com and is subject to the NBA.com Terms of Use. This repo publishes only aggregates and charts; raw play-by-play stays local.
=======
"# stxnx" 
>>>>>>> bf5ed6c002310e29acc80c7bdc1a442262ae0c1c
