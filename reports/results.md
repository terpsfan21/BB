# Torvik totals: generated results

Games: 59,673 D1-vs-D1, seasons 2016-2026 (frozen pregame total + stored pregame possessions). With a closing total: 50,878.

## 1. Baseline accuracy

|      |     games |   torvik_bias |   close_bias |   torvik_MAE |   close_MAE |   retro_MAE(leaky) |   corr(torvik,close) |   sd(torvik-close) |
|:-----|----------:|--------------:|-------------:|-------------:|------------:|-------------------:|---------------------:|-------------------:|
| 2016 |  3623.000 |         0.879 |        0.634 |       13.845 |      13.679 |             12.717 |                0.957 |              3.258 |
| 2017 |  3710.000 |         0.409 |        0.651 |       13.673 |      13.385 |             12.601 |                0.955 |              3.619 |
| 2018 |  3779.000 |         0.486 |        1.055 |       14.015 |      13.698 |             13.063 |                0.951 |              3.718 |
| 2019 |  5110.000 |        -0.965 |        0.027 |       14.031 |      13.624 |             12.905 |                0.945 |              3.895 |
| 2020 |  4893.000 |         0.902 |        0.736 |       13.730 |      13.397 |             12.400 |                0.944 |              3.856 |
| 2021 |  3696.000 |         0.827 |        0.570 |       13.590 |      13.246 |             12.419 |                0.935 |              3.532 |
| 2022 |  4925.000 |         0.817 |        0.749 |       13.541 |      13.190 |             12.379 |                0.937 |              3.708 |
| 2023 |  5267.000 |         1.315 |        1.359 |       13.510 |      13.167 |             12.383 |                0.938 |              3.827 |
| 2024 |  5262.000 |         1.258 |        0.950 |       13.602 |      13.229 |             12.626 |                0.934 |              3.618 |
| 2025 |  5282.000 |         1.050 |        0.683 |       13.211 |      12.866 |             12.179 |                0.937 |              3.679 |
| 2026 |  5331.000 |         0.991 |        0.551 |       14.042 |      13.597 |             12.855 |                0.928 |              4.216 |
| ALL  | 50878.000 |         0.737 |        0.726 |       13.700 |      13.355 |             12.583 |                0.944 |              3.774 |

Error decomposition (all games): actual minus Torvik.

|                       |   mean |     sd |    MAE |
|:----------------------|-------:|-------:|-------:|
| total (pts)           |  0.688 | 17.166 | 13.518 |
| possessions incl. OT  |  0.036 |  4.944 |  3.771 |
| possessions per 40    | -0.567 |  4.325 |  3.457 |
| points per possession |  0.005 |  0.105 |  0.083 |

Variance of total error: pace part 105 pts^2 (36%), efficiency part 209 pts^2 (71%), covariance x2 -20.

Calibration slope of the closing total: 0.998.

Calibration slope, actual total on Torvik total: 0.802 (1.0 = perfect); actual per-40 possessions on projected: 0.826. OT games: 6.0%.

## 2. In-sample factor screen (season fixed effects, SEs clustered by date)

Slope = change in error per +1 SD of the factor. `sign` = seasons whose own slope has the pooled sign. q = Benjamini-Hochberg across all tests in this table.

