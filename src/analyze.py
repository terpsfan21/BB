"""Systematic-error analysis of Torvik pregame totals.

1. Baseline accuracy of Torvik (frozen) vs sportsbook close; error decomposition.
2. In-sample screen: does each pregame factor (pace mismatch / roster change / shot
   profile / opponent style) line up with Torvik's total, possession or efficiency error?
3. Walk-forward out-of-sample test: train on seasons < S, predict season S.
4. Market test: does any of it predict (actual - closing total)?  Betting simulation at -110.

Writes reports/results.md and reports/results.json.
"""
import json
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV

warnings.filterwarnings("ignore")
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "reports")
FIRST_TEST = 2019
BREAKEVEN = 110 / 210
md = []


def emit(s=""):
    print(s)
    md.append(s)


def table(df, floatfmt="%.3f"):
    emit(df.to_markdown(floatfmt=floatfmt.replace("%", "")))
    emit()


# ----------------------------------------------------------------------------- features
def build_features(g):
    f = pd.DataFrame(index=g.index)
    fam = {}
    a1, a2 = g.t1_tm_adjt, g.t2_tm_adjt
    # centre on the mean of the two snapshot tempos available that day (no look-ahead)
    lg = g.groupby("date")[["t1_tm_adjt", "t2_tm_adjt"]].transform("mean").mean(axis=1)
    f["pace_absdiff"] = (a1 - a2).abs()
    f["pace_sum"] = a1 + a2 - 2 * lg
    f["pace_inter"] = (a1 - lg) * (a2 - lg)
    f["pace_fast_slow"] = np.maximum(a1, a2) - lg            # the faster team's deviation
    f["pace_slow_side"] = np.minimum(a1, a2) - lg            # the slower team's deviation
    fam["pace_mismatch"] = ["pace_absdiff", "pace_sum", "pace_inter", "pace_fast_slow", "pace_slow_side"]

    gp = np.minimum(g.t1_s_gp, g.t2_s_gp)
    early = np.exp(-gp / 6.0)                                # 1 on opening night, ~0.2 after 10 games
    turn = 1 - g[["t1_ret_min", "t2_ret_min"]].mean(axis=1)
    f["roster_turnover"] = turn
    f["roster_turnover_max"] = 1 - g[["t1_ret_min", "t2_ret_min"]].min(axis=1)
    f["roster_new_coach"] = g[["t1_new_coach", "t2_new_coach"]].sum(axis=1, min_count=2)
    f["roster_early"] = early
    f["roster_turnover_x_early"] = (turn - 0.5) * early
    f["roster_new_coach_x_early"] = f.roster_new_coach * early
    fam["roster_change"] = ["roster_turnover", "roster_turnover_max", "roster_new_coach", "roster_early",
                            "roster_turnover_x_early", "roster_new_coach_x_early"]

    def s(name):
        return g[f"t1_s_{name}"] + g[f"t2_s_{name}"]

    for k in ("o_3par", "o_ftr", "o_orb", "o_tov", "o_ast", "o_3p_pct", "o_2p_pct", "o_ft_pct"):
        f["shot_" + k[2:]] = s(k)
    f["shot_3par_absdiff"] = (g.t1_s_o_3par - g.t2_s_o_3par).abs()
    fam["shot_profile"] = [c for c in f.columns if c.startswith("shot_")]

    for k in ("d_3par", "d_3p_pct", "d_ftr", "d_tov", "d_orb", "d_stl", "d_blk", "d_foul"):
        f["opp_" + k[2:]] = s(k)
    lgm = {k: pd.concat([g[f"t1_s_{k}"], g[f"t2_s_{k}"]]).mean() for k in
           ("o_3par", "d_3par", "o_tov", "d_tov", "o_orb", "d_orb", "o_ftr", "d_ftr")}

    def cross(o, d):
        return ((g[f"t1_s_{o}"] - lgm[o]) * (g[f"t2_s_{d}"] - lgm[d]) +
                (g[f"t2_s_{o}"] - lgm[o]) * (g[f"t1_s_{d}"] - lgm[d]))

    f["opp_x_3par"] = cross("o_3par", "d_3par")
    f["opp_x_tov"] = cross("o_tov", "d_tov")
    f["opp_x_orb"] = cross("o_orb", "d_orb")
    f["opp_x_ftr"] = cross("o_ftr", "d_ftr")
    # tempo vs turnover-forcing / pressing defence
    f["opp_x_pace_press"] = (a1 - lg) * (g.t2_s_d_tov - lgm["d_tov"]) + (a2 - lg) * (g.t1_s_d_tov - lgm["d_tov"])
    fam["opponent_style"] = [c for c in f.columns if c.startswith("opp_")]
    return f, fam


