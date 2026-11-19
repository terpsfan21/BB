# Phase 2: generated results

Games 2015-16..2025-26: 59,673; with close 50,878; with an opening total 40,153 (SBR 2016-21, ESPN per-book 2024-26; none for 2022-23).

## 1. Opening vs closing totals

|   season |   games |   open_MAE |   close_MAE |   mean|move| |   moved>=1 |   moved>=2 |   moved>=3 |   corr(move, actual-open) | source           |
|---------:|--------:|-----------:|------------:|-------------:|-----------:|-----------:|-----------:|--------------------------:|:-----------------|
|     2016 |    3611 |      13.74 |       13.67 |         1.68 |      67.16 |      38.99 |      20.60 |                      0.14 | sbr              |
|     2017 |    3708 |      13.53 |       13.38 |         2.10 |      75.62 |      47.87 |      28.75 |                      0.13 | sbr              |
|     2018 |    3714 |      13.90 |       13.71 |         1.95 |      73.88 |      44.24 |      25.12 |                      0.15 | sbr              |
|     2019 |    4886 |      13.78 |       13.64 |         1.76 |      67.60 |      39.09 |      21.84 |                      0.15 | sbr              |
|     2020 |    4865 |      13.58 |       13.40 |         1.86 |      69.62 |      42.61 |      25.04 |                      0.16 | sbr              |
|     2021 |    3367 |      13.40 |       13.15 |         1.80 |      71.76 |      41.43 |      21.12 |                      0.19 | sbr              |
|     2024 |    5262 |      13.35 |       13.23 |         1.56 |      64.67 |      35.44 |      17.12 |                      0.11 | espn_book_median |
|     2025 |    5279 |      13.02 |       12.86 |         1.54 |      77.23 |      40.05 |      19.00 |                      0.15 | espn_book_median |
|     2026 |    5330 |      13.83 |       13.60 |         2.10 |      83.02 |      54.22 |      32.63 |                      0.18 | espn_book_median |

Regression actual-open on move: slope 1.068 (t=30.3). Slope 1 = the move is fully informative and the opener was simply stale by that amount.

### 1a. Betting WITH the eventual move (not executable - it uses the close - but it sizes the prize)

|   bet open when |close-open| >= |   bets |   win% |   ci_lo |   ci_hi |   ROI% |   ROI_lo |   ROI_hi | seasons>BE   |
|--------------------------------:|-------:|-------:|--------:|--------:|-------:|---------:|---------:|:-------------|
|                               1 |  28719 |  56.59 |   56.01 |   57.16 |   7.95 |     6.87 |     9.04 | 9/9          |
|                               2 |  16907 |  58.66 |   57.91 |   59.40 |  11.86 |    10.46 |    13.27 | 9/9          |
|                               3 |   9293 |  60.51 |   59.51 |   61.50 |  15.37 |    13.49 |    17.25 | 9/9          |

### 1b. OOS factor signal: opening vs closing line, identical games

|   threshold | line   |   bets |   win% |   ci_lo |   ci_hi |   ROI% |   ROI_lo |   ROI_hi | seasons>BE   |
|------------:|:-------|-------:|-------:|--------:|--------:|-------:|---------:|---------:|:-------------|
|        1.00 | open   |  11122 |  53.62 |   52.70 |   54.55 |   2.36 |     0.60 |     4.11 | 6/6          |
|        1.00 | close  |  11114 |  52.36 |   51.43 |   53.28 |  -0.04 |    -1.80 |     1.71 | 3/6          |
|        1.50 | open   |   5594 |  55.13 |   53.82 |   56.43 |   5.22 |     2.74 |     7.69 | 6/6          |
|        1.50 | close  |   5587 |  53.48 |   52.17 |   54.79 |   2.08 |    -0.39 |     4.56 | 5/6          |
|        2.00 | open   |   2401 |  55.06 |   53.06 |   57.04 |   5.09 |     1.31 |     8.87 | 6/6          |
|        2.00 | close  |   2400 |  52.58 |   50.58 |   54.58 |   0.38 |    -3.41 |     4.18 | 3/6          |

By season at threshold 1.5:

|   season | open_source      |   bets |   open_win% |   close_win% |   avg CLV pts (move toward bet) |   % bets line moved toward |   % moved against |   corr(sig, move) |
|---------:|:-----------------|-------:|------------:|-------------:|--------------------------------:|---------------------------:|------------------:|------------------:|
|     2019 | sbr              |    981 |       53.01 |        50.98 |                            0.92 |                      63.53 |             24.32 |              0.16 |
|     2020 | sbr              |   1329 |       54.85 |        53.08 |                            0.65 |                      55.89 |             32.25 |              0.17 |
|     2021 | sbr              |    528 |       60.61 |        57.41 |                            0.99 |                      60.64 |             29.00 |              0.20 |
|     2024 | espn_book_median |    828 |       54.83 |        53.07 |                            0.51 |                      55.88 |             32.73 |              0.12 |
|     2025 | espn_book_median |    916 |       54.48 |        55.02 |                            0.39 |                      47.05 |             30.02 |              0.09 |
|     2026 | espn_book_median |   1012 |       55.53 |        53.31 |                            0.94 |                      57.11 |             27.27 |              0.20 |

### 1c. Does anything predict the open-to-close move?

| predictor                            | target       |     n |   slope |      t |   corr |
|:-------------------------------------|:-------------|------:|--------:|-------:|-------:|
| OOS factor signal (trained on close) | move         | 28755 |   0.318 | 20.311 |  0.153 |
| OOS factor signal (trained on close) | actual-open  | 28755 |   0.901 | 10.033 |  0.061 |
| OOS factor signal (trained on close) | actual-close | 28755 |   0.583 |  6.636 |  0.040 |
| OOS factor signal (trained on open)  | move         | 28755 |   0.305 | 24.549 |  0.203 |
| OOS factor signal (trained on open)  | actual-open  | 28755 |   0.752 | 11.723 |  0.070 |
| OOS factor signal (trained on open)  | actual-close | 28755 |   0.446 |  7.089 |  0.042 |
| Torvik frozen total - open           | move         | 28755 |   0.074 |  8.943 |  0.100 |
| Torvik frozen total - open           | actual-open  | 28755 |   0.064 |  1.844 |  0.012 |
| Torvik frozen total - open           | actual-close | 28755 |  -0.011 | -0.327 | -0.002 |

### 1d. Direct projection vs market-error model, against the OPENER

Torvik's frozen total is the only independent pregame projection in hand. Bet the opener when Torvik disagrees by the threshold. Caveat: Torvik's number is timestamped only to the game day, the opener is not timestamped at all, so it is unknown which existed first.

