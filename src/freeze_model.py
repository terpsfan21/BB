"""One-off: fit and freeze the factors-only market-error model on 2015-16..2025-26.
Run at repo commit 8527a46 data (data/processed/games.parquet).  Writes frozen/v1/model.json."""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "frozen", "v1"))
import analyze as A            # noqa: E402
import build_dataset as B      # noqa: E402
import features as FZ          # noqa: E402

P = os.path.join(ROOT, "data", "processed", "games.parquet")
g = pd.read_parquet(P)
g = g[g.pre_total.notna() & g.pre_poss_stored.notna()].reset_index(drop=True)
F, fam = A.build_features(g)
cols = [c for v in fam.values() for c in v]
ok = g.close_total.notna() & F[cols].notna().all(axis=1)
y = g.err_close[ok].astype(float)
mu, sd = F.loc[ok, cols].astype(float).mean(), F.loc[ok, cols].astype(float).std().replace(0, 1)
X = (F.loc[ok, cols].astype(float) - mu) / sd
m = RidgeCV(alphas=np.logspace(0, 4, 13)).fit(X, y)

# constants the feature code depended on
lgm = {k: float(pd.concat([g[f"t1_s_{k}"], g[f"t2_s_{k}"]]).mean()) for k in
       ("o_3par", "d_3par", "o_tov", "d_tov", "o_orb", "d_orb", "o_ftr", "d_ftr")}
full = pd.concat([B.load_sked(s) for s in B.SEASONS], ignore_index=True)       # incl. non-D1 opponents
longs = []
for me, opp in (("t1", "t2"), ("t2", "t1")):
    L = pd.DataFrame({"poss": full.poss, "poss_40": full.poss_40})
    for b in FZ.BOX:
        L[b] = full[f"{me}_{b}"]
        L["o_" + b] = full[f"{opp}_{b}"]
    longs.append(L)
L = pd.concat(longs).dropna(subset=["fga", "o_fga"])
L["n"] = 1.0
league = {k: float(v) for k, v in L[FZ.SUMS].mean().items()}

out = {
    "name": "factors-only market-error ridge", "version": "v1", "frozen_on": "2026-11-19",
    "trained_at_commit": "8527a46", "training_file_sha256": hashlib.sha256(open(P, "rb").read()).hexdigest(),
    "target": "actual_total - closing_total (SBR close 2015-16..2020-21, ESPN multi-book median after)",
    "train_seasons": [int(g.season[ok].min()), int(g.season[ok].max())], "n_train": int(ok.sum()),
    "features": cols, "families": fam, "mean": mu.to_dict(), "sd": sd.to_dict(),
    "coef": dict(zip(cols, map(float, m.coef_))), "intercept": float(m.intercept_), "ridge_alpha": float(m.alpha_),
    "ridge_alpha_grid": "logspace(0,4,13), efficient LOO CV",
    "centre": float(y.mean()), "threshold": 1.5,
    "shrink_K": 4, "league_means_per_game": league, "lgm": lgm,
}
json.dump(out, open(os.path.join(ROOT, "frozen", "v1", "model.json"), "w"), indent=1)
pred = m.predict(X) - y.mean()
pd.DataFrame({"muid": g.muid[ok].values, "season": g.season[ok].values, "signal_in_sample": pred}).to_parquet(
    os.path.join(ROOT, "frozen", "v1", "train_signals.parquet"), index=False)
print("n", ok.sum(), "alpha", m.alpha_, "centre", y.mean(), "signal sd", pred.std())
print(pd.Series(out["coef"]).sort_values().round(3).to_string())
