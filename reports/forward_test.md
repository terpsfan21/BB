# Frozen v1 forward test, season 2026-27

Generated 2026-11-23 21:24 UTC. Log rows: 1834; prospective 1061, reconstruction 773.

## Prospective predictions

Settled games: 174; with a DraftKings close: 111; flagged bets (|signal| >= 1.5): 22; overtime games: 14.

| line                                |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:------------------------------------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open                             |         1.5 |     22 |   59.1 | 38.7-76.7 |                   12.2 | -27.7 to 52.2 |
| DK close                            |         1.5 |     22 |   54.5 | 34.7-73.1 |                    3.9 | -36.7 to 44.4 |
| first DK line seen after prediction |         1.5 |     36 |   52.8 | 37.0-68.0 |                    0.6 | -30.9 to 32.2 |

Closing-line value on flagged bets taken at the DK open: mean +1.41 pts; line moved toward the bet 64%, against 9%, unchanged 27%.

All lined games: MAE of the close 11.89; MAE of close + signal 11.98; corr(signal, actual - close) +0.051; corr(signal, close - open) +0.342; calibration slope of (actual - close) on signal +0.71 (1.0 = signal sized correctly).

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 772; with a DraftKings close: 770; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.037; corr(signal, close - open) +0.142; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

