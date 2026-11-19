"""Would an independent pre-market total add value on top of the frozen-style market-error signal?

Experimental only - does not touch frozen/v1.  Builds walk-forward (train seasons < S) projections of
the ACTUAL total from information available before any line exists, then asks whether the gap
between that projection and the opening / closing total predicts the market's error, alone and
after accounting for the factor signal.  Writes reports/independent_total.md.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import analyze as A                 # noqa: E402
from phase2 import bets             # noqa: E402

out = []


def emit(s=""):
    print(s)
    out.append(s)


def wf_total(g, X, cols, kind):
    pred = pd.Series(np.nan, index=g.index)
    ok = X[cols].notna().all(axis=1) & g.total.notna()
    for S in range(2019, int(g.season.max()) + 1):
        tr, te = ok & (g.season < S), ok & (g.season == S)
        if kind == "ridge":
            mu, sd = X.loc[tr, cols].mean(), X.loc[tr, cols].std().replace(0, 1)
            m = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit((X.loc[tr, cols] - mu) / sd, g.total[tr])
            pred[te] = m.predict((X.loc[te, cols] - mu) / sd)
        else:
            m = HistGradientBoostingRegressor(max_depth=4, learning_rate=0.05, max_iter=400, min_samples_leaf=200,
                                              l2_regularization=5.0, random_state=0).fit(X.loc[tr, cols], g.total[tr])
            pred[te] = m.predict(X.loc[te, cols])
    return pred


def main():
    g = pd.read_parquet(os.path.join(ROOT, "data", "processed", "games.parquet"))
    p2 = pd.read_parquet(os.path.join(ROOT, "data", "processed", "p2_games.parquet"))
    g = g.merge(p2[["season", "muid", "open_total"]], on=["season", "muid"], how="left")
    g = g[g.pre_total.notna() & g.pre_poss_stored.notna()].reset_index(drop=True)
    F, fam = A.build_features(g)
    allf = [c for v in fam.values() for c in v]
    g["err_open"] = g.total - g.open_total
    g.loc[(g.close_total - g.open_total).abs() > 15, ["open_total", "err_open"]] = np.nan
    gm = g[g.close_total.notna()]
    p, b = A.walk_forward(gm, F.loc[gm.index], gm.err_close, allf, "ridge")
    g["sig"] = (p - b).reindex(g.index)

    X = F.copy()
    for s in ("t1", "t2"):
        for k in ("adjoe", "adjde", "adjt"):
            X[f"{s}_{k}"] = g[f"{s}_tm_{k}"]
    X["neutral"] = g.neutral.astype(float)
    X["eff_x_pace"] = (g.t1_tm_adjoe * g.t2_tm_adjde + g.t2_tm_adjoe * g.t1_tm_adjde) / 100 * (g.t1_tm_adjt * g.t2_tm_adjt) / 6800
    X["torvik_total"], X["torvik_poss"] = g.pre_total, g.pre_poss
    ratings = ["t1_adjoe", "t1_adjde", "t1_adjt", "t2_adjoe", "t2_adjde", "t2_adjt", "neutral", "eff_x_pace"]
    models = {
        "Torvik frozen total (as published)": g.pre_total.where(g.season >= 2019),
        "Own model: ratings only (GBM)": wf_total(g, X, ratings, "gbm"),
        "Own model: ratings + 33 factors (GBM)": wf_total(g, X, ratings + allf, "gbm"),
        "Own model: Torvik total + ratings + 33 factors (ridge)": wf_total(g, X, ["torvik_total", "torvik_poss"] + ratings + allf, "ridge"),
    }
    emit("# Independent pre-market totals: do they add anything?\n")
    emit("Walk-forward, test seasons 2019-2026. None of these projections uses any sportsbook number. "
         "`signal` is the factor market-error signal refit walk-forward (the frozen model's out-of-sample twin).\n")
    t = g[(g.season >= 2019) & g.close_total.notna()]
    rows = [{"forecast": "Closing total", "games": len(t), "MAE": t.err_close.abs().mean()},
            {"forecast": "Opening total", "games": int(t.open_total.notna().sum()), "MAE": t.err_open.abs().mean()}]
    for nm, pr in models.items():
        k = t.index[pr[t.index].notna()]
        rows.append({"forecast": nm, "games": len(k), "MAE": (g.total[k] - pr[k]).abs().mean()})
    emit("## Accuracy\n")
    emit(pd.DataFrame(rows).to_markdown(index=False, floatfmt=".2f") + "\n")

    for line, err in (("open_total", "err_open"), ("close_total", "err_close")):
        emit(f"## Against the {'opener' if line == 'open_total' else 'close'}\n")
        rows, brow = [], []
        for nm, pr in models.items():
            d = g[g[line].notna() & pr.notna() & g.sig.notna()]
            edge = (pr - g[line])[d.index]
            r1 = sm.OLS(d[err], sm.add_constant(edge.rename("edge"))).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.date)[0]})
            Xb = sm.add_constant(pd.DataFrame({"edge": edge, "signal": d.sig}))
            r2 = sm.OLS(d[err], Xb).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.date)[0]})
            rows.append({"projection": nm, "n": len(d), "corr(edge, signal)": edge.corr(d.sig),
                         "edge alone: slope": r1.params["edge"], "t": r1.tvalues["edge"],
                         "with signal: edge slope": r2.params["edge"], "t ": r2.tvalues["edge"],
                         "with signal: signal slope": r2.params["signal"], "t  ": r2.tvalues["signal"]})
            for th in (2, 3, 4):
                x = bets(edge, d.total, d[line], th, season=d.season)
                brow.append({"bet rule": f"{nm}: gap >= {th}", "bets": x.get("bets"), "win%": x.get("win%"),
                             "CI": f"{x.get('ci_lo', np.nan):.1f}-{x.get('ci_hi', np.nan):.1f}", "seasons>BE": x.get("seasons>BE")})
            agree = (np.sign(edge) == np.sign(d.sig)) & (edge.abs() >= 2)
            x = bets(d.sig[agree], d.total[agree], d[line][agree], 1.5, season=d.season[agree])
            brow.append({"bet rule": f"signal >= 1.5 AND {nm} agrees by >= 2", "bets": x.get("bets"), "win%": x.get("win%"),
                         "CI": f"{x.get('ci_lo', np.nan):.1f}-{x.get('ci_hi', np.nan):.1f}", "seasons>BE": x.get("seasons>BE")})
            dis = (np.sign(edge) != np.sign(d.sig)) & (edge.abs() >= 2)
            x = bets(d.sig[dis], d.total[dis], d[line][dis], 1.5, season=d.season[dis])
            brow.append({"bet rule": f"signal >= 1.5 BUT {nm} disagrees by >= 2", "bets": x.get("bets"), "win%": x.get("win%"),
                         "CI": f"{x.get('ci_lo', np.nan):.1f}-{x.get('ci_hi', np.nan):.1f}", "seasons>BE": x.get("seasons>BE")})
        d = g[g[line].notna() & g.sig.notna()]
        x = bets(d.sig, d.total, d[line], 1.5, season=d.season)
        brow.insert(0, {"bet rule": "signal >= 1.5 alone (reference)", "bets": x["bets"], "win%": x["win%"],
                        "CI": f"{x['ci_lo']:.1f}-{x['ci_hi']:.1f}", "seasons>BE": x["seasons>BE"]})
        emit("Does the gap between the projection and the line predict (actual - line)? A slope of 1 would mean the projection is right and the line wrong.\n")
        emit(pd.DataFrame(rows).to_markdown(index=False, floatfmt=".3f") + "\n")
        emit(pd.DataFrame(brow).to_markdown(index=False, floatfmt=".2f") + "\n")
    open(os.path.join(ROOT, "reports", "independent_total.md"), "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