| model                                             |   threshold |   bets |   win% |   ci_lo |   ci_hi |   ROI% |   ROI_lo |   ROI_hi | seasons>BE   |
|:--------------------------------------------------|------------:|-------:|-------:|--------:|--------:|-------:|---------:|---------:|:-------------|
| Torvik - open                                     |        2.00 |  18735 |  50.48 |   49.77 |   51.20 |  -3.59 |    -4.94 |    -2.24 | 0/9          |
| Torvik - open                                     |        3.00 |  11640 |  50.96 |   50.05 |   51.87 |  -2.68 |    -4.40 |    -0.97 | 1/9          |
| Torvik - open                                     |        4.00 |   6960 |  51.87 |   50.69 |   53.04 |  -0.97 |    -3.19 |     1.25 | 3/9          |
| Torvik - open                                     |        5.00 |   4058 |  52.09 |   50.56 |   53.63 |  -0.54 |    -3.45 |     2.37 | 4/9          |
| factor signal, trained on close                   |        1.00 |  11122 |  53.62 |   52.70 |   54.55 |   2.36 |     0.60 |     4.11 | 6/6          |
| factor signal, trained on open                    |        1.00 |  15062 |  53.32 |   52.52 |   54.12 |   1.78 |     0.27 |     3.29 | 5/6          |
| factor signal, trained on close                   |        1.50 |   5594 |  55.13 |   53.82 |   56.43 |   5.22 |     2.74 |     7.69 | 6/6          |
| factor signal, trained on open                    |        1.50 |  10028 |  54.23 |   53.25 |   55.20 |   3.50 |     1.65 |     5.35 | 5/6          |
| Torvik-open >= 2 AND factor signal same side >= 1 |        1.00 |   3151 |  53.13 |   51.38 |   54.86 |   1.41 |    -1.89 |     4.72 | 4/6          |

Torvik-vs-open by season (threshold 3):

|   season |    bets |   win% |   avg CLV pts |   corr(edge, move) |
|---------:|--------:|-------:|--------------:|-------------------:|
|  2016.00 |  794.00 |  52.39 |          0.38 |               0.11 |
|  2017.00 |  988.00 |  51.21 |          0.86 |               0.19 |
|  2018.00 |  878.00 |  51.94 |          0.10 |               0.01 |
|  2019.00 | 1623.00 |  50.09 |          0.30 |               0.04 |
|  2020.00 | 1321.00 |  50.95 |          0.18 |               0.05 |
|  2021.00 |  790.00 |  50.89 |          0.48 |               0.14 |
|  2024.00 | 1648.00 |  50.24 |          0.26 |               0.08 |
|  2025.00 | 1828.00 |  51.09 |          0.42 |               0.18 |
|  2026.00 | 1770.00 |  51.07 |          0.32 |               0.08 |

### 1e. Which games move most between open and close?

|                                             |   effect on |move| (pts) |      t |
|:--------------------------------------------|-------------------------:|-------:|
| |Torvik - open| (per pt)                    |                    0.071 |  9.052 |
| games played, min of two teams (per 10)     |                   -0.099 | -5.647 |
| both teams non-major                        |                   -0.150 | -3.713 |
| both teams major                            |                   -0.025 | -0.568 |
| neutral site                                |                    0.185 |  4.897 |
| market spread (per 10 pts)                  |                    0.027 |  1.586 |
| open total level (per 10 pts)               |                    0.033 |  3.133 |
| roster turnover, avg of two teams (per 0.1) |                    0.004 |  0.609 |

Mean |move| 1.81; n=39,381; season fixed effects.

By games already played (the less-experienced of the two teams):

|       |    games |   mean|move| |   open_MAE |   close_MAE |   MAE gain open->close |
|:------|---------:|-------------:|-----------:|------------:|-----------------------:|
| 0-2   |  3211.00 |         2.44 |      13.93 |       13.60 |                   0.33 |
| 3-5   |  3857.00 |         1.96 |      13.60 |       13.48 |                   0.11 |
| 6-10  |  6184.00 |         1.77 |      13.50 |       13.33 |                   0.18 |
| 11-20 | 12708.00 |         1.73 |      13.52 |       13.37 |                   0.15 |
| 21+   | 14062.00 |         1.71 |      13.53 |       13.38 |                   0.15 |

### 1f. Do the factors matter at different stages?

Slope per +1 SD, season fixed effects, date-clustered; games with both open and close.

| factor         | eight   |   vs open |   t_open |   vs close |   t_close |   move |   t_move |   share of open error corrected by close |
|:---------------|:--------|----------:|---------:|-----------:|----------:|-------:|---------:|-----------------------------------------:|
| pace_sum       |         |      0.26 |     2.95 |       0.23 |      2.67 |   0.03 |     1.57 |                                     0.11 |
| pace_inter     |         |      0.28 |     2.96 |       0.18 |      1.98 |   0.09 |     7.23 |                                     0.34 |
| pace_slow_side | *       |      0.30 |     3.30 |       0.27 |      3.00 |   0.03 |     1.94 |                                     0.11 |
| shot_3par      |         |      0.32 |     3.60 |       0.21 |      2.35 |   0.12 |     8.96 |                                     0.36 |
| shot_ftr       | *       |     -0.44 |    -4.81 |      -0.29 |     -3.20 |  -0.15 |   -10.44 |                                     0.34 |
| shot_orb       | *       |     -0.17 |    -1.91 |      -0.20 |     -2.21 |   0.02 |     1.85 |                                   nan    |
| shot_tov       |         |      0.03 |     0.33 |      -0.08 |     -0.81 |   0.11 |     6.37 |                                   nan    |
| shot_ast       |         |     -0.03 |    -0.40 |      -0.07 |     -0.87 |   0.04 |     3.03 |                                   nan    |
| shot_3p_pct    |         |     -0.44 |    -4.74 |      -0.15 |     -1.62 |  -0.29 |   -17.81 |                                     0.67 |
| shot_2p_pct    |         |     -0.45 |    -4.75 |      -0.36 |     -3.81 |  -0.09 |    -5.94 |                                     0.21 |
| shot_ft_pct    |         |      0.04 |     0.50 |       0.21 |      2.44 |  -0.17 |   -11.53 |                                   nan    |
| opp_3p_pct     | *       |     -0.83 |    -9.10 |      -0.37 |     -4.13 |  -0.46 |   -25.23 |                                     0.55 |
| opp_ftr        | *       |     -0.51 |    -5.53 |      -0.42 |     -4.66 |  -0.08 |    -5.62 |                                     0.16 |
| opp_tov        |         |     -0.12 |    -1.31 |      -0.26 |     -2.85 |   0.14 |     9.22 |                                   nan    |
| opp_orb        |         |      0.23 |     2.44 |       0.23 |      2.42 |   0.00 |     0.26 |                                     0.02 |
| opp_stl        | *       |     -0.18 |    -1.89 |      -0.30 |     -3.26 |   0.13 |     8.49 |                                   nan    |
| opp_blk        | *       |     -0.20 |    -2.24 |      -0.27 |     -3.05 |   0.07 |     5.25 |                                    -0.35 |
| opp_foul       | *       |     -0.42 |    -4.23 |      -0.35 |     -3.57 |  -0.07 |    -4.08 |                                     0.17 |
| opp_x_3par     |         |      0.18 |     2.13 |       0.17 |      2.03 |   0.01 |     1.00 |                                     0.06 |
| opp_x_tov      |         |      0.07 |     0.79 |       0.04 |      0.46 |   0.03 |     2.23 |                                   nan    |

### 1g. Sportsbook-level openers and line shopping (2023-24 only: the one season with per-book open AND close with prices)

