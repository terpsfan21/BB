# Findings: are Torvik's totals errors predictable, and is there an edge?

Scope: 59,673 D1-vs-D1 games, 2015-16 through 2025-26, of which 50,878 have a closing total.
(2014-15 is in the dataset but excluded here because Torvik did not store a pregame possession
projection that year.) Out-of-sample tests train on all seasons before S and score season S, for
S = 2019 … 2026. Every number below is in `results.md`.

## Verdict

**Do not build a totals model on "fixing Torvik". There is no evidence of an advantage there.**
Torvik's errors are very predictable, but the closing line has already corrected them.

There is one thing worth a second look: a small, statistically solid mispricing in the **closing
line itself**, tied mostly to defensive style. It clears the −110 vig only at selective thresholds
and by a thin margin. I'd call it a lead to confirm on fresh data, not a demonstrated repeatable
advantage.

## 1. The dataset has a trap: most of Torvik's "pregame" columns are not pregame

Torvik's season schedule file carries two projections. The headline columns (line, projected
points, projected tempo) are **recomputed with later ratings**. A trailing field holds the line as
it stood before the game.

| Check | Frozen field | Headline columns |
|---|---|---|
| Correlation with a rebuild from day-before ratings | 0.990 | 0.877 |
| MAE vs actual total (games with odds) | 13.70 | 12.58 |

The headline columns "beat" the closing line (13.36) only because they have seen the future. Any
backtest built on them is invalid. Everything here uses the frozen field.

## 2. Baseline

| | Bias (actual − forecast) | MAE | Calibration slope |
|---|---|---|---|
| Torvik frozen total | +0.74 | 13.70 | 0.80 |
| Closing total | +0.73 | 13.36 | 1.00 |

- The close beats Torvik in all 11 seasons, by about 0.35 points of MAE.
- Torvik's totals are too spread out: for each point he projects above average, only 0.80
  arrives. Projected possessions have the same problem (slope 0.83).
- About 70% of the variance in Torvik's total error is scoring efficiency, about 35% is pace
  (they offset slightly).
- Both forecasts run about 0.7 under on average, but the median closing-line miss is 0.0 and
  betting every over wins 50.15%. The mean is overtime skew, not an over edge.

## 3. Which factors predict Torvik's error

Slopes are points of total error per one standard deviation, within season, all 11 seasons.

| Family | What shows up | Slope (t) | Same sign in |
|---|---|---|---|
| Pace mismatch | The *gap* between the two tempos does almost nothing | −0.11 (−1.5) | 7/11 |
| | Combined pace *level*: fast games come in under Torvik | −0.91 (−12.4) | 11/11 |
| Roster change | Turnover, new coach: weak, mostly efficiency not pace | +0.19 (2.3) | 9/11 |
| | Early-season games run under Torvik | −0.50 (−5.3) | 10/11 |
| Shot profile | Hot 3-point shooting to date → under (regression) | −0.99 (−13.5) | 11/11 |
| | Hot 2-point shooting to date → under | −0.73 (−9.6) | 11/11 |
| | High free-throw rate → under | −0.65 (−8.5) | 11/11 |
| Opponent style | Opponents' 3P% allowed to date → strong regression | −1.34 (−17.7) | 11/11 |
| | Foul-prone defences → under | −0.56 (−7.5) | 11/11 |

The matchup interaction terms (three-point-heavy offence vs. defence that allows threes, pressing
defence vs. fast offence, and so on) add little. The dominant story is that Torvik under-regresses:
extreme pace and shooting luck, especially opponent three-point percentage.

## 4. Out of sample, on Torvik's own error

| Factors used | Total: OOS R² | t | Seasons improved | Possessions: OOS R² |
|---|---|---|---|---|
| Pace mismatch | 0.34% | 8.3 | 8/8 | 1.93% |
| Roster change | 0.08% | 2.0 | 7/8 | 0.01% |
| Shot profile | 0.44% | 5.5 | 7/8 | 0.74% |
| Opponent style | 0.71% | 8.9 | 8/8 | 0.63% |
| All four | 1.42% | 9.3 | 8/8 | 2.68% |

