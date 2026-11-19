"""Regression test for the frozen model: the frozen code must reproduce (a) the stored training
signals from the committed dataset and (b) the dataset's style features from raw box scores
(needs data/raw; skipped if absent).  Run: python frozen/v1/check.py"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
import features as FZ      # noqa: E402
import predict as PZ       # noqa: E402

g = pd.read_parquet(os.path.join(ROOT, "data", "processed", "games.parquet"))
gg = g[g.pre_total.notna() & g.pre_poss_stored.notna()].reset_index(drop=True)
s = PZ.score(gg)
ref = pd.read_parquet(os.path.join(HERE, "train_signals.parquet"))
got = gg[["muid", "season"]].assign(signal=s.signal.values)
d = (ref.merge(got, on=["muid", "season"]).eval("signal - signal_in_sample")).abs()
print(f"(a) training signals: n={len(ref)} max abs diff={d.max():.2e}")
assert d.max() < 1e-6
if os.path.exists(os.path.join(ROOT, "data", "raw", "torvik", "sked", "2016.csv")):
    import build_dataset as B
    full = pd.concat([B.load_sked(y) for y in B.SEASONS], ignore_index=True)
    st = FZ.style_features(full, PZ.MODEL["league_means_per_game"], PZ.MODEL["shrink_K"])
    m = g[["muid", "season"] + [c for c in g.columns if "_s_" in c]].merge(st, on=["muid", "season"], suffixes=("", "_fz"))
    worst = max(float((m[c] - m[c + "_fz"]).abs().max()) for c in g.columns if "_s_" in c)
    print(f"(b) style features rebuilt from raw: rows={len(m)} max abs diff={worst:.2e}")
    assert worst < 1e-4
print("frozen v1 OK")
