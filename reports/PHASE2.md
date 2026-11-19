# Phase 2: where the totals market is beatable

Scope: 59,673 D1-vs-D1 games, 2015-16 … 2025-26. 50,878 have a closing total and 40,153 an opening
total (2015-16 … 2020-21 and 2023-24 … 2025-26; none for 2021-22 and 2022-23). Every table is in
`phase2_results.md`; the 2026-27 forward log is in `forward_test.md`.

## Bottom line

1. **Openers are softer than closes, and the existing signal finds it.** At the 1.5-point threshold
   the signal wins 55.1% against the opener (5,594 bets, 95% CI 53.8–56.4, above break-even in 6 of 6
   seasons) and 53.5% against the close on the same games (CI 52.2–54.8).
2. **That opener was not necessarily bettable.** None of the historical opening numbers has a
   timestamp, a named book (before 2023-24) or a limit. This is the single biggest gap, and it can
   be closed with one purchase.
3. **Two new effects held up in seasons that were not used to find them**: a home-gym effect, and
   overs at altitude. Neither is corrected between open and close.
4. **Several of your hypotheses did not hold**: no market overreaction to hot or cold shooting,
   nothing at Mohegan Sun, and Feast Week leans under rather than over.

I would still not build a production model. I would buy timestamped odds history, keep the forward
log running daily, and decide in January.

---

## A. Frozen model validation

The factors-only market-error model is frozen in `frozen/v1/` (see `MODEL_CARD.md` there).

| Preserved | Where |
|---|---|
| 33 feature definitions and transformations | `frozen/v1/features.py` |
| Coefficients, standardisation means/SDs, ridge alpha | `frozen/v1/model.json` |
| Centring (+0.7255) and 1.5-point threshold | `frozen/v1/model.json` |
| League constants that the features silently depended on | `frozen/v1/model.json` |
| Training data: 50,297 games through 2025-26 | `games.parquet`, checksum and commit recorded |
| Regression test | `frozen/v1/check.py` — reproduces training signals to 8e-16 |

**It can score 2026-27 legitimately.** It needs only Torvik ratings from the day before, box scores
of earlier games, and roster/coach flags — no market data at all.

**Forward log so far** (`data/forward/`, append-only, committed so the git history timestamps it):

| Kind | Games | What it is |
|---|---|---|
| Prospective | 127 (27 flagged bets) | Logged 2026-11-19 09:56 UTC for games tipping Nov 19–21, before tip-off |
| Reconstruction | 771 (85 flagged bets) | Games of Nov 2–18, scored after the fact from pre-game inputs |

The reconstructions are a pipeline check, not evidence: 85 bets, 52.9% (CI 42–63), mean closing-line
value +0.93 points, signal-to-line-move correlation +0.14 (the historical figure is +0.15).

**Weaknesses that remain** (full list in the model card):

- The 1.5 threshold and the centring were chosen after seeing 2019–2026 results.
- Returning-minutes used end-of-season rosters in training. Roster coefficients are tiny.
- It outputs a deviation from a line, not a total. It cannot tell you a number before a line exists;
  it can tell you which side of any line to be on, before that line exists.
- The forward log only captures what ESPN shows (DraftKings), stamped with *our* observation time.
- **The log runs only when someone runs it.** Today's run was manual. See "Decisions I need".

## B. Odds data: what we have and what is missing

| Have | Missing |
|---|---|
| A closing total for 50,878 games | Timestamps on any historical line |
| An opening total for 40,153 games (source unnamed before 2023-24) | Which book opened first, and when |
| Per-book closes with prices, 5–14 books, 2014-15 … 2023-24 | Per-book openers outside 2023-24 |
| Per-book open **and** close with prices, 10 books, 2023-24 only | Intermediate prices, any season |
| DraftKings open and close with prices, 2024-25 → today | Limits, and the books you actually use (Circa, Pinnacle, BookMaker are not in any free source) |

**Recommended collection:** The Odds API. It is the only source I could verify that sells timestamped
per-book totals with prices at a published price (history from November 2020; 5-minute snapshots
from September 2022). One month of the $119 plan covers the full history; the $30 plan covers
5-minute live polling for the rest of this season. Details and the alternatives I ruled out are in
`docs/DATA_SOURCES.md`. I have not bought anything.

