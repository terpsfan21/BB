# Frozen v1 forward test, season 2026-27

Generated 2026-11-22 10:23 UTC. Log rows: 1641; prospective 868, reconstruction 773.

## Prospective predictions

Settled games: 130; with a DraftKings close: 90; flagged bets (|signal| >= 1.5): 18; overtime games: 9.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     18 |   61.1 | 38.6-79.7 |                   15.7 | -28.2 to 59.6 |
| DK close                            |         1.5 |     18 |   55.6 | 33.7-75.4 |                    5.8 | -39.2 to 50.8 |
| first DK line seen after prediction |         1.5 |     27 |   51.9 | 34.0-69.3 |                   -1.3 | -37.8 to 35.3 |

Closing-line value on flagged bets taken at the DK open: mean +1.22 pts; line moved toward the bet 56%, against 11%, unchanged 33%.

All lined games: MAE of the close 11.46; MAE of close + signal 11.53; corr(signal, actual - close) +0.050; corr(signal, close - open) +0.368; calibration slope of (actual - close) on signal +0.69 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