| book                            |   games |   open_MAE |   close_MAE |   mean|move| |   sig bets@open |   win%@open |   ROI%@open (actual price) |   win%@close |   ROI%@close (actual price) |   avg hold% at open |
|:--------------------------------|--------:|-----------:|------------:|-------------:|----------------:|------------:|---------------------------:|-------------:|----------------------------:|--------------------:|
| BetfairSportsbook               |    4072 |      13.34 |       13.24 |         1.61 |             625 |       53.92 |                      -0.72 |        52.64 |                       -3.13 |                8.57 |
| Caesars Sportsbook (Colorado)   |    5152 |      13.37 |       13.23 |         1.73 |             806 |       54.59 |                       4.18 |        53.09 |                        1.20 |                4.76 |
| Caesars Sportsbook (New Jersey) |    4933 |      13.35 |       13.22 |         1.73 |             768 |       54.17 |                       3.37 |        52.78 |                        0.58 |                4.76 |
| Caesars Sportsbook (Tennessee)  |    5147 |      13.37 |       13.24 |         1.73 |             806 |       54.71 |                       1.54 |        53.16 |                        0.33 |                7.78 |
| DraftKings                      |    4888 |      13.37 |       13.24 |         1.80 |             755 |       54.70 |                       4.33 |        53.38 |                        1.80 |                4.75 |
| ESPN BET                        |    4885 |      13.36 |       13.21 |         1.76 |             773 |       55.37 |                       5.49 |        53.17 |                        1.53 |                4.71 |
| MGM                             |    4883 |      13.33 |       13.23 |         1.41 |             768 |       54.95 |                       4.86 |        53.26 |                        1.68 |                4.74 |
| SugarHouse                      |    4721 |      13.32 |       13.26 |         1.20 |             748 |       54.14 |                       3.36 |        52.81 |                        0.97 |                4.76 |
| Titanbets                       |    4965 |      13.41 |       13.25 |         1.71 |             780 |       55.26 |                       5.46 |        53.43 |                        1.96 |                4.70 |
| Unibet                          |    5190 |      13.34 |       13.29 |         0.96 |             824 |       54.98 |                       3.69 |        54.00 |                        1.48 |                6.05 |

| set                                     |   bets |   median-line win% (-110) |   median ROI% |   best-line win% |   best-line ROI% (actual price) |   ROI_lo |   ROI_hi |   avg pts gained by shopping |   % games best != median |
|:----------------------------------------|-------:|--------------------------:|--------------:|-----------------:|--------------------------------:|---------:|---------:|-----------------------------:|-------------------------:|
| 2023-24 openers (10 books)              |    829 |                     54.83 |          4.64 |            56.69 |                            7.33 |     0.97 |    13.69 |                         0.89 |                    76.02 |
| 2023-24 closes (10 books)               |    828 |                     53.07 |          1.31 |            55.31 |                            3.37 |    -2.93 |     9.67 |                         0.95 |                    85.61 |
| 2021-22 last quoted numbers (~10 books) |    822 |                     54.19 |          3.44 |            56.45 |                            6.10 |    -0.24 |    12.44 |                         0.83 |                    80.19 |
| 2022-23 last quoted numbers (~10 books) |    751 |                     54.57 |          4.11 |            56.46 |                            4.97 |    -1.60 |    11.53 |                         0.92 |                    81.90 |

Best-line rows are an UPPER BOUND: the per-book numbers are not timestamped, so the best one may not have been available at the same moment as the others (most true for openers, which post hours apart).

### 1h. Actual prices instead of a flat -110 (DraftKings open/close, 2024-25 and 2025-26)

|   threshold |    bets |   open win% |   open ROI% actual |   open ROI% if -110 |   close win% |   close ROI% actual |   close ROI% if -110 |
|------------:|--------:|------------:|-------------------:|--------------------:|-------------:|--------------------:|---------------------:|
|        1.00 | 1646.00 |       53.04 |               1.27 |                1.19 |        50.85 |               -2.87 |                -2.98 |
|        1.50 |  821.00 |       54.93 |               4.88 |                4.87 |        52.13 |               -0.42 |                -0.48 |
|        2.00 |  353.00 |       55.24 |               5.55 |                5.46 |        52.97 |                1.14 |                 1.13 |

DraftKings average hold on totals: open 4.74%, close 4.74% (-110/-110 = 4.76%).

## 2. The eight stable factors

### 2a. Overlap: correlation matrix

|                |   opp_foul |   opp_ftr |   opp_blk |   opp_stl |   opp_3p_pct |   shot_ftr |   shot_orb |   pace_slow_side |
|:---------------|-----------:|----------:|----------:|----------:|-------------:|-----------:|-----------:|-----------------:|
| opp_foul       |       1.00 |      0.88 |     -0.04 |     -0.08 |         0.17 |       0.31 |       0.07 |            -0.02 |
| opp_ftr        |       0.88 |      1.00 |     -0.04 |      0.11 |         0.15 |       0.26 |       0.09 |             0.09 |
| opp_blk        |      -0.04 |     -0.04 |      1.00 |      0.20 |        -0.24 |       0.18 |       0.37 |             0.03 |
| opp_stl        |      -0.08 |      0.11 |      0.20 |      1.00 |        -0.19 |      -0.05 |       0.25 |             0.07 |
| opp_3p_pct     |       0.17 |      0.15 |     -0.24 |     -0.19 |         1.00 |      -0.02 |      -0.18 |             0.04 |
| shot_ftr       |       0.31 |      0.26 |      0.18 |     -0.05 |        -0.02 |       1.00 |       0.26 |             0.12 |
| shot_orb       |       0.07 |      0.09 |      0.37 |      0.25 |        -0.18 |       0.26 |       1.00 |             0.01 |
| pace_slow_side |      -0.02 |      0.09 |      0.03 |      0.07 |         0.04 |       0.12 |       0.01 |             1.00 |

Principal components: variance shares 26%, 22%, 13%, 12%, 10%, 8%, 7%, 1%. Effective number of independent factors (participation ratio): 5.8 of 8.

### 2b. One at a time vs all together (actual - close, per +1 SD, season FE, date-clustered)

| factor         |   alone | 95% CI         |     t | seasons same sign   |   joint (8 together) |   t_joint |   joint + market controls |   t_ctrl |
|:---------------|--------:|:---------------|------:|:--------------------|---------------------:|----------:|--------------------------:|---------:|
| opp_foul       |   -0.41 | [-0.58, -0.24] | -4.79 | 10/11               |                 0.40 |      1.99 |                      0.28 |     1.38 |
| opp_ftr        |   -0.47 | [-0.63, -0.32] | -5.88 | 11/11               |                -0.75 |     -3.90 |                     -0.69 |    -3.56 |
| opp_blk        |   -0.27 | [-0.42, -0.12] | -3.49 | 9/11                |                -0.30 |     -3.41 |                     -0.34 |    -3.85 |
| opp_stl        |   -0.29 | [-0.45, -0.13] | -3.56 | 9/11                |                -0.17 |     -1.83 |                     -0.21 |    -2.25 |
| opp_3p_pct     |   -0.35 | [-0.51, -0.19] | -4.40 | 11/11               |                -0.49 |     -5.87 |                     -0.43 |    -4.92 |
| shot_ftr       |   -0.32 | [-0.48, -0.17] | -4.02 | 10/11               |                -0.35 |     -3.97 |                     -0.34 |    -3.85 |
| shot_orb       |   -0.24 | [-0.40, -0.09] | -3.04 | 10/11               |                -0.11 |     -1.19 |                     -0.04 |    -0.47 |
| pace_slow_side |    0.32 | [+0.17, +0.47] |  4.24 | 11/11               |                 0.49 |      6.08 |                      0.78 |     7.12 |

n = 50,878 games with a close. Market controls: closing total level, market spread, Torvik-minus-close.

### 2c. Stage, calendar and conference tier

