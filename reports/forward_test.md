# Frozen v1 forward test, season 2026-27

Generated 2026-11-24 10:23 UTC. Log rows: 2009; prospective 1236, reconstruction 773.

## Prospective predictions

Settled games: 200; with a DraftKings close: 131; flagged bets (|signal| >= 1.5): 25; overtime games: 16.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     25 |   64   | 44.5-79.8 |                   21.7 | -14.9 to 58.2 |
| DK close                            |         1.5 |     25 |   60   | 40.7-76.6 |                   14.2 | -23.1 to 51.6 |
| first DK line seen after prediction |         1.5 |     40 |   52.5 | 37.5-67.1 |                    0.2 | -29.7 to 30.1 |

Closing-line value on flagged bets taken at the DK open: mean +1.36 pts; line moved toward the bet 64%, against 12%, unchanged 24%.

All lined games: MAE of the close 12.55; MAE of close + signal 12.59; corr(signal, actual - close) +0.042; corr(signal, close - open) +0.345; calibration slope of (actual - close) on signal +0.62 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