## C. The eight stable factors

**In basketball terms.** Totals go **under** the close when the two teams' defences foul a lot, send
opponents to the line, block shots, get steals, or have been burned from three so far; and when the
offences live at the line or on the offensive glass. Totals go **over** when even the slower team
plays reasonably fast.

| Factor | Effect on (actual − close) per SD | 95% CI | Seasons same sign | With all eight together | Against the opener |
|---|---|---|---|---|---|
| FT rate allowed (`opp_ftr`) | −0.47 | −0.63, −0.32 | 11/11 | −0.75 | −0.51 |
| Fouls per possession (`opp_foul`) | −0.41 | −0.58, −0.24 | 10/11 | **+0.40** (flips) | −0.42 |
| 3P% allowed (`opp_3p_pct`) | −0.35 | −0.51, −0.19 | 11/11 | −0.49 | **−0.84** |
| Own FT rate (`shot_ftr`) | −0.32 | −0.48, −0.17 | 10/11 | −0.35 | −0.44 |
| Steal rate (`opp_stl`) | −0.29 | −0.45, −0.13 | 9/11 | −0.17 (fades) | −0.19 |
| Block rate (`opp_blk`) | −0.27 | −0.42, −0.12 | 9/11 | −0.30 | −0.19 |
| Own offensive rebounding (`shot_orb`) | −0.24 | −0.40, −0.09 | 10/11 | −0.11 (gone) | −0.17 |
| Slower team's tempo (`pace_slow_side`) | +0.32 | +0.17, +0.47 | 11/11 | +0.49 | +0.31 |

- **They are not eight things.** Fouling and FT rate allowed correlate 0.88 and are one factor. In
  effect there are about six independent signals, and five carry the weight together: free throws
  allowed, three-point luck allowed, blocks, own free-throw rate, and slow-side pace.
- **Opponent adjustment adds nothing.** Adjusted and raw versions correlate 0.94–0.99 and predict
  equally.
- **Controlling for the market changes little.** Adding the closing total, the spread and the
  Torvik-vs-close gap leaves the five intact.
- **They are stronger before January** (free throws allowed: −0.89 before, −0.30 after) and
  **stronger in games with no major-conference team** (−0.60 vs −0.17 when both are majors). Three-point
  luck allowed is the exception: it is strongest in major-conference games.
- **The market fixes some and not others between open and close.** It removes about 55% of the
  three-point-luck error and 67% of the own-three-point-shooting error, but only about 16% of the
  free-throw and fouling error.
- **After the vig:** the eight alone win 54.7% at 1.5 against the close (3,094 bets, CI 53.0–56.5,
  7 of 8 seasons) and 55.1% against the opener (2,436 bets, CI 53.1–57.1, 6 of 6). Fewer bets than
  the 33-factor model, slightly higher hit rate.

## D. Ranked research opportunities

| Rank | Opportunity | Why | Status |
|---|---|---|---|
| 1 | **Bet timing: opener vs later prices** | Largest measured edge; the line moves toward the signal (t = 20) | Promising; blocked on timestamped odds |
| 2 | **Home-gym and altitude effects** | New, replicated, large for a single factor, not corrected by the market | Promising |
| 3 | **Defensive-style factors, consolidated to five** | 11 seasons of consistency; strongest early and in smaller conferences | Established as real; thin after vig at the close |
| 4 | **Market under-reaction to recent pace and recent totals** | Replicated; the opposite of the overreaction idea | Promising |
| 5 | **Line shopping across books** | Up to ~0.9 points and ~2 points of win rate; holds differ by book from 4.7% to 8.6% | Upper bound only until timestamps exist |
| 6 | **Neutral sites and multi-day tournaments: unders at the open** | Openers run 1.4–1.8 points too high; the market fixes about half | Promising at the open only |
| 7 | **Coach-level persistence** | Replicated but small | Promising |
| 8 | **Referee crews** | Officials are in ESPN's game data back to 2014-15; fouls drive the top factor | Speculative; assignments may not be public before tip |
| 9 | **Play-by-play: possession length, late-game fouling, shot mix** | Available free back to 2014-15; could sharpen pace and foul factors | Speculative; large collection job |
| 10 | **Injuries and lineup changes** | Plausible, but I found no free point-in-time source | Speculative; data limitation |