| factor         |   vs open |   t_open | before Jan (t)   | Jan on (t)   | both major   | mixed        | neither major   |
|:---------------|----------:|---------:|:-----------------|:-------------|:-------------|:-------------|:----------------|
| opp_foul       |     -0.42 |    -4.31 | -0.80 (-4.9)     | -0.25 (-2.5) | -0.17 (-0.8) | -0.43 (-1.5) | -0.51 (-4.8)    |
| opp_ftr        |     -0.51 |    -5.63 | -0.89 (-6.0)     | -0.30 (-3.1) | -0.17 (-0.8) | -0.48 (-1.8) | -0.60 (-6.0)    |
| opp_blk        |     -0.19 |    -2.14 | -0.39 (-2.7)     | -0.22 (-2.4) | -0.23 (-1.3) | -0.16 (-0.6) | -0.31 (-2.9)    |
| opp_stl        |     -0.19 |    -1.96 | -0.36 (-2.5)     | -0.24 (-2.4) | -0.21 (-1.1) | -0.17 (-0.7) | -0.32 (-3.3)    |
| opp_3p_pct     |     -0.84 |    -9.20 | -0.42 (-3.5)     | -0.35 (-3.3) | -0.62 (-3.3) | -0.52 (-2.2) | -0.32 (-3.3)    |
| shot_ftr       |     -0.44 |    -4.81 | -0.57 (-3.9)     | -0.18 (-1.9) | -0.18 (-0.9) | -0.54 (-2.1) | -0.30 (-3.1)    |
| shot_orb       |     -0.17 |    -1.87 | -0.36 (-2.5)     | -0.18 (-1.9) | -0.24 (-1.3) | -0.41 (-1.5) | -0.20 (-2.0)    |
| pace_slow_side |      0.31 |     3.44 | +0.24 (1.8)      | +0.37 (4.0)  | +0.37 (2.3)  | +0.51 (2.3)  | +0.29 (3.2)     |

### 2d. Does opponent adjustment help?

| factor                        |   raw (per-game mean) |   t_raw |   opponent-adjusted |   t_adj |   corr(raw, adj) |   both in: raw |     t |   both in: adj |    t  |
|:------------------------------|----------------------:|--------:|--------------------:|--------:|-----------------:|---------------:|------:|---------------:|------:|
| opp_ftr (FT rate allowed)     |                 -0.43 |   -5.40 |               -0.40 |   -5.21 |             0.97 |          -0.70 | -1.48 |           0.26 |  0.58 |
| opp_3p_pct (3P% allowed)      |                 -0.35 |   -4.38 |               -0.35 |   -4.46 |             0.99 |           0.42 |  0.54 |          -0.76 | -0.99 |
| opp_stl (steal rate)          |                 -0.25 |   -3.10 |               -0.26 |   -3.17 |             0.99 |           0.47 |  0.58 |          -0.74 | -0.88 |
| opp_foul (fouls per poss)     |                 -0.36 |   -4.42 |               -0.33 |   -4.22 |             0.98 |          -0.65 | -1.33 |           0.29 |  0.61 |
| shot_ftr (own FT rate)        |                 -0.31 |   -3.91 |               -0.31 |   -4.04 |             0.94 |          -0.01 | -0.04 |          -0.29 | -1.01 |
| shot_orb (own off. reb. rate) |                 -0.23 |   -2.87 |               -0.21 |   -2.72 |             0.99 |          -0.75 | -1.35 |           0.52 |  0.95 |

### 2e. After the vig: the eight factors alone as a walk-forward model

| model          |   threshold | line   |   bets |   win% |   ci_lo |   ci_hi |   ROI% |   ROI_lo |   ROI_hi | seasons>BE   |
|:---------------|------------:|:-------|-------:|-------:|--------:|--------:|-------:|---------:|---------:|:-------------|
| 8 factors      |        0.50 | close  |  21843 |  52.22 |   51.56 |   52.88 |  -0.30 |    -1.55 |     0.96 | 3/8          |
| all 33 factors |        0.50 | close  |  25788 |  52.12 |   51.51 |   52.73 |  -0.49 |    -1.65 |     0.66 | 4/8          |
| 8 factors      |        0.50 | open   |  16030 |  52.72 |   51.95 |   53.49 |   0.64 |    -0.82 |     2.11 | 4/6          |
| 8 factors      |        1.00 | close  |   9456 |  53.37 |   52.37 |   54.38 |   1.88 |    -0.02 |     3.79 | 5/8          |
| all 33 factors |        1.00 | close  |  14917 |  52.69 |   51.89 |   53.49 |   0.59 |    -0.93 |     2.11 | 5/8          |
| 8 factors      |        1.00 | open   |   7106 |  53.39 |   52.23 |   54.55 |   1.92 |    -0.28 |     4.12 | 6/6          |
| 8 factors      |        1.50 | close  |   3094 |  54.72 |   52.96 |   56.47 |   4.42 |     1.10 |     7.74 | 7/8          |
| all 33 factors |        1.50 | close  |   7265 |  53.74 |   52.59 |   54.88 |   2.57 |     0.40 |     4.74 | 7/8          |
| 8 factors      |        1.50 | open   |   2436 |  55.09 |   53.11 |   57.06 |   5.14 |     1.39 |     8.90 | 6/6          |

Signal sd: 8 factors 0.84, 33 factors 1.12; correlation between them 0.67.

## 3. Descriptive tables behind the new hypotheses

### 3a. Named neutral-site venues (all seasons; raw means, NOT out-of-sample)