# ----------------------------------------------------------------------------- stats helpers
def clustered_slope(y, x, groups, fe=None):
    X = pd.DataFrame({"x": x})
    if fe is not None:
        X = pd.concat([X, pd.get_dummies(fe, prefix="s", dtype=float)], axis=1)
    else:
        X = sm.add_constant(X)
    ok = X.notna().all(axis=1) & y.notna()
    r = sm.OLS(y[ok], X[ok]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(groups[ok])[0]})
    return r.params["x"], r.tvalues["x"], r.pvalues["x"], int(ok.sum())


def bh(p):
    p = np.asarray(p)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank, i in enumerate(order[::-1]):
        k = n - rank
        prev = min(prev, p[i] * n / k)
        q[i] = prev
    return q


def loss_test(base_err, model_err, dates):
    """Paired test of squared-error improvement, clustered by game date."""
    d = pd.Series(base_err ** 2 - model_err ** 2)
    by = d.groupby(np.asarray(dates)).sum()
    t = by.mean() / (by.std(ddof=1) / np.sqrt(len(by)))
    return 1 - (model_err ** 2).sum() / (base_err ** 2).sum(), t


def walk_forward(d, X, y, cols, kind="ridge", first_test=FIRST_TEST):
    """Expanding-window: fit on seasons < S, predict S.  Returns OOS prediction series
    (NaN outside test seasons) and the train-mean-only prediction."""
    pred = pd.Series(np.nan, index=d.index)
    base = pd.Series(np.nan, index=d.index)
    ok = X[cols].notna().all(axis=1) & y.notna()
    for S in sorted(d.season.unique()):
        if S < first_test:
            continue
        tr, te = ok & (d.season < S), ok & (d.season == S)
        if tr.sum() < 2000 or te.sum() == 0:
            continue
        mu, sd = X.loc[tr, cols].mean(), X.loc[tr, cols].std().replace(0, 1)
        Xtr, Xte = (X.loc[tr, cols] - mu) / sd, (X.loc[te, cols] - mu) / sd
        base[te] = y[tr].mean()
        if not cols:
            pred[te] = y[tr].mean()
        elif kind == "ridge":
            m = RidgeCV(alphas=np.logspace(0, 4, 13)).fit(Xtr, y[tr])
            pred[te] = m.predict(Xte)
        else:
            m = HistGradientBoostingRegressor(max_depth=3, learning_rate=0.04, max_iter=250,
                                              min_samples_leaf=300, l2_regularization=10.0,
                                              random_state=0).fit(Xtr, y[tr])
            pred[te] = m.predict(Xte)
    return pred, base


def bet_sim(signal, total, line, thresholds, season):
    rows = []
    for th in thresholds:
        over, under = signal >= th, signal <= -th
        res = np.where(over, np.sign(total - line), np.where(under, np.sign(line - total), np.nan))
        res = pd.Series(res, index=signal.index)
        w, l, p = (res == 1).sum(), (res == -1).sum(), (res == 0).sum()
        n = w + l
        if n == 0:
            continue
        wr = w / n
        z = (wr - BREAKEVEN) / np.sqrt(BREAKEVEN * (1 - BREAKEVEN) / n)
        z50 = (wr - 0.5) / np.sqrt(0.25 / n)
        roi = (w * (100 / 110) - l) / (n + p)
        by = pd.DataFrame({"r": res, "s": season}).dropna()
        by = by[by.r != 0].groupby("s").r.apply(lambda v: (v == 1).mean())
        rows.append({"threshold": th, "bets": n, "win%": 100 * wr, "ROI%@-110": 100 * roi,
                     "z_vs_52.4": z, "z_vs_50": z50, "seasons>52.4%": f"{(by > BREAKEVEN).sum()}/{len(by)}"})
    return pd.DataFrame(rows).set_index("threshold")