| factor                   | family         |   total_slope |   total_t | total_sign   |   poss40_slope |   poss40_t | poss40_sign   |   ppp_x100_slope |   ppp_x100_t | ppp_x100_sign   |
|:-------------------------|:---------------|--------------:|----------:|:-------------|---------------:|-----------:|:--------------|-----------------:|-------------:|:----------------|
| pace_absdiff             | pace_mismatch  |         -0.11 |     -1.47 | 7/11         |          -0.06 |      -2.89 | 7/11          |            -0.01 |        -0.32 | 6/11            |
| pace_sum                 | pace_mismatch  |         -0.91 |    -12.35 | 11/11        |          -0.55 |     -27.77 | 11/11         |             0.12 |         2.81 | 10/11           |
| pace_inter               | pace_mismatch  |          0.13 |      1.76 | 6/11         |           0.03 |       1.63 | 9/11          |             0.05 |         1.02 | 9/11            |
| pace_fast_slow           | pace_mismatch  |         -0.80 |    -10.49 | 10/11        |          -0.47 |     -23.23 | 11/11         |             0.09 |         2.07 | 6/11            |
| pace_slow_side           | pace_mismatch  |         -0.75 |    -10.49 | 11/11        |          -0.46 |     -23.99 | 11/11         |             0.11 |         2.66 | 9/11            |
| roster_turnover          | roster_change  |          0.17 |      1.87 | 7/11         |          -0.01 |      -0.71 | 4/11          |             0.15 |         2.66 | 11/11           |
| roster_turnover_max      | roster_change  |          0.19 |      2.27 | 9/11         |          -0.02 |      -0.92 | 4/11          |             0.17 |         3.30 | 9/11            |
| roster_new_coach         | roster_change  |         -0.08 |     -1.07 | 7/11         |          -0.07 |      -3.96 | 9/11          |             0.06 |         1.34 | 8/11            |
| roster_early             | roster_change  |         -0.50 |     -5.26 | 10/11        |          -0.03 |      -0.72 | 7/11          |            -0.24 |        -3.54 | 7/11            |
| roster_turnover_x_early  | roster_change  |          0.19 |      2.18 | 7/11         |          -0.03 |      -1.13 | 6/11          |             0.18 |         3.42 | 6/11            |
| roster_new_coach_x_early | roster_change  |         -0.25 |     -2.98 | 9/11         |          -0.04 |      -1.65 | 8/11          |            -0.06 |        -1.29 | 7/11            |
| shot_3par                | shot_profile   |          0.13 |      1.81 | 8/11         |           0.00 |       0.15 | 7/11          |             0.07 |         1.60 | 7/11            |
| shot_ftr                 | shot_profile   |         -0.65 |     -8.45 | 11/11        |          -0.19 |      -9.19 | 11/11         |            -0.20 |        -4.19 | 9/11            |
| shot_orb                 | shot_profile   |         -0.21 |     -2.82 | 9/11         |           0.02 |       1.24 | 8/11          |            -0.15 |        -3.42 | 9/11            |
| shot_tov                 | shot_profile   |          0.32 |      4.14 | 10/11        |          -0.14 |      -7.15 | 11/11         |             0.46 |         9.86 | 11/11           |
| shot_ast                 | shot_profile   |         -0.03 |     -0.44 | 6/11         |          -0.04 |      -2.22 | 9/11          |             0.07 |         1.67 | 9/11            |
| shot_3p_pct              | shot_profile   |         -0.99 |    -13.54 | 11/11        |           0.04 |       2.03 | 9/11          |            -0.76 |       -16.90 | 11/11           |
| shot_2p_pct              | shot_profile   |         -0.73 |     -9.55 | 11/11        |          -0.05 |      -2.58 | 10/11         |            -0.44 |        -9.26 | 11/11           |
| shot_ft_pct              | shot_profile   |         -0.41 |     -5.91 | 9/11         |          -0.01 |      -0.63 | 8/11          |            -0.28 |        -6.61 | 11/11           |
| shot_3par_absdiff        | shot_profile   |          0.09 |      1.21 | 8/11         |          -0.02 |      -1.19 | 6/11          |             0.10 |         2.07 | 9/11            |
| opp_3par                 | opponent_style |          0.04 |      0.47 | 5/11         |           0.06 |       3.27 | 8/11          |            -0.05 |        -1.09 | 8/11            |
| opp_3p_pct               | opponent_style |         -1.34 |    -17.70 | 11/11        |           0.01 |       0.74 | 6/11          |            -1.05 |       -23.23 | 11/11           |
| opp_ftr                  | opponent_style |         -0.56 |     -7.52 | 11/11        |          -0.13 |      -6.36 | 11/11         |            -0.22 |        -4.82 | 10/11           |
| opp_tov                  | opponent_style |          0.20 |      2.69 | 9/11         |          -0.13 |      -6.42 | 11/11         |             0.36 |         7.71 | 11/11           |
| opp_orb                  | opponent_style |         -0.08 |     -1.04 | 7/11         |           0.12 |       6.81 | 11/11         |            -0.23 |        -5.38 | 11/11           |
| opp_stl                  | opponent_style |          0.02 |      0.23 | 5/11         |          -0.10 |      -5.30 | 10/11         |             0.17 |         3.72 | 10/11           |
| opp_blk                  | opponent_style |          0.02 |      0.27 | 7/11         |          -0.05 |      -2.79 | 7/11          |             0.14 |         3.22 | 10/11           |
| opp_foul                 | opponent_style |         -0.32 |     -3.98 | 11/11        |          -0.01 |      -0.37 | 5/11          |            -0.21 |        -4.15 | 10/11           |
| opp_x_3par               | opponent_style |          0.18 |      2.66 | 9/11         |           0.03 |       1.70 | 6/11          |             0.07 |         1.83 | 9/11            |
| opp_x_tov                | opponent_style |         -0.01 |     -0.19 | 6/11         |           0.04 |       2.01 | 8/11          |            -0.09 |        -2.05 | 7/11            |
| opp_x_orb                | opponent_style |          0.14 |      1.94 | 8/11         |           0.06 |       3.39 | 8/11          |             0.02 |         0.51 | 5/11            |
| opp_x_ftr                | opponent_style |         -0.02 |     -0.30 | 6/11         |           0.06 |       2.91 | 7/11          |            -0.08 |        -1.83 | 8/11            |
| opp_x_pace_press         | opponent_style |          0.02 |      0.21 | 4/11         |          -0.02 |      -0.75 | 7/11          |             0.02 |         0.37 | 6/11            |