| venue                             |   games |   seasons |   mean_vs_close |      t |   over_pct |   shrunk_effect |   mean_vs_torvik |   poss40_vs_torvik |   ppp_vs_torvik_x100 |
|:----------------------------------|--------:|----------:|----------------:|-------:|-----------:|----------------:|-----------------:|-------------------:|---------------------:|
| Orleans Arena                     |     238 |        11 |            2.63 |   2.35 |      54.43 |            2.25 |             1.89 |              -1.09 |                 2.25 |
| Barclays Center                   |     198 |         9 |           -0.49 |  -0.43 |      44.16 |           -0.41 |            -1.64 |              -1.19 |                -0.71 |
| Madison Square Garden             |     186 |        11 |           -0.35 |  -0.28 |      46.45 |           -0.29 |            -1.63 |              -0.90 |                -0.90 |
| T-Mobile Center                   |     159 |        11 |           -0.17 |  -0.14 |      51.27 |           -0.13 |            -1.06 |              -0.52 |                -0.38 |
| T-Mobile Arena                    |     140 |        10 |            1.56 |   1.03 |      51.82 |            1.22 |             0.52 |              -0.76 |                -0.10 |
| Enterprise Center                 |     129 |        11 |           -2.24 |  -1.57 |      41.41 |           -1.71 |            -4.70 |              -0.90 |                -2.94 |
| Ocean Center                      |     116 |         6 |            1.45 |   0.87 |      55.65 |            1.08 |             0.34 |              -0.63 |                -0.07 |
| Imperial Arena                    |     114 |        10 |            0.16 |   0.10 |      49.09 |            0.12 |            -0.75 |              -2.24 |                 0.96 |
| Stan Sheriff Center               |     107 |        10 |            1.49 |   0.89 |      51.43 |            1.09 |             2.20 |               0.04 |                 0.71 |
| Mohegan Sun Arena                 |     103 |        11 |            0.94 |   0.59 |      50.50 |            0.68 |             1.38 |              -1.09 |                 2.20 |
| Thomas & Mack Center              |     102 |        11 |           -1.88 |  -1.12 |      41.00 |           -1.35 |            -3.45 |              -0.39 |                -2.48 |
| Gainbridge Fieldhouse             |     101 |        11 |            4.48 |   2.61 |      53.47 |            3.21 |             3.48 |               0.14 |                 1.11 |
| Capital One Arena                 |      83 |         8 |            3.29 |   1.79 |      62.65 |            2.22 |             1.90 |              -1.18 |                 2.44 |
| Lahaina Civic Center              |      78 |         8 |            3.05 |   1.49 |      51.28 |            2.02 |             4.64 |              -1.69 |                 4.96 |
| United Center                     |      72 |         9 |           -1.12 |  -0.75 |      42.25 |           -0.72 |            -2.30 |              -0.21 |                -2.04 |
| The HTC Center                    |      69 |         7 |            2.43 |   1.12 |      59.42 |            1.54 |             2.20 |              -1.10 |                 2.69 |
| MGM Grand Garden Arena            |      68 |         7 |            4.88 |   3.18 |      69.12 |            3.07 |             6.38 |               0.71 |                 1.90 |
| Baha Mar Convention Center        |      68 |         6 |            3.56 |   1.42 |      47.06 |            2.24 |             2.45 |              -0.42 |                -0.06 |
| Michelob ULTRA Arena              |      55 |         6 |            1.98 |   0.91 |      50.91 |            1.15 |             2.39 |               0.51 |                 0.68 |
| State Farm Field House            |      41 |         3 |            3.39 |   1.28 |      60.00 |            1.72 |             3.47 |              -0.42 |                 2.88 |
| ESPN Wide World of Sports Complex |      14 |         2 |          -11.36 |  -4.24 |       7.14 |           -2.94 |           -12.12 |              -3.57 |                -4.66 |
| MGM Grand                         |       2 |         1 |            5.25 |   0.25 |      50.00 |            0.25 |             7.99 |               0.42 |                 3.84 |
| Mohegan Sun Arena Wilkes-Barre    |       1 |         1 |           -4.50 | nan    |       0.00 |           -0.11 |            -4.90 |              -4.52 |                 3.40 |

All neutral venues with >=40 lined games: 49. Venues with |t| >= 2: 8 (expected by chance: 2.2). Spread of venue means: observed sd 2.71 pts vs 1.89 expected from noise alone.

Feast Week neutral-site games by season:

|   season |   games |   mean_vs_close |   over_pct |   mean_vs_open |   mean_vs_torvik |
|---------:|--------:|----------------:|-----------:|---------------:|-----------------:|
|     2016 |  158.00 |           -1.62 |      46.84 |          -1.08 |            -1.33 |
|     2017 |  182.00 |           -2.08 |      42.78 |          -3.31 |            -3.04 |
|     2018 |  198.00 |           -0.26 |      44.90 |          -1.43 |            -1.49 |
|     2019 |  194.00 |            0.09 |      47.15 |          -0.54 |            -2.09 |
|     2020 |  201.00 |           -0.05 |      47.21 |          -0.68 |            -1.66 |
|     2021 |   87.00 |            0.02 |      44.19 |           0.88 |            -1.12 |
|     2022 |  232.00 |            1.23 |      49.34 |         nan    |             1.43 |
|     2023 |  271.00 |            0.27 |      48.52 |         nan    |             0.46 |
|     2024 |  225.00 |            1.56 |      52.02 |           0.73 |             1.52 |
|     2025 |  236.00 |            0.53 |      49.15 |           0.33 |             0.57 |
|     2026 |  224.00 |           -1.43 |      46.15 |          -2.19 |            -1.90 |

Feast Week overall: 2,189 games, overs 47.5% (95% CI 45.4-49.6), mean vs close -0.07.

### 3b. Spread size, overtime and second-half scoring

| mkt_spread_abs   |    games |   OT% |   mean vs close |   median vs close |   over% |   over% regulation only |   2H minus 1H pts |
|:-----------------|---------:|------:|----------------:|------------------:|--------:|------------------------:|------------------:|
| 0-2.5            | 10218.00 |  8.00 |            0.71 |             -0.50 |   49.53 |                   46.56 |              8.10 |
| 3-5.5            | 13175.00 |  7.50 |            0.97 |              0.50 |   50.58 |                   47.69 |              8.03 |
| 6-9.5            | 12363.00 |  6.15 |            0.47 |             -0.50 |   49.45 |                   47.03 |              8.03 |
| 10-14.5          |  7828.00 |  3.56 |            0.87 |              0.50 |   50.68 |                   49.39 |              7.67 |
| 15+              |  6593.00 |  1.70 |            0.49 |              0.50 |   50.80 |                   50.26 |              6.55 |

### 3c. Who controls pace?

Actual per-40 possessions on the two teams' pregame adjusted tempos (deviations from average): slower team 0.882 (se 0.009), faster team 0.801 (se 0.009); difference t = 5.4. Equal weights mean neither side dictates; an additive model predicts ~1.0 each.

By tempo gap between the two teams:

|     |    games |   poss40_vs_torvik |   total_vs_torvik |   total_vs_close |   over_pct |
|:----|---------:|-------------------:|------------------:|-----------------:|-----------:|
| 0-2 | 21643.00 |              -0.51 |              0.74 |             0.77 |      50.15 |
| 2-4 | 15632.00 |              -0.47 |              0.79 |             0.79 |      50.00 |
| 4-6 |  8320.00 |              -0.51 |              0.81 |             0.74 |      50.33 |
| 6+  |  5281.00 |              -0.74 |              0.44 |             0.36 |      50.35 |

### 3d. Early season: how good is the market before teams have played?

|       |    games |   close_MAE |   torvik_MAE |   mean vs close |   over% |   open_MAE (where open exists) |   mean|move| |
|:------|---------:|------------:|-------------:|----------------:|--------:|-------------------------------:|-------------:|
| 0     |  1349.00 |       14.17 |        14.61 |            1.74 |   51.84 |                          14.58 |         2.62 |
| 1-2   |  3209.00 |       13.47 |        13.93 |           -0.41 |   47.60 |                          13.66 |         2.37 |
| 3-5   |  4939.00 |       13.48 |        13.77 |            0.11 |   49.25 |                          13.60 |         1.96 |
| 6-10  |  7833.00 |       13.26 |        13.56 |            0.69 |   49.88 |                          13.50 |         1.77 |
| 11-20 | 15942.00 |       13.31 |        13.67 |            0.73 |   50.34 |                          13.52 |         1.73 |
| 21+   | 17606.00 |       13.32 |        13.66 |            1.04 |   50.70 |                          13.53 |         1.71 |

First five games, by season (is the early-season under still there?):

|   season |   games |   mean_vs_close |   over_pct |
|---------:|--------:|----------------:|-----------:|
|     2016 |  451.00 |           -0.69 |      48.00 |
|     2017 |  492.00 |           -1.51 |      43.74 |
|     2018 |  502.00 |            0.23 |      49.00 |
|     2019 |  793.00 |           -0.39 |      49.23 |
|     2020 |  814.00 |           -0.28 |      46.82 |
|     2021 |  883.00 |            0.67 |      50.23 |
|     2022 |  784.00 |           -0.18 |      46.54 |
|     2023 |  788.00 |            0.52 |      49.23 |
|     2024 |  805.00 |            1.29 |      51.63 |
|     2025 |  785.00 |           -0.30 |      49.68 |
|     2026 |  817.00 |            1.09 |      50.55 |

