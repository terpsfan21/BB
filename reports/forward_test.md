# Frozen v1 forward test, season 2026-27

Generated 2026-11-21 21:24 UTC. Log rows: 1439; prospective 666, reconstruction 773.

## Prospective predictions

Settled games: 93; with a DraftKings close: 72; flagged bets (|signal| >= 1.5): 15; overtime games: 8.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     15 |   73.3 | 48.0-89.1 |                   38.8 | -5.0 to 82.7  |
| DK close                            |         1.5 |     15 |   66.7 | 41.7-84.8 |                   27   | -20.1 to 74.0 |
| first DK line seen after prediction |         1.5 |     20 |   60   | 38.7-78.1 |                   14.3 | -27.7 to 56.3 |

Closing-line value on flagged bets taken at the DK open: mean +1.53 pts; line moved toward the bet 53%, against 7%, unchanged 40%.

All lined games: MAE of the close 11.54; MAE of close + signal 11.48; corr(signal, actual - close) +0.165; corr(signal, close - open) +0.427; calibration slope of (actual - close) on signal +2.29 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