Tests with q<0.05: total 17/33, poss40 17/33, ppp 19/33.

### Quintile view of the strongest factor in each family (mean error by factor quintile)

**pace_mismatch: `pace_sum`**

| pace_sum   |        n |   total_err |   poss40_err |   ppp_err_x100 |   close_err |
|:-----------|---------:|------------:|-------------:|---------------:|------------:|
| Q1 low     | 11935.00 |        2.03 |         0.19 |           0.36 |        0.41 |
| Q2         | 11934.00 |        0.99 |        -0.34 |           0.38 |        0.47 |
| Q3         | 11935.00 |        0.61 |        -0.56 |           0.37 |        0.68 |
| Q4         | 11934.00 |        0.36 |        -0.78 |           0.56 |        0.92 |
| Q5 high    | 11935.00 |       -0.55 |        -1.34 |           0.68 |        1.14 |

**roster_change: `roster_early`**

| roster_early   |        n |   total_err |   poss40_err |   ppp_err_x100 |   close_err |
|:---------------|---------:|------------:|-------------:|---------------:|------------:|
| Q1 low         | 11935.00 |        0.75 |        -0.51 |           0.38 |        0.99 |
| Q2             | 11934.00 |        1.38 |        -0.45 |           0.65 |        1.06 |
| Q3             | 11935.00 |        0.87 |        -0.65 |           0.68 |        0.63 |
| Q4             | 11934.00 |        0.85 |        -0.44 |           0.54 |        0.80 |
| Q5 high        | 11935.00 |       -0.41 |        -0.78 |           0.10 |        0.14 |

**shot_profile: `shot_3p_pct`**

| shot_3p_pct   |        n |   total_err |   poss40_err |   ppp_err_x100 |   close_err |
|:--------------|---------:|------------:|-------------:|---------------:|------------:|
| Q1 low        | 11935.00 |        2.15 |        -0.55 |           1.50 |        1.01 |
| Q2            | 11934.00 |        1.35 |        -0.57 |           0.93 |        0.91 |
| Q3            | 11935.00 |        0.42 |        -0.50 |           0.18 |        0.50 |
| Q4            | 11934.00 |        0.18 |        -0.53 |           0.09 |        0.63 |
| Q5 high       | 11935.00 |       -0.66 |        -0.68 |          -0.35 |        0.59 |

**opponent_style: `opp_3p_pct`**

