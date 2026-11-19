# Frozen v1 forward test, season 2026-27

Generated 2026-11-19 10:07 UTC. Log rows: 898; prospective 127, reconstruction 771.

## Prospective predictions

No settled games yet.

## Reconstruction predictions

These were computed AFTER the games were played, from inputs dated before each game. They are a check that the pipeline works, not a forward test.

Settled games: 771; with a DraftKings close: 769; flagged bets (|signal| >= 1.5): 85; overtime games: 33.

| line     |   threshold |   bets |   win% | 95% CI    |   ROI% at actual price | ROI 95% CI    |
|:---------|------------:|-------:|-------:|:----------|-----------------------:|:--------------|
| DK open  |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.4 to 21.3 |
| DK close |         1.5 |     85 |   52.9 | 42.4-63.2 |                    0.9 | -19.5 to 21.2 |

Closing-line value on flagged bets taken at the DK open: mean +0.93 pts; line moved toward the bet 54%, against 35%, unchanged 11%.

All lined games: MAE of the close 13.24; MAE of close + signal 13.22; corr(signal, actual - close) +0.038; corr(signal, close - open) +0.141; calibration slope of (actual - close) on signal +0.73 (1.0 = signal sized correctly).

