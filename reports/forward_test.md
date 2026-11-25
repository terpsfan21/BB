# Frozen v1 forward test, season 2026-27

Generated 2026-11-25 10:25 UTC. Log rows: 2231; prospective 1457, reconstruction 774.

## Prospective predictions

Settled games: 279; with a DraftKings close: 219; flagged bets (|signal| >= 1.5): 46; overtime games: 19.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     46 |   54.3 | 40.2-67.8 |                    3.6 | -24.1 to 31.4 |
| DK close                            |         1.5 |     46 |   47.8 | 34.1-61.9 |                   -9   | -36.8 to 18.8 |
| first DK line seen after prediction |         1.5 |     58 |   48.3 | 35.9-60.8 |                   -7.8 | -32.6 to 17.0 |

Closing-line value on flagged bets taken at the DK open: mean +1.39 pts; line moved toward the bet 61%, against 20%, unchanged 20%.

All lined games: MAE of the close 12.76; MAE of close + signal 12.86; corr(signal, actual - close) +0.003; corr(signal, close - open) +0.327; calibration slope of (actual - close) on signal +0.05 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