| opp_3p_pct   |        n |   total_err |   poss40_err |   ppp_err_x100 |   close_err |
|:-------------|---------:|------------:|-------------:|---------------:|------------:|
| Q1 low       | 11935.00 |        2.61 |        -0.49 |           1.79 |        1.15 |
| Q2           | 11934.00 |        1.57 |        -0.45 |           0.98 |        1.05 |
| Q3           | 11935.00 |        0.48 |        -0.63 |           0.42 |        0.52 |
| Q4           | 11934.00 |       -0.06 |        -0.46 |          -0.19 |        0.73 |
| Q5 high      | 11935.00 |       -1.16 |        -0.80 |          -0.65 |        0.10 |

## 3. Out-of-sample: predicting Torvik's error (train seasons < S, test S = 2019..2026)

`R2_oos` is relative to a constant correction equal to the training-seasons mean error; `t` is a date-clustered paired test of squared-error improvement (t > 2 ~ significant); `seasons+` = test seasons with positive R2.

| model                     |   total_R2_oos% |   total_t |   total_corr | total_seasons+   |     n |   poss40_R2_oos% |   poss40_t |   poss40_corr | poss40_seasons+   |   ppp_x100_R2_oos% |   ppp_x100_t |   ppp_x100_corr | ppp_x100_seasons+   |
|:--------------------------|----------------:|----------:|-------------:|:-----------------|------:|-----------------:|-----------:|--------------:|:------------------|-------------------:|-------------:|----------------:|:--------------------|
| pace_mismatch (ridge)     |           0.342 |     8.303 |        0.062 | 8/8              | 43306 |            1.929 |     14.705 |         0.152 | 8/8               |              0.006 |        0.606 |           0.005 | 6/8                 |
| roster_change (ridge)     |           0.083 |     1.967 |        0.026 | 7/8              | 42660 |            0.013 |      0.385 |         0.032 | 4/8               |              0.025 |        0.466 |           0.022 | 3/8                 |
| shot_profile (ridge)      |           0.441 |     5.491 |        0.065 | 7/8              | 43306 |            0.743 |      8.913 |         0.071 | 8/8               |              0.608 |        7.371 |           0.075 | 8/8                 |
| opponent_style (ridge)    |           0.708 |     8.915 |        0.084 | 8/8              | 43306 |            0.632 |      6.309 |         0.073 | 7/8               |              0.817 |        8.484 |           0.086 | 8/8                 |
| ALL four families (ridge) |           1.415 |     9.286 |        0.118 | 8/8              | 42660 |            2.677 |     14.238 |         0.146 | 7/8               |              1.145 |        6.220 |           0.120 | 7/8                 |
| ALL four families (gbm)   |           1.497 |    11.228 |        0.121 | 8/8              | 42660 |            2.857 |     14.286 |         0.158 | 8/8               |              1.135 |        7.097 |           0.118 | 7/8                 |

Size of the walk-forward correction (ALL, ridge): sd 2.26 pts, 95% of games within +/-4.76 pts. Torvik MAE on test seasons 13.435 -> corrected 13.350.

## 4. Market test (games with a closing total, test seasons only)

Games: 39,185.

|                             |    MAE |   RMSE |
|:----------------------------|-------:|-------:|
| Torvik frozen               | 13.655 | 17.325 |
| Torvik + factor correction  | 13.582 | 17.208 |
| Closing total               | 13.285 | 16.858 |
| 50/50 blend corrected+close | 13.352 | 16.930 |

Regressions of (actual - close), SEs clustered by date. A market-efficient close gives slope 0.

| regression                   | term     |   slope |      t |     p |   R2% |
|:-----------------------------|:---------|--------:|-------:|------:|------:|
| Torvik edge (torvik - close) | edge     |  -0.041 | -1.764 | 0.078 | 0.009 |
| factor correction only       | corr_all |   0.224 |  5.698 | 0.000 | 0.091 |
| edge + factor correction     | edge     |   0.008 |  0.335 | 0.737 | 0.091 |
| edge + factor correction     | corr_all |   0.229 |  5.363 | 0.000 | 0.091 |