# ----------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    g = pd.read_parquet(os.path.join(ROOT, "data", "processed", "games.parquet"))
    g = g[g.pre_total.notna() & g.pre_poss_stored.notna()].reset_index(drop=True)   # 2015-16 onward
    F, fam = build_features(g)
    allf = [c for v in fam.values() for c in v]
    res = {}

    emit("# Torvik totals: generated results\n")
    emit(f"Games: {len(g):,} D1-vs-D1, seasons {g.season.min()}-{g.season.max()} "
         f"(frozen pregame total + stored pregame possessions). With a closing total: {g.close_total.notna().sum():,}.\n")

    # ---------------- 1. baseline
    emit("## 1. Baseline accuracy\n")
    c = g[g.close_total.notna()]
    t = c.groupby("season").apply(lambda d: pd.Series({
        "games": len(d),
        "torvik_bias": d.err_total.mean(), "close_bias": d.err_close.mean(),
        "torvik_MAE": d.err_total.abs().mean(), "close_MAE": d.err_close.abs().mean(),
        "retro_MAE(leaky)": (d.total - d.retro_total).abs().mean(),
        "corr(torvik,close)": d.pre_total.corr(d.close_total),
        "sd(torvik-close)": d.edge.std()}))
    allrow = pd.Series({"games": len(c), "torvik_bias": c.err_total.mean(), "close_bias": c.err_close.mean(),
                        "torvik_MAE": c.err_total.abs().mean(), "close_MAE": c.err_close.abs().mean(),
                        "retro_MAE(leaky)": (c.total - c.retro_total).abs().mean(),
                        "corr(torvik,close)": c.pre_total.corr(c.close_total), "sd(torvik-close)": c.edge.std()}, name="ALL")
    table(pd.concat([t, allrow.to_frame().T]))
    res["baseline"] = allrow.to_dict()

    emit("Error decomposition (all games): actual minus Torvik.\n")
    pace_part = 2 * g.pre_ppp * g.err_poss
    eff_part = 2 * g.pre_poss * g.err_ppp
    dec = pd.DataFrame({
        "mean": [g.err_total.mean(), g.err_poss.mean(), g.err_poss_40.mean(), g.err_ppp.mean()],
        "sd": [g.err_total.std(), g.err_poss.std(), g.err_poss_40.std(), g.err_ppp.std()],
        "MAE": [g.err_total.abs().mean(), g.err_poss.abs().mean(), g.err_poss_40.abs().mean(), g.err_ppp.abs().mean()]},
        index=["total (pts)", "possessions incl. OT", "possessions per 40", "points per possession"])
    table(dec)
    v = np.cov(pace_part.fillna(0), eff_part.fillna(0))
    emit(f"Variance of total error: pace part {v[0,0]:.0f} pts^2 ({100*v[0,0]/g.err_total.var():.0f}%), "
         f"efficiency part {v[1,1]:.0f} pts^2 ({100*v[1,1]/g.err_total.var():.0f}%), covariance x2 {2*v[0,1]:.0f}.\n")
    cal = sm.OLS(g.total, sm.add_constant(g.pre_total)).fit()
    calp = sm.OLS(g.poss_40, sm.add_constant(g.pre_poss)).fit()
    cc = g[g.close_total.notna()]
    calc = sm.OLS(cc.total, sm.add_constant(cc.close_total)).fit()
    emit(f"Calibration slope of the closing total: {calc.params.iloc[1]:.3f}.\n")
    res["calibration_slope_close"] = calc.params.iloc[1]
    emit(f"Calibration slope, actual total on Torvik total: {cal.params.iloc[1]:.3f} (1.0 = perfect); "
         f"actual per-40 possessions on projected: {calp.params.iloc[1]:.3f}. OT games: {100*(g.overtimes>0).mean():.1f}%.\n")
    res["calibration_slope_total"] = cal.params.iloc[1]
    res["calibration_slope_poss"] = calp.params.iloc[1]

    # ---------------- 2. in-sample screen
    emit("## 2. In-sample factor screen (season fixed effects, SEs clustered by date)\n")
    emit("Slope = change in error per +1 SD of the factor. `sign` = seasons whose own slope has the pooled sign. "
         "q = Benjamini-Hochberg across all tests in this table.\n")
    targets = {"total": g.err_total, "poss40": g.err_poss_40, "ppp_x100": 100 * g.err_ppp}
    rows = []
    for family, cols in fam.items():
        for col in cols:
            z = (F[col] - F[col].mean()) / F[col].std()
            row = {"family": family, "factor": col}
            for tn, y in targets.items():
                b, tval, p, n = clustered_slope(y, z, g.date, fe=g.season)
                per = []
                for S, idx in g.groupby("season").groups.items():
                    zz, yy = z.loc[idx], y.loc[idx]
                    ok = zz.notna() & yy.notna()
                    if ok.sum() > 500:
                        per.append(np.polyfit(zz[ok], yy[ok], 1)[0])
                per = np.array(per)
                row[f"{tn}_slope"], row[f"{tn}_t"], row[f"{tn}_p"] = b, tval, p
                row[f"{tn}_sign"] = f"{int((np.sign(per) == np.sign(b)).sum())}/{len(per)}"
            rows.append(row)
    scr = pd.DataFrame(rows)
    allp = np.concatenate([scr[f"{t}_p"].values for t in targets])
    q = bh(allp).reshape(len(targets), -1)
    for i, tn in enumerate(targets):
        scr[f"{tn}_q"] = q[i]
    show = scr[["family", "factor"] + [f"{t}_{k}" for t in targets for k in ("slope", "t", "sign")]].set_index("factor")
    table(show, "%.2f")
    emit(f"Tests with q<0.05: total {int((scr.total_q<0.05).sum())}/{len(scr)}, "
         f"poss40 {int((scr.poss40_q<0.05).sum())}/{len(scr)}, ppp {int((scr.ppp_x100_q<0.05).sum())}/{len(scr)}.\n")
    res["screen"] = scr.to_dict(orient="records")

    emit("### Quintile view of the strongest factor in each family (mean error by factor quintile)\n")
    for family, cols in fam.items():
        best = scr[scr.family == family].assign(m=lambda d: d.total_t.abs()).sort_values("m").factor.iloc[-1]
        qs = pd.qcut(F[best].rank(method="first"), 5, labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"])
        t = g.groupby(qs, observed=True).agg(n=("err_total", "size"), total_err=("err_total", "mean"),
                                             poss40_err=("err_poss_40", "mean"),
                                             ppp_err_x100=("err_ppp", lambda v: 100 * v.mean()),
                                             close_err=("err_close", "mean"))
        emit(f"**{family}: `{best}`**\n")
        table(t, "%.2f")

    # ---------------- 3. walk-forward OOS on Torvik's own error
    emit(f"## 3. Out-of-sample: predicting Torvik's error (train seasons < S, test S = {FIRST_TEST}..{g.season.max()})\n")
    emit("`R2_oos` is relative to a constant correction equal to the training-seasons mean error; "
         "`t` is a date-clustered paired test of squared-error improvement (t > 2 ~ significant); "
         "`seasons+` = test seasons with positive R2.\n")
    tgt = {"total": g.err_total, "poss40": g.err_poss_40, "ppp_x100": 100 * g.err_ppp}
    oos_rows, preds = [], {}
    sets = dict(fam)
    sets["ALL four families"] = allf
    for name, cols in sets.items():
        for kind in (("ridge", "gbm") if name == "ALL four families" else ("ridge",)):
            row = {"model": f"{name} ({kind})"}
            for tn, y in tgt.items():
                p, b = walk_forward(g, F, y, cols, kind)
                ok = p.notna() & b.notna() & y.notna()
                r2, tval = loss_test((y - b)[ok].values, (y - p)[ok].values, g.date[ok].values)
                per = [1 - ((y - p)[ok & (g.season == S)] ** 2).sum() / ((y - b)[ok & (g.season == S)] ** 2).sum()
                       for S in sorted(g.season[ok].unique())]
                row[f"{tn}_R2_oos%"] = 100 * r2
                row[f"{tn}_t"] = tval
                row[f"{tn}_corr"] = np.corrcoef(p[ok], y[ok])[0, 1]
                row[f"{tn}_seasons+"] = f"{sum(v > 0 for v in per)}/{len(per)}"
                preds[(name, kind, tn)] = p
                if tn == "total":
                    row["n"] = int(ok.sum())
            oos_rows.append(row)
    oos = pd.DataFrame(oos_rows).set_index("model")
    table(oos, "%.3f")
    res["oos_torvik_error"] = oos.reset_index().to_dict(orient="records")

    corr_all = preds[("ALL four families", "ridge", "total")]
    ok = corr_all.notna()
    emit(f"Size of the walk-forward correction (ALL, ridge): sd {corr_all[ok].std():.2f} pts, "
         f"95% of games within +/-{corr_all[ok].abs().quantile(0.95):.2f} pts. "
         f"Torvik MAE on test seasons {g.err_total[ok].abs().mean():.3f} -> corrected {(g.err_total - corr_all)[ok].abs().mean():.3f}.\n")
    res["correction_sd"] = corr_all[ok].std()

    # ---------------- 4. market test
    emit("## 4. Market test (games with a closing total, test seasons only)\n")
    m = g[g.close_total.notna() & corr_all.notna()].copy()
    m["corr_all"] = corr_all[m.index]
    m["corr_gbm"] = preds[("ALL four families", "gbm", "total")][m.index]
    m["adj_total"] = m.pre_total + m.corr_all
    emit(f"Games: {len(m):,}.\n")
    acc = pd.DataFrame({
        "MAE": [m.err_total.abs().mean(), (m.total - m.adj_total).abs().mean(), m.err_close.abs().mean(),
                (m.total - (0.5 * m.adj_total + 0.5 * m.close_total)).abs().mean()],
        "RMSE": [np.sqrt((m.err_total ** 2).mean()), np.sqrt(((m.total - m.adj_total) ** 2).mean()),
                 np.sqrt((m.err_close ** 2).mean()),
                 np.sqrt(((m.total - (0.5 * m.adj_total + 0.5 * m.close_total)) ** 2).mean())]},
        index=["Torvik frozen", "Torvik + factor correction", "Closing total", "50/50 blend corrected+close"])
    table(acc)
    res["market_accuracy"] = acc.reset_index().to_dict(orient="records")

    emit("Regressions of (actual - close), SEs clustered by date. A market-efficient close gives slope 0.\n")
    regs = []
    for label, xcols in (("Torvik edge (torvik - close)", ["edge"]),
                         ("factor correction only", ["corr_all"]),
                         ("edge + factor correction", ["edge", "corr_all"])):
        X = sm.add_constant(m[xcols])
        r = sm.OLS(m.err_close, X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(m.date)[0]})
        for x in xcols:
            regs.append({"regression": label, "term": x, "slope": r.params[x], "t": r.tvalues[x], "p": r.pvalues[x],
                         "R2%": 100 * r.rsquared})
    table(pd.DataFrame(regs).set_index("regression"))
    res["market_regressions"] = regs

    emit("Encompassing regression: actual = a + b1*Torvik + b2*close (b1 > 0 means Torvik adds information to the close).\n")
    r = sm.OLS(m.total, sm.add_constant(m[["pre_total", "close_total"]])).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(m.date)[0]})
    r2 = sm.OLS(m.total, sm.add_constant(m[["adj_total", "close_total"]])).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(m.date)[0]})
    enc = pd.DataFrame({"b_torvik": [r.params.iloc[1], r2.params.iloc[1]], "t_torvik": [r.tvalues.iloc[1], r2.tvalues.iloc[1]],
                        "b_close": [r.params.iloc[2], r2.params.iloc[2]], "t_close": [r.tvalues.iloc[2], r2.tvalues.iloc[2]]},
                       index=["Torvik frozen", "Torvik + factor correction"])
    table(enc)
    res["encompassing"] = enc.reset_index().to_dict(orient="records")

    emit("### Walk-forward model of the MARKET error (actual - close) from the factors\n")
    gm = g[g.close_total.notna()].copy()
    Fm = F.loc[gm.index].copy()
    Fm["edge"] = gm.edge
    mk_rows, mk_pred = [], {}
    msets = {"edge only": ["edge"], **{k: v for k, v in fam.items()}, "ALL four families": allf,
             "ALL + edge": allf + ["edge"]}
    for name, cols in msets.items():
        for kind in (("ridge", "gbm") if name.startswith("ALL") else ("ridge",)):
            p, b = walk_forward(gm, Fm, gm.err_close, cols, kind)
            ok = p.notna() & b.notna()
            r2v, tval = loss_test((gm.err_close - b)[ok].values, (gm.err_close - p)[ok].values, gm.date[ok].values)
            per = [1 - ((gm.err_close - p)[ok & (gm.season == S)] ** 2).sum() /
                   ((gm.err_close - b)[ok & (gm.season == S)] ** 2).sum() for S in sorted(gm.season[ok].unique())]
            mk_rows.append({"model": f"{name} ({kind})", "n": int(ok.sum()), "R2_oos%": 100 * r2v, "t": tval,
                            "corr": np.corrcoef(p[ok], gm.err_close[ok])[0, 1], "pred_sd": p[ok].std(),
                            "seasons+": f"{sum(v > 0 for v in per)}/{len(per)}"})
            mk_pred[(name, kind)] = p - b      # centred: bet on the deviation from the historical mean error
    mk = pd.DataFrame(mk_rows).set_index("model")
    table(mk)
    res["oos_market_error"] = mk.reset_index().to_dict(orient="records")

    emit("### Betting simulation at -110 (break-even 52.38%), test seasons, closing totals\n")
    emit("Bet OVER when signal >= threshold, UNDER when <= -threshold. Pushes excluded from win%.\n")
    t_ = gm[gm.season >= FIRST_TEST]
    nz = t_.total != t_.close_total
    emit(f"Reference: betting every OVER wins {100*(t_.total > t_.close_total)[nz].mean():.2f}% (n={int(nz.sum()):,}). "
         f"The mean of actual-close is {t_.err_close.mean():+.2f} but the median is {t_.err_close.median():+.2f} (overtime skew), "
         "so the direct market models E-G bet on the prediction minus the training-seasons mean.\n")
    sims = {
        "A. Raw Torvik edge (torvik - close)": (m.edge, m, [1, 2, 3, 4, 5, 6]),
        "B. Corrected Torvik edge (torvik + factor correction - close)": (m.adj_total - m.close_total, m, [1, 2, 3, 4, 5, 6]),
        "C. Factor correction alone, ridge (ignores Torvik-vs-close gap)": (m.corr_all, m, [0.5, 1, 1.5, 2]),
        "D. Factor correction alone, GBM": (m.corr_gbm, m, [0.5, 1, 1.5, 2]),
    }
    pm = mk_pred[("ALL + edge", "ridge")]
    okm = pm.notna()
    sims["E. Direct market-error model (ALL + edge, ridge)"] = (pm[okm], gm[okm], [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5])
    pg = mk_pred[("ALL + edge", "gbm")]
    okg = pg.notna()
    sims["F. Direct market-error model (ALL + edge, GBM)"] = (pg[okg], gm[okg], [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5])
    pf = mk_pred[("ALL four families", "ridge")]
    okf = pf.notna()
    sims["G. Direct market-error model (factors only, ridge)"] = (pf[okf], gm[okf], [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5])
    res["bets"] = {}
    for label, (sig, d, ths) in sims.items():
        emit(f"**{label}**\n")
        t = bet_sim(sig, d.total, d.close_total, ths, d.season)
        table(t, "%.2f")
        res["bets"][label] = t.reset_index().to_dict(orient="records")

    emit("### Robustness of the direct factors-only market model (G)\n")
    sig, d = pf[okf], gm[okf]
    rows = []
    for S in sorted(d.season.unique()):
        k = d.season == S
        row = {"season": S, "line_source": d.close_source[k].mode().iloc[0], "corr(pred, actual-close)": np.corrcoef(sig[k], d.err_close[k])[0, 1]}
        for th in (1.0, 1.5):
            b = bet_sim(sig[k], d.total[k], d.close_total[k], [th], d.season[k])
            row[f"bets@{th}"] = int(b.bets.iloc[0]) if len(b) else 0
            row[f"win%@{th}"] = b["win%"].iloc[0] if len(b) else np.nan
        rows.append(row)
    table(pd.DataFrame(rows).set_index("season"), "%.2f")
    op = d.espn_open.notna()
    if op.sum() > 1000:
        emit(f"Same signal settled against the OPENING total instead (seasons with an opening line, n={int(op.sum()):,}; "
             "note the model was trained on closing-line errors):\n")
        table(bet_sim(sig[op], d.total[op], d.espn_open[op], [0.5, 1.0, 1.5, 2.0], d.season[op]), "%.2f")
        emit("...and against the close on the identical games:\n")
        table(bet_sim(sig[op], d.total[op], d.close_total[op], [0.5, 1.0, 1.5, 2.0], d.season[op]), "%.2f")
        mv = (d.close_total - d.espn_open)[op]
        emit(f"Line movement open->close on those games: corr with the signal {np.corrcoef(sig[op], mv)[0,1]:.3f}; "
             f"corr with raw Torvik edge vs open {np.corrcoef((d.pre_total - d.espn_open)[op], mv)[0,1]:.3f}.\n")
    k = d.overtimes == 0
    emit("Regulation-only games (drops overtime luck):\n")
    table(bet_sim(sig[k], d.total[k], d.close_total[k], [0.5, 1.0, 1.5, 2.0], d.season[k]), "%.2f")
    under, over = sig <= -1.0, sig >= 1.0
    emit(f"Direction split at threshold 1.0: overs {int(over.sum()):,} bets, "
         f"{100*((d.total>d.close_total)[over].sum()/((d.total!=d.close_total)[over].sum())):.2f}% win; "
         f"unders {int(under.sum()):,} bets, {100*((d.total<d.close_total)[under].sum()/((d.total!=d.close_total)[under].sum())):.2f}% win.\n")

    emit("### Single-factor market check\n")
    emit("Slope of (actual - close) per +1 SD of each factor, season fixed effects, clustered by date, all seasons with odds.\n")
    rows = []
    for family, cols in fam.items():
        for col in cols:
            z = (F[col] - F[col].mean()) / F[col].std()
            b, tval, p, n = clustered_slope(gm.err_close, z.loc[gm.index], gm.date, fe=gm.season)
            # split-half replication: 2016-2020 vs 2021-2026
            h1, h2 = gm.season <= 2020, gm.season > 2020
            b1, t1, _, _ = clustered_slope(gm.err_close[h1], z.loc[gm.index][h1], gm.date[h1], fe=gm.season[h1])
            b2, t2, _, _ = clustered_slope(gm.err_close[h2], z.loc[gm.index][h2], gm.date[h2], fe=gm.season[h2])
            rows.append({"family": family, "factor": col, "slope": b, "t": tval, "p": p,
                         "slope_2016_20": b1, "t_2016_20": t1, "slope_2021_26": b2, "t_2021_26": t2})
    sf = pd.DataFrame(rows)
    sf["q"] = bh(sf.p.values)
    table(sf.set_index("factor"), "%.2f")
    emit(f"Factors with q<0.05 against the close: {int((sf.q < 0.05).sum())}/{len(sf)}; "
         f"with |t|>2 in BOTH halves and the same sign: "
         f"{int(((sf.t_2016_20.abs() > 2) & (sf.t_2021_26.abs() > 2) & (np.sign(sf.slope_2016_20) == np.sign(sf.slope_2021_26))).sum())}/{len(sf)}.\n")
    res["single_factor_market"] = sf.to_dict(orient="records")

    open(os.path.join(OUT, "results.md"), "w").write("\n".join(md) + "\n")
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