## 4. New hypotheses: discovery (2016-22) then validation (2023-26)

53 tests, each run once. Slopes are points of (actual - close) per +1 SD (or for a 0/1 flag), season fixed effects, date-clustered. `open` and `move` columns use all seasons with an opener and are descriptive.

| family                           | hypothesis                                                                               | unit   |   disc_n |   disc_slope |   disc_t |   disc_q |   valid_n |   valid_slope |   valid_t | replicates   |   open_slope |   open_t |   move_slope |   move_t |
|:---------------------------------|:-----------------------------------------------------------------------------------------|:-------|---------:|-------------:|---------:|---------:|----------:|--------------:|----------:|:-------------|-------------:|---------:|-------------:|---------:|
| B. last-game outliers            | last game 3P% minus own prior average (hot shooting last time out)                       | per SD |    27994 |        -0.05 |    -0.46 |     0.76 |     19963 |         -0.11 |     -0.99 |              |        -0.10 |    -1.21 |        -0.02 |    -1.48 |
| B. last-game outliers            | last game OPPONENT 3P% minus prior average allowed                                       | per SD |    27994 |         0.17 |     1.75 |     0.16 |     19963 |         -0.07 |     -0.54 |              |         0.09 |     1.05 |         0.01 |     0.55 |
| B. last-game outliers            | last 3 games 3P% minus season-to-date                                                    | per SD |    27015 |        -0.01 |    -0.06 |     0.97 |     19304 |          0.01 |      0.11 |              |         0.01 |     0.11 |        -0.04 |    -3.52 |
| B. last-game outliers            | last game eFG% minus prior average                                                       | per SD |    27994 |         0.01 |     0.15 |     0.92 |     19963 |         -0.09 |     -0.76 |              |        -0.06 |    -0.66 |         0.01 |     0.57 |
| B. last-game outliers            | last game FT% minus prior average                                                        | per SD |    27983 |        -0.08 |    -0.81 |     0.57 |     19961 |         -0.10 |     -0.77 |              |        -0.10 |    -1.10 |         0.02 |     1.59 |
| B. last-game outliers            | last game turnover rate minus prior average                                              | per SD |    27994 |        -0.20 |    -1.98 |     0.11 |     19963 |         -0.25 |     -2.26 |              |        -0.27 |    -3.08 |        -0.06 |    -4.67 |
| B. last-game outliers            | last game pace minus prior average                                                       | per SD |    27994 |         0.49 |     4.74 |     0.00 |     19963 |          0.37 |      3.00 | YES          |         0.65 |     7.32 |         0.19 |    13.66 |
| B. last-game outliers            | last game total fouls minus prior average                                                | per SD |    27994 |        -0.00 |    -0.03 |     0.97 |     19963 |          0.23 |      1.90 |              |         0.14 |     1.65 |         0.06 |     4.84 |
| B. last-game outliers            | either team's last game went to overtime                                                 | 0/1    |    28928 |        -0.33 |    -1.06 |     0.45 |     20601 |          0.48 |      1.35 |              |         0.05 |     0.19 |         0.06 |     1.47 |
| B. last-game outliers            | teams' previous game vs its closing total (sum of both teams' last market miss)          | per SD |    28068 |         0.27 |     2.70 |     0.03 |     20242 |          0.33 |      2.82 | YES          |         0.30 |     3.36 |         0.03 |     2.05 |
| B. last-game outliers            | extreme last game: either team's last game >= 25 pts off its close                       | 0/1    |    28068 |         0.40 |     1.96 |     0.11 |     20242 |          0.10 |      0.43 |              |         0.12 |     0.68 |         0.03 |     0.97 |
| F. team-level market persistence | teams' season-to-date average miss vs the close (shrunk)                                 | per SD |    28068 |        -0.33 |    -3.15 |     0.02 |     20242 |          0.02 |      0.17 |              |        -0.64 |    -7.05 |        -0.44 |   -21.25 |
| F. team-level market persistence | teams' PRIOR-season average miss vs the close (shrunk)                                   | per SD |    25683 |         0.25 |     2.53 |     0.05 |     20902 |          0.18 |      1.65 |              |         0.26 |     3.08 |        -0.02 |    -1.17 |
| F. team-level market persistence | coaches' career-to-date (prior seasons) average miss vs the close (shrunk)               | per SD |    29736 |         0.38 |     3.96 |     0.00 |     21142 |          0.25 |      2.04 | YES          |         0.42 |     4.85 |         0.06 |     5.14 |
| A. venue & schedule              | neutral-site venue's prior-seasons average miss vs close (shrunk, >=10 prior games)      | per SD |     1923 |         1.05 |     2.35 |     0.06 |      2156 |          0.54 |      1.66 |              |         1.02 |     3.19 |         0.15 |     3.02 |
| A. venue & schedule              | home gym: home team's prior-season home-game average miss vs close (shrunk)              | per SD |    22091 |         0.51 |     4.53 |     0.00 |     18280 |          0.67 |      5.04 | YES          |         0.62 |     6.23 |        -0.01 |    -0.83 |
| A. venue & schedule              | Feast Week neutral-site game (Nov 18-30)                                                 | 0/1    |    29736 |        -1.00 |    -2.00 |     0.11 |     21142 |         -0.70 |     -1.18 |              |        -1.82 |    -4.12 |        -0.78 |    -8.91 |
| A. venue & schedule              | any neutral-site game                                                                    | 0/1    |    29736 |        -0.76 |    -2.41 |     0.06 |     21142 |         -0.76 |     -2.16 | YES          |        -1.42 |    -5.19 |        -0.77 |   -14.55 |
| A. venue & schedule              | conference tournament game                                                               | 0/1    |    29736 |        -0.24 |    -0.51 |     0.74 |     21142 |         -0.86 |     -1.85 |              |        -1.18 |    -2.92 |        -0.95 |   -10.66 |
| A. venue & schedule              | postseason (NCAA/NIT/other) game                                                         | 0/1    |    29736 |        -0.15 |    -0.27 |     0.85 |     21142 |         -0.61 |     -0.62 |              |         0.81 |     1.42 |         0.77 |     4.56 |
| A. venue & schedule              | either team played yesterday                                                             | 0/1    |    28928 |        -1.06 |    -2.82 |     0.03 |     20601 |         -0.30 |     -0.66 |              |        -1.56 |    -4.66 |        -0.80 |   -12.14 |
| A. venue & schedule              | both teams played yesterday (tournament day 2+)                                          | 0/1    |    28928 |        -1.20 |    -2.92 |     0.03 |     20601 |          0.30 |      0.53 |              |        -1.63 |    -4.38 |        -0.84 |   -11.03 |
| A. venue & schedule              | long rest: both teams 7+ days off                                                        | 0/1    |    28928 |         1.01 |     2.06 |     0.10 |     20601 |          0.07 |      0.13 |              |         0.79 |     2.11 |         0.02 |     0.32 |
| A. venue & schedule              | home game at altitude (>4,000 ft home team)                                              | 0/1    |    29736 |         1.40 |     2.85 |     0.03 |     21142 |          2.02 |      3.48 | YES          |         2.02 |     4.75 |         0.12 |     1.98 |
| A. venue & schedule              | altitude home team hosting a non-altitude visitor                                        | 0/1    |    29736 |         1.31 |     2.31 |     0.07 |     21142 |          1.50 |      2.34 | YES          |         2.05 |     4.27 |         0.23 |     3.31 |
| C. pace control                  | tempo gap x slower team's defence forces few turnovers (slow team controls)              | per SD |    29736 |         0.19 |     1.93 |     0.11 |     21142 |          0.21 |      1.63 |              |         0.14 |     1.55 |        -0.01 |    -0.40 |
| C. pace control                  | faster team's offensive rebound rate x tempo gap                                         | per SD |    29736 |        -0.21 |    -1.97 |     0.11 |     21142 |         -0.15 |     -1.20 |              |        -0.15 |    -1.60 |        -0.01 |    -0.77 |
| C. pace control                  | raw pace to date minus Torvik adjusted tempo (both teams)                                | per SD |    29736 |         0.06 |     0.50 |     0.74 |     21142 |         -0.03 |     -0.22 |              |         0.00 |     0.01 |         0.06 |     1.78 |
| C. pace control                  | home team is the faster team (non-neutral)                                               | 0/1    |    25850 |        -0.45 |    -2.26 |     0.07 |     18362 |         -0.07 |     -0.29 |              |        -0.26 |    -1.40 |         0.03 |     1.08 |
| C. pace control                  | tempo gap >= 6 possessions                                                               | 0/1    |    29736 |        -0.47 |    -1.39 |     0.29 |     21142 |         -0.28 |     -0.72 |              |        -0.16 |    -0.54 |         0.03 |     0.63 |
| D. early season & roster         | season opener for either team (0 games played)                                           | 0/1    |    29736 |         0.27 |     0.32 |     0.83 |     21142 |          2.24 |      2.60 |              |         2.10 |     2.57 |         0.81 |     2.85 |
| D. early season & roster         | first 5 games for either team                                                            | 0/1    |    29736 |        -0.98 |    -3.42 |     0.01 |     21142 |         -0.27 |     -0.69 |              |        -0.66 |    -2.21 |        -0.03 |    -0.29 |
| D. early season & roster         | roster turnover in the first 5 games                                                     | per SD |     4719 |        -0.20 |    -0.59 |     0.72 |      3195 |         -0.01 |     -0.02 |              |         0.07 |     0.27 |        -0.07 |    -1.50 |
| D. early season & roster         | new head coach (either) in the first 10 games                                            | 0/1    |     9366 |        -0.53 |    -1.33 |     0.31 |      6415 |          0.08 |      0.18 |              |        -0.04 |    -0.12 |         0.11 |     2.03 |
| D. early season & roster         | ex-post transfer minutes share, first 10 games [uses later info]                         | per SD |     9366 |        -0.12 |    -0.33 |     0.83 |      6415 |          0.53 |      2.22 |              |         0.37 |     1.64 |         0.10 |     2.57 |
| D. early season & roster         | early opponents were weak: team rank now minus preseason-ish (rank gap of the two teams) | per SD |     7518 |        -0.17 |    -0.79 |     0.57 |      5146 |          0.16 |      0.60 |              |         0.11 |     0.54 |         0.17 |     4.90 |
| E. game state                    | market spread size (bigger favourite)                                                    | per SD |    29038 |        -0.14 |    -1.33 |     0.31 |     21139 |          0.11 |      0.97 |              |         0.08 |     0.90 |         0.11 |     6.74 |
| E. game state                    | pick'em-ish game: spread <= 3                                                            | 0/1    |    29038 |         0.20 |     0.86 |     0.57 |     21139 |         -0.31 |     -1.12 |              |        -0.13 |    -0.63 |        -0.12 |    -4.08 |
| E. game state                    | blowout expected: spread >= 15                                                           | 0/1    |    29038 |        -0.68 |    -2.24 |     0.07 |     21139 |          0.31 |      0.87 |              |         0.02 |     0.06 |         0.27 |     5.50 |
| E. game state                    | close spread x both teams' FT rate (late fouling pays)                                   | per SD |    29038 |        -0.16 |    -1.52 |     0.23 |     21139 |         -0.13 |     -1.06 |              |        -0.23 |    -2.52 |        -0.10 |    -7.90 |
| E. game state                    | close spread x both teams' FT% (late fouling pays)                                       | per SD |    29038 |         0.20 |     2.09 |     0.10 |     21139 |          0.12 |      0.99 |              |         0.03 |     0.41 |        -0.13 |   -10.18 |
| E. game state                    | teams' season-to-date overtime rate                                                      | per SD |    28928 |         0.08 |     0.83 |     0.57 |     20601 |          0.21 |      1.52 |              |         0.24 |     2.44 |         0.06 |     3.90 |
| F. other market profiles         | closing total level                                                                      | per SD |    29736 |        -0.05 |    -0.51 |     0.74 |     21142 |          0.10 |      0.78 |              |         0.18 |     2.01 |         0.20 |     7.45 |
| F. other market profiles         | very high total (close >= 160)                                                           | 0/1    |    29736 |        -0.45 |    -0.90 |     0.56 |     21142 |          0.26 |      0.46 |              |         0.48 |     1.23 |         0.68 |     7.98 |
| F. other market profiles         | very low total (close <= 125)                                                            | 0/1    |    29736 |         0.42 |     0.79 |     0.57 |     21142 |         -1.19 |     -1.38 |              |         0.45 |     0.78 |         0.38 |     3.32 |
| F. other market profiles         | both teams from major conferences                                                        | 0/1    |    29736 |        -0.06 |    -0.22 |     0.87 |     21142 |          0.28 |      0.92 |              |        -0.05 |    -0.22 |        -0.11 |    -3.07 |
| F. other market profiles         | neither team from a major conference                                                     | 0/1    |    29736 |         0.51 |     2.44 |     0.06 |     21142 |         -0.01 |     -0.03 |              |         0.21 |     1.11 |        -0.01 |    -0.20 |
| F. other market profiles         | weekend game (Sat/Sun)                                                                   | 0/1    |    29736 |         0.58 |     2.86 |     0.03 |     21142 |          0.30 |      1.27 |              |         0.49 |     2.79 |        -0.02 |    -0.39 |
| F. other market profiles         | combined team quality (sum of Torvik barthag)                                            | per SD |    29736 |        -0.19 |    -1.74 |     0.16 |     21142 |          0.07 |      0.64 |              |        -0.02 |    -0.24 |         0.03 |     2.17 |
| F. other market profiles         | defence-heavy matchup: both adj. defences better than both adj. offences are good        | per SD |    29736 |         0.36 |     2.79 |     0.03 |     21142 |          0.10 |      0.60 |              |         1.02 |     8.58 |         0.69 |    24.14 |
| F. other market profiles         | books disagree: range of totals across books (2+ books)                                  | per SD |    27466 |         0.20 |     1.27 |     0.33 |     10500 |         -0.13 |     -0.55 |              |         0.25 |     1.60 |        -0.02 |    -1.02 |
| F. other market profiles         | 3-point volume: both offences' 3PA rate x both defences' 3PA allowed                     | per SD |    29736 |         0.05 |     0.41 |     0.78 |     21142 |          0.24 |      2.05 |              |         0.25 |     2.62 |         0.10 |     7.14 |
| F. other market profiles         | second half of conference season (Feb on), conference games                              | 0/1    |    29736 |         0.52 |     2.36 |     0.06 |     21142 |          0.60 |      2.27 | YES          |         0.47 |     2.44 |         0.15 |     4.09 |