Encompassing regression: actual = a + b1*Torvik + b2*close (b1 > 0 means Torvik adds information to the close).

|                            |   b_torvik |   t_torvik |   b_close |   t_close |
|:---------------------------|-----------:|-----------:|----------:|----------:|
| Torvik frozen              |     -0.041 |     -1.730 |     1.041 |    38.296 |
| Torvik + factor correction |      0.041 |      1.651 |     0.958 |    37.639 |

### Walk-forward model of the MARKET error (actual - close) from the factors

| model                     |     n |   R2_oos% |      t |   corr |   pred_sd | seasons+   |
|:--------------------------|------:|----------:|-------:|-------:|----------:|:-----------|
| edge only (ridge)         | 39766 |     0.002 |  0.586 | -0.006 |     0.103 | 5/8        |
| pace_mismatch (ridge)     | 39766 |     0.021 |  0.987 |  0.013 |     0.363 | 5/8        |
| roster_change (ridge)     | 39185 |    -0.017 | -0.735 |  0.003 |     0.351 | 3/8        |
| shot_profile (ridge)      | 39766 |     0.044 |  1.597 |  0.019 |     0.451 | 7/8        |
| opponent_style (ridge)    | 39766 |     0.209 |  4.743 |  0.044 |     0.760 | 8/8        |
| ALL four families (ridge) | 39185 |     0.190 |  2.759 |  0.047 |     1.110 | 6/8        |
| ALL four families (gbm)   | 39185 |     0.199 |  4.015 |  0.044 |     0.839 | 6/8        |
| ALL + edge (ridge)        | 39185 |     0.184 |  2.696 |  0.046 |     1.102 | 5/8        |
| ALL + edge (gbm)          | 39185 |     0.194 |  3.717 |  0.044 |     0.882 | 7/8        |

### Betting simulation at -110 (break-even 52.38%), test seasons, closing totals

Bet OVER when signal >= threshold, UNDER when <= -threshold. Pushes excluded from win%.

Reference: betting every OVER wins 50.15% (n=39,469). The mean of actual-close is +0.71 but the median is +0.00 (overtime skew), so the direct market models E-G bet on the prediction minus the training-seasons mean.

**A. Raw Torvik edge (torvik - close)**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|           1 |  30557 |  49.33 |       -5.78 |      -10.69 |     -2.35 | 0/8             |
|           2 |  22924 |  49.45 |       -5.56 |       -8.90 |     -1.68 | 0/8             |
|           3 |  16244 |  49.70 |       -5.07 |       -6.83 |     -0.75 | 0/8             |
|           4 |  10991 |  49.65 |       -5.18 |       -5.73 |     -0.73 | 0/8             |
|           5 |   7140 |  49.66 |       -5.15 |       -4.60 |     -0.57 | 1/8             |
|           6 |   4375 |  48.75 |       -6.87 |       -4.80 |     -1.65 | 0/8             |

**B. Corrected Torvik edge (torvik + factor correction - close)**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|           1 |  30231 |  50.57 |       -3.44 |       -6.31 |      1.97 | 0/8             |
|           2 |  22270 |  50.49 |       -3.58 |       -5.65 |      1.46 | 0/8             |
|           3 |  15508 |  50.47 |       -3.62 |       -4.76 |      1.17 | 1/8             |
|           4 |  10257 |  50.51 |       -3.54 |       -3.79 |      1.04 | 1/8             |
|           5 |   6549 |  50.28 |       -3.97 |       -3.40 |      0.46 | 1/8             |
|           6 |   4061 |  49.94 |       -4.62 |       -3.12 |     -0.08 | 1/8             |

**C. Factor correction alone, ridge (ignores Torvik-vs-close gap)**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.50 |  32611 |  51.16 |       -2.32 |       -4.42 |      4.18 | 0/8             |
|        1.00 |  26408 |  51.54 |       -1.59 |       -2.73 |      5.01 | 1/8             |
|        1.50 |  20813 |  51.81 |       -1.08 |       -1.65 |      5.22 | 2/8             |
|        2.00 |  15845 |  51.65 |       -1.38 |       -1.84 |      4.15 | 2/8             |

