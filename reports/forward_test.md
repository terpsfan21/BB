# Frozen v1 forward test, season 2026-27

Generated 2026-11-27 10:25 UTC. Log rows: 2626; prospective 1852, reconstruction 774.

## Prospective predictions

Settled games: 356; with a DraftKings close: 242; flagged bets (|signal| >= 1.5): 49; overtime games: 26.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     49 |   55.1 | 41.3-68.1 |                    5.1 | -21.8 to 31.9 |
| DK close                            |         1.5 |     49 |   49   | 35.6-62.5 |                   -6.9 | -33.8 to 20.0 |
| first DK line seen after prediction |         1.5 |     67 |   53.7 | 41.9-65.1 |                    2.7 | -20.3 to 25.6 |

Closing-line value on flagged bets taken at the DK open: mean +1.24 pts; line moved toward the bet 59%, against 20%, unchanged 20%.

All lined games: MAE of the close 12.70; MAE of close + signal 12.76; corr(signal, actual - close) +0.029; corr(signal, close - open) +0.303; calibration slope of (actual - close) on signal +0.43 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 773; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

