# Forward test: how it runs and what it records

The frozen v1 model is a **market-error signal**: it says which side of a posted total is likely
wrong and by roughly how much. It is not a projected total and is never reported as one.

## What happens without anyone starting it

| Step | Where it runs | When (UTC) | What it does |
|---|---|---|---|
| Signals | Claude cloud scheduled task | 10:23 and 21:23 daily | Pulls Torvik, scores every D1 game from 2 days back to 4 days ahead with `frozen/v1`, appends to `predictions.csv`, rebuilds `reports/forward_test.md`, commits |
| Odds | GitHub Actions (`.github/workflows/forward-log.yml`) | Every hour at :17 | Reads sportsbook totals for upcoming games, appends new or changed numbers to `lines.csv`, a heartbeat to `polls.csv`, best-line rows to `opportunities.csv`, commits |

Why two places: barttorvik.com refuses requests from GitHub's servers (HTTP 403), so the Torvik step
cannot run there. The Claude cloud environment can reach Torvik. ESPN is reachable from both.

## What each log holds

| File | One row per | Key fields |
|---|---|---|
| `predictions.csv` | game × run date | `run_ts_utc`, `kind` (prospective = logged before tip-off), `signal`, `direction`, ratings snapshot date, games in the inputs |
| `lines.csv` | book × game, each time the number or price is first seen or changes | `obs_ts_utc`, `source`, `provider`, `total`, `over_odds`, `under_odds`; post-game rows add the provider's own open and close |
| `polls.csv` | odds poll × source | proves the screen was checked then, so an unchanged line is known to be unchanged as of the last poll |
| `opportunities.csv` | flagged game, when a number is first available and whenever the best one changes | `signal`, `direction`, `best_book`, `best_total`, `best_price`, `books_seen`, `median_total` |

Timestamps are when *we* observed the number, not when the book posted it. With hourly polling a
"first seen" time is within about an hour of the true opener.

## Sportsbook sources

| Source | Status | Books | Cost |
|---|---|---|---|
| ESPN event odds | **On** | DraftKings only; lines appear on game day, not the night before | Free, unofficial |
| The Odds API | **Built, off until a key is added** | DraftKings, FanDuel, BetMGM, BetRivers, Bovada, BetOnline, LowVig (`us`); Pinnacle (`eu`) | Free tier: 500 credits/month = about 16 polls/day for one region |

To turn on The Odds API: create a free key at the-odds-api.com, then in the GitHub repository go to
Settings → Secrets and variables → Actions and add a secret named `ODDS_API_KEY`. Optionally add a
variable `ODDS_API_REGIONS` (`us`, or `us,eu` to include Pinnacle at twice the credit cost). With the
hourly schedule one region uses about 720 credits a month, so either reduce to `us` at 16 polls a day
or accept that the free quota runs out around day 21. **This path has not been tested with a real key.**

## Limits to know about

- GitHub's scheduler can start runs late and occasionally skips one under load. `polls.csv` shows exactly when each poll happened.
- GitHub disables scheduled workflows after 60 days without repository activity; the log commits themselves count as activity.
- If the repository is private, GitHub's free plan includes 2,000 Actions minutes a month; this job uses roughly 750.
- The signal job uses Claude usage twice a day. It can be paused or deleted from the scheduled-tasks list in the Claude app.
- A game whose opener posts and moves between two hourly polls is recorded at the later number.
- No source here gives limits, and none covers Circa or BookMaker.

## Manual run

```bash
pip install -r requirements.txt
python src/forward_log.py all && python src/forward_eval.py
```