**D. Factor correction alone, GBM**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.50 |  31663 |  51.02 |       -2.57 |       -4.84 |      3.64 | 1/8             |
|        1.00 |  24586 |  51.26 |       -2.11 |       -3.50 |      3.97 | 1/8             |
|        1.50 |  18544 |  51.17 |       -2.29 |       -3.30 |      3.19 | 1/8             |
|        2.00 |  13557 |  51.48 |       -1.71 |       -2.10 |      3.44 | 1/8             |

**E. Direct market-error model (ALL + edge, ridge)**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.25 |  32162 |  51.87 |       -0.96 |       -1.83 |      6.71 | 2/8             |
|        0.50 |  25738 |  52.27 |       -0.21 |       -0.36 |      7.28 | 4/8             |
|        0.75 |  19879 |  52.45 |        0.13 |        0.19 |      6.90 | 5/8             |
|        1.00 |  14724 |  52.75 |        0.70 |        0.90 |      6.68 | 5/8             |
|        1.50 |   7147 |  53.74 |        2.58 |        2.31 |      6.33 | 7/8             |
|        2.00 |   2920 |  53.63 |        2.37 |        1.35 |      3.92 | 4/8             |
|        2.50 |    975 |  52.72 |        0.64 |        0.21 |      1.70 | 5/8             |

**F. Direct market-error model (ALL + edge, GBM)**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.25 |  29187 |  51.79 |       -1.11 |       -2.01 |      6.13 | 3/8             |
|        0.50 |  20862 |  52.39 |        0.02 |        0.03 |      6.91 | 4/8             |
|        0.75 |  14370 |  52.85 |        0.88 |        1.12 |      6.82 | 5/8             |
|        1.00 |   9434 |  53.38 |        1.89 |        1.95 |      6.57 | 7/8             |
|        1.50 |   3587 |  53.81 |        2.70 |        1.71 |      4.56 | 7/8             |
|        2.00 |   1278 |  54.38 |        3.79 |        1.43 |      3.13 | 6/8             |
|        2.50 |    402 |  52.24 |       -0.27 |       -0.06 |      0.90 | 3/7             |

**G. Direct market-error model (factors only, ridge)**

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.25 |  32238 |  51.94 |       -0.83 |       -1.58 |      6.97 | 3/8             |
|        0.50 |  25788 |  52.12 |       -0.49 |       -0.84 |      6.81 | 4/8             |
|        0.75 |  19998 |  52.38 |       -0.00 |       -0.00 |      6.73 | 5/8             |
|        1.00 |  14917 |  52.69 |        0.59 |        0.76 |      6.57 | 5/8             |
|        1.50 |   7265 |  53.74 |        2.57 |        2.31 |      6.37 | 7/8             |
|        2.00 |   2978 |  53.26 |        1.66 |        0.96 |      3.55 | 5/8             |
|        2.50 |   1002 |  52.99 |        1.16 |        0.39 |      1.90 | 6/8             |

### Robustness of the direct factors-only market model (G)

|   season | line_source   |   corr(pred, actual-close) |   bets@1.0 |   win%@1.0 |   bets@1.5 |   win%@1.5 |
|---------:|:--------------|---------------------------:|-----------:|-----------:|-----------:|-----------:|
|     2019 | sbr           |                       0.05 |       1969 |      52.01 |       1020 |      51.47 |
|     2020 | sbr           |                       0.06 |       2328 |      53.09 |       1341 |      53.39 |
|     2021 | sbr           |                       0.05 |       1315 |      53.08 |        578 |      56.57 |
|     2022 | espn          |                       0.08 |       1764 |      53.57 |        823 |      54.19 |
|     2023 | espn          |                       0.06 |       1801 |      53.58 |        744 |      54.57 |
|     2024 | espn          |                       0.03 |       1847 |      51.33 |        831 |      53.07 |
|     2025 | espn          |                       0.05 |       1878 |      53.46 |        917 |      54.96 |
|     2026 | espn          |                       0.03 |       2015 |      51.61 |       1011 |      53.31 |