Rejected on the evidence: shooting-regression overreaction, overtime hangover, pace-control
interactions, roster turnover and new coaches, spread and game-state effects, total level,
conference tier, day of week.

## E. Exploratory findings

### Opening vs closing

| Test | Result |
|---|---|
| Accuracy | The close beats the opener in all 9 seasons, by 0.07–0.25 points of average miss |
| Size of moves | Average 1.8 points; about 72% of totals move a point or more, 17–33% move three or more depending on the season |
| Is the move informative? | Fully. Each point of move is worth 1.07 points of final score (t = 30) |
| Signal vs opener, threshold 1.5 | 55.1%, 5,594 bets, 6/6 seasons, ROI +5.2% at −110 (CI +2.7 to +7.7) |
| Signal vs close, same games | 53.5%, ROI +2.1% (CI −0.4 to +4.6) |
| Does the signal anticipate the move? | Yes: correlation 0.15, t = 20; the line moved toward flagged bets 47–64% of the time and against 24–33% |
| A model trained on opening errors instead | No better: 54.2% at 1.5 |
| **Torvik's total vs the opener** | **No edge**: 50.5% at a 2-point gap, 52.1% at 5 points |

The direct-projection approach fails against the opener just as it failed against the close. What
works is modelling the market's own mistakes.

**Which games move most:** games early in the season (2.4 points on average in a team's first three
games vs 1.7 later), neutral-site games, and games where Torvik disagrees with the opener. Games
between two non-major teams move less.

**Sportsbooks (2023-24, the one season with per-book openers):** all ten books' openers were about
equally accurate (average miss 13.32–13.41), and the signal won 54–55% against every one. Price is
what separated them: hold on totals was 4.7% at DraftKings, MGM and ESPN BET but 6.1% at Unibet,
7.8% at Caesars Tennessee and 8.6% at Betfair, which turned a +5% return into −0.7%. Taking the
best of ten openers lifted the win rate from 54.8% to 56.7% — an upper bound, since those numbers
were not all live at once.

### New hypotheses: 53 tests, found on 2016–22, checked on 2023–26

Eight replicated. Slopes are points of (actual − close).

| Finding | 2016–22 | 2023–26 | Against the opener |
|---|---|---|---|
| **Home gym**: home team's home games ran over/under the close last season (per SD) | +0.51 (t 4.5) | +0.67 (t 5.0) | +0.62 (t 6.2) |
| **Altitude home game** (17 schools above 4,000 ft) | +1.40 (t 2.9) | +2.02 (t 3.5) | +2.02 (t 4.8) |
| Altitude team hosting a low-elevation visitor | +1.31 | +1.50 | +2.05 |
| Last game's pace above the team's norm (per SD) | +0.49 (t 4.7) | +0.37 (t 3.0) | +0.65 (t 7.3) |
| Teams' previous game went over its close (per SD) | +0.27 | +0.33 | +0.30 |
| Coach's career record vs the close (per SD) | +0.38 | +0.25 | +0.42 |
| Any neutral-site game | −0.76 | −0.76 | −1.42 |
| Conference games from February on | +0.52 | +0.60 | +0.47 |

- **The home-gym effect is about the building, not the team.** A home team's *home* games last
  season predict (+0.58, t 6.4); the same team's *road* games do not (−0.01). It survives dropping
  the altitude schools. Betting it alone won 53.3% against the close in 2023–26 (3,218 bets,
  4 of 4 seasons).
- **Altitude:** overs hit 55.3% in 2,179 home games (CI 53.3–57.4), and 57.5% in the 2023–26
  seasons alone (CI 54.2–60.7). The average miss was positive in all 11 seasons. The list of schools
  was written down before any result was computed.
- **Adding the discovery-period features to the 33 factors** lifted the 2023–26 result from 54.0%
  to 54.3% at 1.5 against the close while nearly doubling the bets (3,503 → 6,218), and to 55.6%
  against the opener (4,757 bets, CI 54.2–57.1). The added features were chosen without seeing
  those seasons; the threshold was not.