So yes: three of the four families predict Torvik's errors out of sample, reliably, every season.
Roster change barely registers. The combined correction has a standard deviation of 2.3 points and
cuts Torvik's MAE from 13.44 to 13.35 — which still leaves it well behind the close at 13.29 on
the same games.

## 5. Against the market

**Torvik, corrected or not, adds nothing to the close.**

- In a regression of the actual total on Torvik and the close together, Torvik's weight is −0.04
  (t = −1.7); corrected Torvik's is +0.04 (t = 1.7). The close takes all the weight.
- Betting the raw Torvik-vs-close gap wins 49.3–49.7% at every threshold from 1 to 6 points, and
  beat break-even in 0 of 8 seasons. Bigger disagreements with the market are not better bets.
- Betting the corrected gap wins about 50.5%.

**The factors do predict a little of the closing line's own error.** Fitting the factors directly
to (actual − close), walk-forward:

| Factors used | OOS R² | t | Seasons improved |
|---|---|---|---|
| Pace mismatch | 0.02% | 1.0 | 5/8 |
| Roster change | −0.02% | −0.7 | 3/8 |
| Shot profile | 0.04% | 1.6 | 7/8 |
| Opponent style | 0.21% | 4.7 | 8/8 |
| All four | 0.19% | 2.8 | 6/8 |

Betting that model's signal against the close at −110 (break-even 52.38%):

| Signal at least | Bets | Win % | ROI | z vs break-even | Seasons above break-even |
|---|---|---|---|---|---|
| 0.5 pts | 25,788 | 52.12 | −0.5% | −0.8 | 4/8 |
| 1.0 pts | 14,917 | 52.69 | +0.6% | +0.8 | 5/8 |
| 1.5 pts | 7,265 | 53.74 | +2.6% | +2.3 | 7/8 |
| 2.0 pts | 2,978 | 53.26 | +1.7% | +1.0 | 5/8 |

- The win rate is far above a coin flip (z ≈ 6.5), so the signal is real, and it is split evenly
  between overs (52.7%) and unders (52.7%).
- It is only clearly above the vig in one threshold band, and I did not fix that threshold in
  advance.
- The factors that hold up in both halves of the sample (2016–20 and 2021–26) are all on the
  defensive side: teams whose defences foul a lot, send opponents to the line, block shots, force
  steals, or have allowed a high three-point percentage go **under** the close; games where the
  slower team is still fairly fast go **over**. Each is worth 0.25–0.5 points per standard
  deviation.
- Against the opening line (2023-24 on, the only seasons with one), the same signal does better:
  53.1% at 1.0 and 55.0% at 1.5, above break-even in 3 of 3 seasons. The line also moves toward
  the signal between open and close (correlation 0.14). That is what a real effect would look
  like, but it is three seasons from a single book.

## What I'd trust less

- **Line quality.** Closes are the SBR archive through 2020-21 and an ESPN multi-book median
  after; the two agree within half a point on 88% of overlapping games. For 2024-25 and 2025-26
  ESPN lists one book only. None of this is timestamped, and no price other than −110 is modelled.
- **Choices made after seeing results.** The first pass bet the uncentred model output, which was
  mostly overs and won 52.2% at 1.0. Centring it on the historical mean is the right handling of
  the overtime skew, but I made that call after seeing the first pass. Thresholds were not
  pre-set either.
- **Regulation only**, the 1.5-point band drops from 53.7% to 53.1%, so some of the margin is
  overtime luck.
- **Roster features** use each team's final roster list to decide who "returned", so mid-season
  departures are known slightly early. Since roster change showed nothing, this doesn't alter a
  conclusion.
- **Style features** are simple season-to-date box-score rates, not opponent-adjusted.

## Suggested next step

Freeze the factors-only market model exactly as it is in `src/analyze.py` (fit through 2025-26,
1.5-point threshold, centred) and score it on the 2026-27 season now in progress, against lines
captured with timestamps at open and close. If it holds near 53–54% there, a model is justified,
and it should be a model of the *market's* error built on defensive style — not a Torvik
correction.