Discovery q<0.10: 21/53. Replicated in validation: 8.

## 5. Follow-ups on what replicated

### 5a. Home-gym effect: is it the building or the team?

| sample                              |     n | home team: last season's HOME games   | home team: last season's ROAD games   | road team: last season's ROAD games   | road team: last season's HOME games   |
|:------------------------------------|------:|:--------------------------------------|:--------------------------------------|:--------------------------------------|:--------------------------------------|
| all seasons                         | 39300 | +0.58 (6.4)                           | -0.01 (-0.2)                          | +0.28 (3.2)                           | -0.19 (-2.3)                          |
| discovery 2016-22                   | 21162 | +0.49 (4.1)                           | +0.02 (0.1)                           | +0.37 (3.2)                           | -0.20 (-1.8)                          |
| validation 2023-26                  | 18138 | +0.69 (5.0)                           | -0.06 (-0.4)                          | +0.17 (1.3)                           | -0.17 (-1.3)                          |
| validation, altitude homes excluded | 17269 | +0.75 (5.3)                           | -0.03 (-0.2)                          | +0.16 (1.2)                           | -0.19 (-1.5)                          |

Each cell: points of (actual - close) per +1 SD, t in brackets, all four in one regression. If the building mattered, only the first column would carry weight; if it is the team's style, the home team's road games would predict too.

