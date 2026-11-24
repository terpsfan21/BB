# Frozen v1 forward test, season 2026-27

Generated 2026-11-24 21:24 UTC. Log rows: 2009; prospective 1236, reconstruction 773.

## Prospective predictions

Settled games: 209; with a DraftKings close: 145; flagged bets (|signal| >= 1.5): 28; overtime games: 17.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     28 |   64.3 | 45.8-79.3 |                   22.2 | -12.2 to 56.6 |
| DK close                            |         1.5 |     28 |   53.6 | 35.8-70.5 |                    2   | -33.8 to 37.8 |
| first DK line seen after prediction |         1.5 |     42 |   52.4 | 37.7-66.6 |                   -0.1 | -29.3 to 29.0 |

Closing-line value on flagged bets taken at the DK open: mean +1.57 pts; line moved toward the bet 64%, against 11%, unchanged 25%.

All lined games: MAE of the close 12.68; MAE of close + signal 12.76; corr(signal, actual - close) +0.026; corr(signal, close - open) +0.367; calibration slope of (actual - close) on signal +0.39 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