Same signal settled against the OPENING total instead (seasons with an opening line, n=15,769; note the model was trained on closing-line errors):

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.50 |  10174 |  52.16 |       -0.42 |       -0.44 |      4.36 | 0/3             |
|        1.00 |   5735 |  53.13 |        1.43 |        1.14 |      4.74 | 3/3             |
|        1.50 |   2757 |  54.95 |        4.90 |        2.70 |      5.20 | 3/3             |
|        2.00 |   1144 |  55.07 |        5.13 |        1.82 |      3.43 | 3/3             |

...and against the close on the identical games:

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.50 |  10193 |  51.51 |       -1.67 |       -1.77 |      3.04 | 0/3             |
|        1.00 |   5740 |  52.13 |       -0.49 |       -0.39 |      3.22 | 1/3             |
|        1.50 |   2759 |  53.79 |        2.68 |        1.48 |      3.98 | 3/3             |
|        2.00 |   1144 |  52.88 |        0.96 |        0.34 |      1.95 | 2/3             |

Line movement open->close on those games: corr with the signal 0.140; corr with raw Torvik edge vs open 0.115.

Regulation-only games (drops overtime luck):

|   threshold |   bets |   win% |   ROI%@-110 |   z_vs_52.4 |   z_vs_50 | seasons>52.4%   |
|------------:|-------:|-------:|------------:|------------:|----------:|:----------------|
|        0.50 |  24294 |  51.79 |       -1.12 |       -1.84 |      5.58 | 2/8             |
|        1.00 |  14053 |  52.25 |       -0.24 |       -0.31 |      5.34 | 4/8             |
|        1.50 |   6849 |  53.13 |        1.42 |        1.24 |      5.18 | 6/8             |
|        2.00 |   2811 |  53.01 |        1.19 |        0.66 |      3.19 | 5/8             |

Direction split at threshold 1.0: overs 9,310 bets, 52.71% win; unders 5,729 bets, 52.65% win.

### Single-factor market check

Slope of (actual - close) per +1 SD of each factor, season fixed effects, clustered by date, all seasons with odds.

