# Data source register

Status as of 2026-11-19. "PIT" = point-in-time accurate (the historical record shows what was known then).

## In use

| Source | Provides | Coverage | PIT? | Available before a bet? | Limits / notes |
|---|---|---|---|---|---|
| **Torvik `*_super_sked.csv`** | Schedule, frozen pregame line (trailing field), results, box score, possessions, OT | 2008→; frozen tempo from 2015-16 | Frozen field yes (r=0.990 with day-before rebuild). **Headline columns no — recomputed, leaky** | Yes, morning of game | Only timestamped to the day. Free |
| **Torvik time machine** | Daily team ratings snapshot | 2014-15→ | Yes; file dated D includes D's games, so use D−1 | Yes | Older files use old school names (aliased) |
| **Torvik player stats** | Player-season minutes, class | 2008→ | **No** (end-of-season) | Roster list yes, minutes no | Used only for returning-minutes share |
| **Torvik game stats** | Coach names per game | 2008→ | Yes | Yes | |
| **SBR archive** (sportsbookreviewsonline.com) | One open, one close per game | 2007-08 → 2020-21 (2021-22 page no longer downloadable) | Unknown book, no timestamps | n/a | Agrees with ESPN close within 0.5 on 88% of games |
| **ESPN scoreboard API** | Event id, tip time, venue id/name/city, tournament note, half scores, attendance | 2014-15→ | Yes | Yes | Free, unofficial |
| **ESPN core odds API** | Per-book total, prices, spread | See below | Not timestamped | Current number yes | Free, unofficial |

ESPN odds detail by season:

| Seasons | Books | Open | Close | Prices |
|---|---|---|---|---|
| 2014-15 … 2016-17 | 4–9 offshore/Vegas (5Dimes, BetOnline, Bovada, Pinnacle, Westgate) | A separate "Opening" row for some 2014-15 games | Last quoted number | Yes |
| 2017-18 … 2022-23 | 5–14 (Caesars, DraftKings, Unibet, SugarHouse, Westgate…) | No | Last quoted number | Yes |
| 2023-24 | 10–11 | **Per book, with prices** | **Per book, with prices** | Yes |
| 2024-25 … 2026-27 | DraftKings (plus ESPN BET for some) | Yes | Yes | Yes |

## Verified available, not yet collected

| Source | Provides | Why it matters | Cost / limits |
|---|---|---|---|
| **ESPN game summary API** | Full play-by-play with clock and wall-clock time, play types (layup / dunk / jump shot, fouls, turnovers), **officiating crew** | Possession length, late-game fouling, shot mix, referee tendencies. Checked for 2014-15, 2018-19 and 2023-24 games | Free; ~65k calls, ~20 GB raw. No shot coordinates. Referee assignments are not reliably public before tip |
| **The Odds API** | Per-book totals with prices, snapshot timestamps | The only verified retail source of timestamped multi-book history | NCAAB from 2020-11-16; 10-min snapshots, 5-min from Sept 2022. $30 / $59 / $119 / $249 per month. Historical call = 10 credits per region. No explicit opener field — derived from the first snapshot a book appears in. No Pinnacle/Circa in US regions (not verified). Research use and indefinite storage allowed |
| **TeamRankings movement pages** | Timestamped total movement with an Open row | Free timestamps | Anonymous books, no prices, scrape only |

## Checked and set aside

| Source | Finding |
|---|---|
| hoopR release files | The file URLs tried returned 404; not pursued since ESPN serves the same data directly |
| SportsDataIO, OpticOdds, OddsJam, Unabated | Sales-quote or enterprise pricing; NCAAB depth not published |
| SportsGameOdds | Open/close per book only, $299/month for history |
| Pinnacle | No public archive found |
| Kaggle / GitHub | No multi-book timestamped NCAAB totals dataset found |
| **Bookie Beats** | No export, API or line history advertised publicly. Lists Circa, Pinnacle and BookMaker, which The Odds API's US regions do not. The subscriber's own alert history is the only trail — worth asking them |

## What can be established historically vs only prospectively

| Question | Historical data can answer | Needs prospective measurement |
|---|---|---|
| Does the signal beat the close? | Yes (11 seasons) | Confirmation only |
| Does it beat "the opener"? | Partly: 9 seasons of an untimestamped opener | Whether that number was bettable, at what limit, for how long |
| Which book opens first / softest? | One season (2023-24), no timestamps | Yes — or buy The Odds API history (2020-21→) |
| Best time to bet between open and close | No | Yes — or The Odds API history |
| Value of line shopping | Upper bound only | Yes |
| Books the user can actually bet | No | User's own access and limits |