Betting the home-gym prior alone (over if the home team's prior-season home games ran over the close by the threshold, under if under):

| sample             | line   |   threshold (pts, set on discovery) |   bets |   win% |   ci_lo |   ci_hi |   ROI% |   ROI_lo |   ROI_hi | seasons>BE   |
|:-------------------|:-------|------------------------------------:|-------:|-------:|--------:|--------:|-------:|---------:|---------:|:-------------|
| discovery 2016-22  | close  |                                2.91 |   4386 |  51.69 |   50.21 |   53.16 |  -1.31 |    -4.10 |     1.48 | 3/6          |
| discovery 2016-22  | open   |                                2.91 |   3548 |  53.69 |   52.05 |   55.33 |   2.47 |    -0.62 |     5.55 | 4/5          |
| validation 2023-26 | close  |                                2.91 |   3218 |  53.33 |   51.60 |   55.04 |   1.79 |    -1.48 |     5.07 | 4/4          |
| validation 2023-26 | open   |                                2.91 |   2406 |  53.03 |   51.04 |   55.02 |   1.24 |    -2.55 |     5.03 | 2/3          |

### 5b. Altitude

|   season |   games |   mean_vs_close |   over_pct |   mean_vs_open |
|---------:|--------:|----------------:|-----------:|---------------:|
|     2016 |  185.00 |            1.72 |      54.35 |           1.94 |
|     2017 |  185.00 |            1.77 |      50.00 |           1.79 |
|     2018 |  185.00 |            4.14 |      55.98 |           4.42 |
|     2019 |  207.00 |            0.44 |      49.51 |           1.19 |
|     2020 |  202.00 |            2.67 |      58.21 |           2.86 |
|     2021 |  148.00 |            2.83 |      57.53 |           2.58 |
|     2022 |  206.00 |            0.61 |      52.71 |         nan    |
|     2023 |  216.00 |            2.75 |      57.41 |         nan    |
|     2024 |  208.00 |            3.92 |      58.45 |           4.04 |
|     2025 |  220.00 |            1.23 |      54.55 |           1.66 |
|     2026 |  230.00 |            3.37 |      59.57 |           3.69 |

All altitude home games: overs 1206/2179 = 55.3% (95% CI 53.3-57.4). Validation seasons only: 502/873 = 57.5% (CI 54.2-60.7). The list of 17 schools was fixed before looking at results.

| team2             |   games |   mean_vs_close |   over_pct |
|:------------------|--------:|----------------:|-----------:|
| Denver            |  112.00 |            4.05 |      60.36 |
| Wyoming           |  147.00 |            3.93 |      59.86 |
| Northern Colorado |  110.00 |            3.50 |      58.18 |
| Colorado St.      |  149.00 |            3.38 |      56.76 |
| Idaho St.         |   98.00 |            3.35 |      54.08 |
| Air Force         |  145.00 |            3.12 |      58.62 |
| Northern Arizona  |  106.00 |            2.65 |      58.10 |
| Utah Valley       |   82.00 |            2.38 |      57.32 |
| Utah              |  158.00 |            2.29 |      52.56 |
| Weber St.         |  109.00 |            2.23 |      55.56 |
| Southern Utah     |  106.00 |            2.19 |      53.77 |
| Montana St.       |  118.00 |            2.15 |      57.26 |
| New Mexico        |  141.00 |            1.84 |      54.29 |
| Utah St.          |  141.00 |            1.71 |      54.61 |
| Colorado          |  166.00 |            0.83 |      50.62 |
| Nevada            |  153.00 |            0.82 |      51.63 |
| BYU               |  151.00 |            0.08 |      51.33 |

### 5c. Experimental model: 33 factors plus the new features that passed DISCOVERY only

Selected using seasons through 2021-22 only (20 features): last game pace minus prior average; teams' season-to-date average miss vs the close (shrunk); teams' PRIOR-season average miss vs the close (shrunk); coaches' career-to-date (prior seasons) average miss vs the close (shrunk); neutral-site venue's prior-seasons average miss vs close (shrunk, >=10 prior games); home gym: home team's prior-season home-game average miss vs close (shrunk); any neutral-site game; either team played yesterday; both teams played yesterday (tournament day 2+); long rest: both teams 7+ days off; home game at altitude (>4,000 ft home team); altitude home team hosting a non-altitude visitor; home team is the faster team (non-neutral); first 5 games for either team; blowout expected: spread >= 15; close spread x both teams' FT% (late fouling pays); neither team from a major conference; weekend game (Sat/Sun); defence-heavy matchup: both adj. defences better than both adj. offences are good; second half of conference season (Feb on), conference games.

| model                    | test seasons   |     n |   OOS R2% |    t |   corr |   close bets@1.0 |   win%@1.0 | CI@1.0    | seasons>BE@1.0   |   close bets@1.5 |   win%@1.5 | CI@1.5    | seasons>BE@1.5   |   open bets@1.5 (2024-26) |   open win%@1.5 | open CI   |
|:-------------------------|:---------------|------:|----------:|-----:|-------:|-----------------:|-----------:|:----------|:-----------------|-----------------:|-----------:|:----------|:-----------------|--------------------------:|----------------:|:----------|
| 33 factors (phase-1 set) | 2023-26        | 20902 |      0.13 | 1.51 |   0.04 |             7541 |      52.47 | 51.3-53.6 | 2/4              |             3503 |      53.95 | 52.3-55.6 | 4/4              |                      2756 |           54.97 | 53.1-56.8 |
| 33 + new                 | 2023-26        | 20902 |      0.29 | 2.40 |   0.06 |            10157 |      53.39 | 52.4-54.4 | 3/4              |             6218 |      54.31 | 53.1-55.5 | 4/4              |                      4757 |           55.64 | 54.2-57.1 |
| new only                 | 2023-26        | 21142 |      0.16 | 1.85 |   0.05 |             6526 |      53.08 | 51.9-54.3 | 2/4              |             2779 |      53.80 | 51.9-55.6 | 4/4              |                      2155 |           55.41 | 53.3-57.5 |

This is a clean test of the ADDED features: they were chosen without seeing 2023-26. It is not a clean test of any threshold.