| factor                   | family         |   slope |     t |    p |   slope_2016_20 |   t_2016_20 |   slope_2021_26 |   t_2021_26 |    q |
|:-------------------------|:---------------|--------:|------:|-----:|----------------:|------------:|----------------:|------------:|-----:|
| pace_absdiff             | pace_mismatch  |   -0.17 | -2.12 | 0.03 |           -0.03 |       -0.28 |           -0.30 |       -2.75 | 0.06 |
| pace_sum                 | pace_mismatch  |    0.26 |  3.43 | 0.00 |            0.37 |        3.21 |            0.17 |        1.68 | 0.00 |
| pace_inter               | pace_mismatch  |    0.23 |  2.80 | 0.01 |            0.08 |        0.70 |            0.39 |        3.35 | 0.01 |
| pace_fast_slow           | pace_mismatch  |    0.13 |  1.63 | 0.10 |            0.27 |        2.38 |           -0.01 |       -0.05 | 0.16 |
| pace_slow_side           | pace_mismatch  |    0.32 |  4.24 | 0.00 |            0.36 |        2.97 |            0.30 |        3.02 | 0.00 |
| roster_turnover          | roster_change  |    0.00 |  0.01 | 0.99 |           -0.01 |       -0.08 |            0.01 |        0.08 | 0.99 |
| roster_turnover_max      | roster_change  |    0.01 |  0.11 | 0.92 |           -0.04 |       -0.27 |            0.04 |        0.34 | 0.94 |
| roster_new_coach         | roster_change  |   -0.08 | -0.99 | 0.32 |           -0.11 |       -0.95 |           -0.05 |       -0.51 | 0.44 |
| roster_early             | roster_change  |   -0.23 | -2.51 | 0.01 |           -0.45 |       -3.64 |           -0.09 |       -0.73 | 0.03 |
| roster_turnover_x_early  | roster_change  |    0.05 |  0.55 | 0.59 |            0.26 |        1.80 |           -0.04 |       -0.34 | 0.69 |
| roster_new_coach_x_early | roster_change  |   -0.13 | -1.59 | 0.11 |           -0.28 |       -2.31 |           -0.04 |       -0.40 | 0.17 |
| shot_3par                | shot_profile   |    0.19 |  2.54 | 0.01 |            0.02 |        0.19 |            0.31 |        3.13 | 0.03 |
| shot_ftr                 | shot_profile   |   -0.32 | -4.02 | 0.00 |           -0.37 |       -2.97 |           -0.29 |       -2.75 | 0.00 |
| shot_orb                 | shot_profile   |   -0.24 | -3.04 | 0.00 |           -0.27 |       -2.09 |           -0.23 |       -2.21 | 0.01 |
| shot_tov                 | shot_profile   |   -0.11 | -1.30 | 0.19 |            0.00 |        0.02 |           -0.17 |       -1.71 | 0.28 |
| shot_ast                 | shot_profile   |   -0.06 | -0.79 | 0.43 |            0.00 |        0.02 |           -0.10 |       -1.03 | 0.57 |
| shot_3p_pct              | shot_profile   |   -0.18 | -2.20 | 0.03 |           -0.23 |       -1.99 |           -0.13 |       -1.19 | 0.05 |
| shot_2p_pct              | shot_profile   |   -0.28 | -3.34 | 0.00 |           -0.59 |       -4.33 |           -0.08 |       -0.77 | 0.00 |
| shot_ft_pct              | shot_profile   |    0.16 |  2.10 | 0.04 |           -0.02 |       -0.14 |            0.28 |        2.87 | 0.06 |
| shot_3par_absdiff        | shot_profile   |    0.03 |  0.41 | 0.68 |            0.01 |        0.12 |            0.05 |        0.44 | 0.77 |
| opp_3par                 | opponent_style |   -0.06 | -0.71 | 0.48 |           -0.04 |       -0.33 |           -0.07 |       -0.65 | 0.60 |
| opp_3p_pct               | opponent_style |   -0.35 | -4.40 | 0.00 |           -0.30 |       -2.43 |           -0.39 |       -3.73 | 0.00 |
| opp_ftr                  | opponent_style |   -0.47 | -5.88 | 0.00 |           -0.40 |       -3.23 |           -0.54 |       -5.00 | 0.00 |
| opp_tov                  | opponent_style |   -0.24 | -3.02 | 0.00 |           -0.17 |       -1.28 |           -0.29 |       -2.83 | 0.01 |
| opp_orb                  | opponent_style |    0.24 |  2.98 | 0.00 |            0.39 |        2.85 |            0.15 |        1.47 | 0.01 |
| opp_stl                  | opponent_style |   -0.29 | -3.56 | 0.00 |           -0.30 |       -2.16 |           -0.29 |       -2.83 | 0.00 |
| opp_blk                  | opponent_style |   -0.27 | -3.49 | 0.00 |           -0.25 |       -2.15 |           -0.29 |       -2.77 | 0.00 |
| opp_foul                 | opponent_style |   -0.41 | -4.79 | 0.00 |           -0.41 |       -3.16 |           -0.41 |       -3.60 | 0.00 |
| opp_x_3par               | opponent_style |    0.16 |  2.18 | 0.03 |            0.12 |        0.96 |            0.18 |        2.06 | 0.05 |
| opp_x_tov                | opponent_style |    0.05 |  0.68 | 0.50 |            0.01 |        0.04 |            0.07 |        0.82 | 0.61 |
| opp_x_orb                | opponent_style |    0.19 |  2.40 | 0.02 |            0.11 |        0.85 |            0.24 |        2.41 | 0.03 |
| opp_x_ftr                | opponent_style |    0.02 |  0.30 | 0.77 |           -0.19 |       -1.56 |            0.20 |        1.85 | 0.82 |
| opp_x_pace_press         | opponent_style |    0.02 |  0.29 | 0.77 |           -0.06 |       -0.53 |            0.09 |        0.86 | 0.82 |

Factors with q<0.05 against the close: 16/33; with |t|>2 in BOTH halves and the same sign: 8/33.