### Your specific ideas

| Idea | Finding |
|---|---|
| Mohegan Sun | No evidence: +0.9 points vs the close over 103 games (t = 0.6), overs 50.5% |
| Maui (Lahaina) | +3.1 points over 78 games, but t = 1.5 and overs only 51.3% — a few big games |
| Battle 4 Atlantis | Nothing: +0.2 over 114 games |
| Feast Week as a whole | Leans **under**: overs 47.5% of 2,189 neutral-site games (CI 45.4–49.6). Openers ran 1.8 points too high and moved down 0.8. Flat since 2022 |
| Venues in general | Some real variation: 8 of 49 busy neutral venues stand out where 2 would by chance. A venue's past does carry forward (+1.05 then +0.54 per SD) but it just missed replicating |
| Sportsbooks overreact to hot/cold shooting | **No.** Six versions (last game 3P%, opponent 3P%, last three games, eFG%, FT%, overtime) all null in both periods |
| Regression to the mean | Real for season-long three-point luck (the opener is off by 0.84 points per SD) but the market corrects more than half by the close |
| Who controls pace | The slower team has slightly more say (weight 0.88 vs 0.80, t = 5.4). The market already prices it; no interaction term replicated |
| Roster turnover, new coaches | Null against both the opener and the close |
| First games of the season | The 2016–22 early-season under is gone (−0.98, then −0.27) |
| Close games and late fouling | Overtime is far more common in pick'em games (8.0% vs 1.7% in blowouts) but the market prices it: overs 49.5–50.8% in every spread band |
| Back-to-back tournament days | Openers 1.6 points too high (t −4.4); the close fixes it in recent seasons |

## F. Recommendation

**Highest expected value: establish whether the opener edge is executable.** Everything else is
secondary to that, because it is the largest effect and the one with the weakest data underneath.

1. Buy one month of The Odds API ($119) and pull per-book totals history from 2020-21. Re-run
   Section 1 at realistic entry points: first appearance at each book, 30 minutes later, morning of
   the game, an hour before tip.
2. Run the forward log every day so each flagged bet has a pre-tip timestamp and an observed price.
3. Leave v1 frozen. Build the venue, altitude and recent-pace factors into a separate experimental
   model, and collect venue elevations and referee crews to test whether they explain the home-gym
   effect.

**What would justify a live model:**

- On timestamped history, at least 54% at prices that were available for 30 minutes or more, with
  the interval's lower bound above 52.4%, across at least four seasons.
- In the 2026-27 forward log, average closing-line value of +0.5 points or better on 300 or more
  flagged bets. Closing-line value will answer months sooner than win rate: separating 54% from
  52.4% takes roughly 2,500 bets.

### Where each claim stands

| Established | Promising, unconfirmed | Speculative | Data limitation |
|---|---|---|---|
| Torvik's headline history is leaky | Opener edge is bettable | Referee crews | No timestamps on any historical line |
| Direct projection (Torvik) has no edge vs open or close | Home-gym effect | Play-by-play factors | No openers for 2021-22, 2022-23 |
| Market's errors are predictable from style factors | Altitude overs | Injuries and lineups | One book only for 2024-25 on |
| Opener is less accurate than close; moves are fully informative | Recent-pace under-reaction | Venue-specific effects for tournament sites | No limits, no Circa/Pinnacle/BookMaker |
| Signal predicts line movement | Line shopping worth ~0.9 points | | Roster data is end-of-season, not point-in-time |
| No overreaction to hot/cold shooting | 33 + new features at 54–56% | | Forward sample is days old |

### Checks on my own work

- Choices made after seeing results: the 1.5 threshold and the centring (Phase 1). Both are now
  frozen. The 2023–26 seasons were "validation" for the 53 new tests but had already been seen in
  Phase 1 for the 33 original factors.
- The altitude list is from memory of campus elevations, not a measured dataset.
- 53 tests at a 10% false-discovery rate means roughly two of the 21 discovery hits are expected to
  be false; the replication step is there to catch them.
- Win rates assume −110 unless a table says "actual price". Where real prices exist (DraftKings,
  2024-25 on) the average hold is 4.74% and results are within 0.1 points of the −110 figure.
