# Frozen v1 forward test, season 2026-27

Generated 2026-11-21 10:24 UTC. Log rows: 1439; prospective 666, reconstruction 773.

## Prospective predictions

Settled games: 79; with a DraftKings close: 50; flagged bets (|signal| >= 1.5): 11; overtime games: 6.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     11 |   72.7 | 43.4-90.3 |                   37.4 | -14.8 to 89.6 |
| DK close                            |         1.5 |     11 |   63.6 | 35.4-84.8 |                   20.9 | -35.7 to 77.6 |
| first DK line seen after prediction |         1.5 |     17 |   64.7 | 41.3-82.7 |                   23.3 | -21.3 to 68.0 |

Closing-line value on flagged bets taken at the DK open: mean +0.82 pts; line moved toward the bet 45%, against 9%, unchanged 45%.

All lined games: MAE of the close 11.08; MAE of close + signal 11.06; corr(signal, actual - close) +0.175; corr(signal, close - open) +0.289; calibration slope of (actual - close) on signal +2.33 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 769; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.038; corr(signal, close - open) +0.141; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

