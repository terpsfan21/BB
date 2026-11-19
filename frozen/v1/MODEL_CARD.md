# Frozen model v1 — factors-only market-error model

**Status: frozen 2026-11-19. Nothing in this folder may change.** Any change of features, constants,
coefficients, centring or threshold is a new version in a new folder (`frozen/v2`, or `experimental/`).

| Item | Value |
|---|---|
| What it predicts | `actual total − closing total`, i.e. how wrong the market's total will be |
| Output | `signal` (points, centred). Bet OVER if `signal ≥ +1.5`, UNDER if `signal ≤ −1.5`, else no bet |
| "Projected total" | It does not produce one. The implied total is `line + signal` for whatever line is being considered |
| Model | Ridge regression on 33 standardised pregame factors; alpha 2154.43 chosen by leave-one-out CV over `logspace(0,4,13)` |
| Training data | 50,297 D1-vs-D1 games with a closing total, seasons 2015-16 … 2025-26 |
| Training file | `data/processed/games.parquet`, sha256 `1d70f337…1f499`, repo commit `8527a46` |
| Target lines | SBR archive close through 2020-21; ESPN multi-book median 2021-22 … 2023-24; DraftKings close 2024-25 … 2025-26 |
| Centring | Raw prediction minus the training mean of the target (+0.7255). The mean is overtime skew; the median market miss is 0.0 |
| Threshold | 1.5 points (chosen after seeing 2019–2026 walk-forward results — see weaknesses) |
| Code | `features.py` (definitions), `predict.py` (scoring), `model.json` (all numbers), `check.py` (regression test) |
| Fitting script | `src/freeze_model.py` (kept for the record; do not rerun to overwrite) |

`python frozen/v1/check.py` confirms the frozen code reproduces the stored training signals
(max difference 8e-16) and rebuilds the dataset's style features from raw box scores (max difference 4e-6).

## Inputs (all must exist before tip-off)

1. **Ratings snapshot**: each team's Torvik adjusted tempo from the time-machine file dated the day
   *before* the game (the file dated the game day already contains that day's results).
2. **Season-to-date box-score rates** for both teams from games played strictly before the game date,
   shrunk toward frozen league means with 4 pseudo-games (`league_means_per_game` in `model.json`).
3. **Returning minutes**: share of last season's minutes played by players on this season's roster.
4. **New head coach** flag.

## The 33 factors

Offence rates are what a team does; `opp_` rates are what its defence allows or forces. Unless noted,
each factor is the **sum of the two teams' values**.

| Family | Factor | Definition |
|---|---|---|
| Pace | `pace_absdiff` | absolute gap between the two adjusted tempos |
| | `pace_sum` | both tempos minus twice the day's average tempo |
| | `pace_inter` | product of the two tempo deviations |
| | `pace_fast_slow`, `pace_slow_side` | faster / slower team's tempo deviation |
| Roster | `roster_turnover`, `roster_turnover_max` | 1 − returning minutes (average of the two; higher of the two) |
| | `roster_new_coach` | number of teams with a new head coach |
| | `roster_early` | `exp(−games played / 6)` for the less-experienced team |
| | `roster_turnover_x_early`, `roster_new_coach_x_early` | interactions |
| Shot profile | `shot_3par`, `shot_ftr` | 3PA/FGA, FTA/FGA |
| | `shot_orb`, `shot_tov`, `shot_ast` | offensive rebound rate, turnovers per possession, assists per made FG |
| | `shot_3p_pct`, `shot_2p_pct`, `shot_ft_pct` | shooting percentages to date |
| | `shot_3par_absdiff` | gap between the teams' 3PA rates |
| Opponent style | `opp_3par`, `opp_3p_pct`, `opp_ftr` | opponents' 3PA rate, 3P%, FT rate allowed |
| | `opp_tov`, `opp_orb` | turnovers forced per possession, offensive rebound rate allowed |
| | `opp_stl`, `opp_blk`, `opp_foul` | steals per possession, blocks per opponent FGA, fouls per possession |
| | `opp_x_3par`, `opp_x_tov`, `opp_x_orb`, `opp_x_ftr` | offence tendency × opposing defence tendency, both directions |
| | `opp_x_pace_press` | tempo deviation × opposing defence's forced-turnover rate |

Standardisation means/SDs and coefficients are in `model.json`. Largest coefficients (points per SD):
`opp_ftr` −0.69, `opp_3p_pct` −0.50, `shot_2p_pct` −0.41, `opp_orb` +0.38, `opp_stl` −0.33, `opp_blk` −0.32.

## Known weaknesses (documented before any forward result was seen)

1. **Threshold and centring were chosen after looking at walk-forward results.** That is the main reason
   the 2026-27 forward test matters.
2. **In-sample history.** v1 is fit on every season through 2025-26, so its historical signals are in-sample.
   Historical out-of-sample evidence comes from the walk-forward refits in `src/analyze.py` / `src/phase2.py`.
3. **Returning minutes used the end-of-season roster in training** (a player who left mid-season is known
   slightly early). Live scoring uses the roster to date. Roster coefficients are all ≤ 0.12 in size.
4. **Mixed closing-line sources in the target**, none timestamped; one book only for the last two seasons.
5. **Day-level tempo centring** depends on which games are scored that day; score the full slate.
6. **Staleness.** A prediction logged more than a day ahead uses an older ratings snapshot and fewer games
   than training did. The log records the snapshot date and games-in-inputs so this can be audited.
7. **Torvik update timing.** If last night's late games are not yet in Torvik's files when the log runs,
   inputs are a day stale.
8. **It is a market-error model, not an independent projection.** It says which way a line is likely wrong,
   not what the total "should" be before a line exists.
