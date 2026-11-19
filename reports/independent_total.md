# Independent pre-market totals: do they add anything?

Walk-forward, test seasons 2019-2026. None of these projections uses any sportsbook number. `signal` is the factor market-error signal refit walk-forward (the frozen model's out-of-sample twin).

## Accuracy

| forecast                                               |   games |   MAE |
|:-------------------------------------------------------|--------:|------:|
| Closing total                                          |   39766 | 13.29 |
| Opening total                                          |   28989 | 13.50 |
| Torvik frozen total (as published)                     |   39766 | 13.66 |
| Own model: ratings only (GBM)                          |   39766 | 13.68 |
| Own model: ratings + 33 factors (GBM)                  |   39185 | 13.53 |
| Own model: Torvik total + ratings + 33 factors (ridge) |   39185 | 13.46 |

## Against the opener

Does the gap between the projection and the line predict (actual - line)? A slope of 1 would mean the projection is right and the line wrong.

| projection                                             |     n |   corr(edge, signal) |   edge alone: slope |      t |   with signal: edge slope |     t  |   with signal: signal slope |    t   |
|:-------------------------------------------------------|------:|---------------------:|--------------------:|-------:|--------------------------:|-------:|----------------------------:|-------:|
| Torvik frozen total (as published)                     | 28755 |                0.076 |               0.064 |  1.844 |                     0.040 |  1.126 |                       0.893 |  9.883 |
| Own model: ratings only (GBM)                          | 28755 |               -0.187 |               0.102 |  3.455 |                     0.162 |  5.407 |                       0.995 | 10.930 |
| Own model: ratings + 33 factors (GBM)                  | 28755 |                0.210 |               0.343 | 11.425 |                     0.290 |  9.318 |                       0.726 |  7.867 |
| Own model: Torvik total + ratings + 33 factors (ridge) | 28755 |                0.441 |               0.469 | 14.119 |                     0.399 | 10.681 |                       0.429 |  4.261 |

| bet rule                                                                                   |   bets |   win% | CI        | seasons>BE   |
|:-------------------------------------------------------------------------------------------|-------:|-------:|:----------|:-------------|
| signal >= 1.5 alone (reference)                                                            |   5594 |  55.13 | 53.8-56.4 | 6/6          |
| Torvik frozen total (as published): gap >= 2                                               |  13989 |  50.28 | 49.4-51.1 | 0/6          |
| Torvik frozen total (as published): gap >= 3                                               |   8906 |  50.74 | 49.7-51.8 | 0/6          |
| Torvik frozen total (as published): gap >= 4                                               |   5487 |  51.78 | 50.5-53.1 | 2/6          |
| signal >= 1.5 AND Torvik frozen total (as published) agrees by >= 2                        |   1713 |  54.58 | 52.2-56.9 | 6/6          |
| signal >= 1.5 BUT Torvik frozen total (as published) disagrees by >= 2                     |   1103 |  54.31 | 51.4-57.2 | 5/6          |
| Own model: ratings only (GBM): gap >= 2                                                    |  15782 |  50.37 | 49.6-51.1 | 1/6          |
| Own model: ratings only (GBM): gap >= 3                                                    |  10678 |  51.01 | 50.1-52.0 | 1/6          |
| Own model: ratings only (GBM): gap >= 4                                                    |   6784 |  51.53 | 50.3-52.7 | 1/6          |
| signal >= 1.5 AND Own model: ratings only (GBM) agrees by >= 2                             |   1054 |  55.22 | 52.2-58.2 | 6/6          |
| signal >= 1.5 BUT Own model: ratings only (GBM) disagrees by >= 2                          |   2243 |  53.63 | 51.6-55.7 | 5/6          |
| Own model: ratings + 33 factors (GBM): gap >= 2                                            |  15514 |  53.13 | 52.3-53.9 | 5/6          |
| Own model: ratings + 33 factors (GBM): gap >= 3                                            |  10392 |  53.88 | 52.9-54.8 | 6/6          |
| Own model: ratings + 33 factors (GBM): gap >= 4                                            |   6624 |  54.60 | 53.4-55.8 | 6/6          |
| signal >= 1.5 AND Own model: ratings + 33 factors (GBM) agrees by >= 2                     |   2384 |  57.05 | 55.1-59.0 | 6/6          |
| signal >= 1.5 BUT Own model: ratings + 33 factors (GBM) disagrees by >= 2                  |    836 |  53.11 | 49.7-56.5 | 3/6          |
| Own model: Torvik total + ratings + 33 factors (ridge): gap >= 2                           |  14748 |  54.05 | 53.2-54.9 | 6/6          |
| Own model: Torvik total + ratings + 33 factors (ridge): gap >= 3                           |   9347 |  55.18 | 54.2-56.2 | 6/6          |
| Own model: Torvik total + ratings + 33 factors (ridge): gap >= 4                           |   5614 |  56.11 | 54.8-57.4 | 6/6          |
| signal >= 1.5 AND Own model: Torvik total + ratings + 33 factors (ridge) agrees by >= 2    |   3238 |  56.61 | 54.9-58.3 | 6/6          |
| signal >= 1.5 BUT Own model: Torvik total + ratings + 33 factors (ridge) disagrees by >= 2 |    341 |  48.97 | 43.7-54.3 | 0/6          |

## Against the close

Does the gap between the projection and the line predict (actual - line)? A slope of 1 would mean the projection is right and the line wrong.

| projection                                             |     n |   corr(edge, signal) |   edge alone: slope |      t |   with signal: edge slope |     t  |   with signal: signal slope |   t   |
|:-------------------------------------------------------|------:|---------------------:|--------------------:|-------:|--------------------------:|-------:|----------------------------:|------:|
| Torvik frozen total (as published)                     | 39185 |               -0.035 |              -0.041 | -1.764 |                    -0.033 | -1.441 |                       0.704 | 9.228 |
| Own model: ratings only (GBM)                          | 39185 |               -0.254 |              -0.057 | -2.614 |                    -0.005 | -0.235 |                       0.703 | 8.863 |
| Own model: ratings + 33 factors (GBM)                  | 39185 |                0.127 |               0.097 |  3.902 |                     0.068 |  2.730 |                       0.682 | 8.896 |
| Own model: Torvik total + ratings + 33 factors (ridge) | 39185 |                0.327 |               0.151 |  5.319 |                     0.077 |  2.556 |                       0.638 | 7.940 |

| bet rule                                                                                   |   bets |   win% | CI        | seasons>BE   |
|:-------------------------------------------------------------------------------------------|-------:|-------:|:----------|:-------------|
| signal >= 1.5 alone (reference)                                                            |   7265 |  53.74 | 52.6-54.9 | 7/8          |
| Torvik frozen total (as published): gap >= 2                                               |  22924 |  49.45 | 48.8-50.1 | 0/8          |
| Torvik frozen total (as published): gap >= 3                                               |  16244 |  49.70 | 48.9-50.5 | 0/8          |
| Torvik frozen total (as published): gap >= 4                                               |  10991 |  49.65 | 48.7-50.6 | 0/8          |
| signal >= 1.5 AND Torvik frozen total (as published) agrees by >= 2                        |   2003 |  53.62 | 51.4-55.8 | 5/8          |
| signal >= 1.5 BUT Torvik frozen total (as published) disagrees by >= 2                     |   2315 |  53.69 | 51.7-55.7 | 7/8          |
| Own model: ratings only (GBM): gap >= 2                                                    |  22631 |  48.97 | 48.3-49.6 | 0/8          |
| Own model: ratings only (GBM): gap >= 3                                                    |  16061 |  48.86 | 48.1-49.6 | 0/8          |
| Own model: ratings only (GBM): gap >= 4                                                    |  10838 |  48.84 | 47.9-49.8 | 0/8          |
| signal >= 1.5 AND Own model: ratings only (GBM) agrees by >= 2                             |   1075 |  52.47 | 49.5-55.4 | 6/8          |
| signal >= 1.5 BUT Own model: ratings only (GBM) disagrees by >= 2                          |   3447 |  53.93 | 52.3-55.6 | 7/8          |
| Own model: ratings + 33 factors (GBM): gap >= 2                                            |  21488 |  50.80 | 50.1-51.5 | 1/8          |
| Own model: ratings + 33 factors (GBM): gap >= 3                                            |  14589 |  50.94 | 50.1-51.7 | 2/8          |
| Own model: ratings + 33 factors (GBM): gap >= 4                                            |   9473 |  50.93 | 49.9-51.9 | 1/8          |
| signal >= 1.5 AND Own model: ratings + 33 factors (GBM) agrees by >= 2                     |   2751 |  54.31 | 52.4-56.2 | 7/8          |
| signal >= 1.5 BUT Own model: ratings + 33 factors (GBM) disagrees by >= 2                  |   1404 |  53.06 | 50.4-55.7 | 4/8          |
| Own model: Torvik total + ratings + 33 factors (ridge): gap >= 2                           |  20029 |  51.13 | 50.4-51.8 | 2/8          |
| Own model: Torvik total + ratings + 33 factors (ridge): gap >= 3                           |  12996 |  51.61 | 50.7-52.5 | 3/8          |
| Own model: Torvik total + ratings + 33 factors (ridge): gap >= 4                           |   7885 |  51.68 | 50.6-52.8 | 4/8          |
| signal >= 1.5 AND Own model: Torvik total + ratings + 33 factors (ridge) agrees by >= 2    |   3663 |  54.05 | 52.4-55.7 | 6/8          |
| signal >= 1.5 BUT Own model: Torvik total + ratings + 33 factors (ridge) disagrees by >= 2 |    647 |  53.32 | 49.5-57.1 | 3/8          |

