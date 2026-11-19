"""Phase-2 exploratory experiments.  Writes reports/phase2_results.md (+ .json).

Protocol
  * Market targets: err_close = actual - close, err_open = actual - open, move = close - open.
  * "OOS signal" = the phase-1 factors-only ridge, refit walk-forward (train seasons < S), centred.
    It is out of sample for 2019..2026.  (The frozen v1 model is fit on everything through 2026 and is
    therefore only testable on 2026-27; see src/forward_eval.py.)
  * New single-factor hypotheses: DISCOVERY = seasons 2016..2022, VALIDATION = 2023..2026.
    Every new test is run once and listed in one table with Benjamini-Hochberg q-values on discovery.
    "Replicates" = discovery q < 0.10 AND validation same sign with |t| >= 2.
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import analyze as A            # noqa: E402
import build_dataset as B      # noqa: E402

OUT = os.path.join(ROOT, "reports")
BE = 110 / 210
DISC_END = 2022
EIGHT = ["opp_foul", "opp_ftr", "opp_blk", "opp_stl", "opp_3p_pct", "shot_ftr", "shot_orb", "pace_slow_side"]
md, RES, HYP, HX = [], {}, [], {}


def emit(s=""):
    print(s)
    md.append(s)


def table(df, fmt=".2f", index=True):
    emit(df.to_markdown(floatfmt=fmt, index=index))
    emit()


def wilson(w, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = w / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def payout(american):
    a = np.asarray(american, dtype=float)
    return np.where(a > 0, a / 100.0, 100.0 / np.abs(a))


def bets(sig, total, line, th, over_odds=None, under_odds=None, season=None):
    """Bet OVER if sig >= th, UNDER if sig <= -th at `line`.  Prices default to -110."""
    side = np.where(sig >= th, 1, np.where(sig <= -th, -1, 0))
    k = (side != 0) & pd.notna(line) & pd.notna(sig)
    res = np.sign((np.asarray(total) - np.asarray(line)) * side)
    pay = np.full(len(side), 100 / 110) if over_odds is None else np.where(side == 1, payout(over_odds), payout(under_odds))
    k = k & ~np.isnan(pay)
    w, l, p = int(((res == 1) & k).sum()), int(((res == -1) & k).sum()), int(((res == 0) & k).sum())
    n = w + l
    if n == 0:
        return {"bets": 0}
    profit = np.where(res == 1, pay, np.where(res == -1, -1.0, 0.0))[k]
    lo, hi = wilson(w, n)
    roi = profit.mean()
    se = profit.std(ddof=1) / np.sqrt(len(profit))
    out = {"bets": n, "win%": 100 * w / n, "ci_lo": lo, "ci_hi": hi, "ROI%": 100 * roi,
           "ROI_lo": 100 * (roi - 1.96 * se), "ROI_hi": 100 * (roi + 1.96 * se)}
    if season is not None:
        s = pd.DataFrame({"r": res[k], "s": np.asarray(season)[k]})
        s = s[s.r != 0].groupby("s").r.apply(lambda v: (v == 1).mean())
        out["seasons>BE"] = f"{int((s > BE).sum())}/{len(s)}"
    return out


def slope(y, x, d, fe=True):
    ok = y.notna() & x.notna()
    if ok.sum() < 300 or x[ok].std() == 0:
        return np.nan, np.nan, np.nan, int(ok.sum())
    b, t, p, n = A.clustered_slope(y[ok], x[ok], d.date[ok], fe=d.season[ok] if fe else None)
    return b, t, p, n


def hyp(family, name, x, g, standardize=True, note=""):
    """Register one new hypothesis: discovery / validation slopes against close and open errors."""
    x = pd.Series(x, index=g.index).astype(float)
    HX[name] = x.copy()
    unit = "per SD"
    if standardize:
        x = (x - x.mean()) / x.std()
    else:
        unit = "0/1"
    dz, vz = g.season <= DISC_END, g.season > DISC_END
    r = {"family": family, "hypothesis": name, "unit": unit, "note": note}
    for tag, m in (("disc", dz), ("valid", vz)):
        b, t, p, n = slope(g.err_close[m], x[m], g[m])
        r[f"{tag}_n"], r[f"{tag}_slope"], r[f"{tag}_t"], r[f"{tag}_p"] = n, b, t, p
    b, t, p, n = slope(g.err_open, x, g)
    r["open_n"], r["open_slope"], r["open_t"] = n, b, t
    b, t, p, n = slope(g.move, x, g)
    r["move_slope"], r["move_t"] = b, t
    HYP.append(r)
    return r


def main():
    os.makedirs(OUT, exist_ok=True)
    g = pd.read_parquet(os.path.join(ROOT, "data", "processed", "games.parquet"))
    p2 = pd.read_parquet(os.path.join(ROOT, "data", "processed", "p2_games.parquet"))
    books = pd.read_parquet(os.path.join(ROOT, "data", "processed", "odds_books.parquet"))
    g = g.merge(p2.drop(columns=["espn_id"]), on=["season", "muid"], how="left")
    g = g[g.pre_total.notna() & g.pre_poss_stored.notna()].reset_index(drop=True)
    F, fam = A.build_features(g)
    allf = [c for v in fam.values() for c in v]
    g["err_open"] = g.total - g.open_total
    g["move"] = g.close_total - g.open_total
    g.loc[g.move.abs() > 15, ["move", "err_open", "open_total"]] = np.nan      # bad open rows
    has_c = g.close_total.notna()

    # walk-forward OOS signal (factors only, trained on closing-line error)
    gm = g[has_c]
    p, b = A.walk_forward(gm, F.loc[gm.index], gm.err_close, allf, "ridge")
    g["sig"] = (p - b).reindex(g.index)
    # same factors trained on OPENING-line error (seasons with an opener)
    go = g[g.err_open.notna()]
    po, bo = A.walk_forward(go, F.loc[go.index], go.err_open, allf, "ridge")
    g["sig_open_model"] = (po - bo).reindex(g.index)
    # 8-factor only
    p8, b8 = A.walk_forward(gm, F.loc[gm.index], gm.err_close, EIGHT, "ridge")
    g["sig8"] = (p8 - b8).reindex(g.index)

    emit("# Phase 2: generated results\n")
    emit(f"Games 2015-16..2025-26: {len(g):,}; with close {int(has_c.sum()):,}; with an opening total "
         f"{int(g.open_total.notna().sum()):,} (SBR 2016-21, ESPN per-book 2024-26; none for 2022-23).\n")

    # =========================================================== 1. OPEN vs CLOSE
    emit("## 1. Opening vs closing totals\n")
    o = g[g.open_total.notna() & has_c].copy()
    t = o.groupby("season").apply(lambda d: pd.Series({
        "games": len(d), "open_MAE": d.err_open.abs().mean(), "close_MAE": d.err_close.abs().mean(),
        "mean|move|": d.move.abs().mean(), "moved>=1": 100 * (d.move.abs() >= 1).mean(),
        "moved>=2": 100 * (d.move.abs() >= 2).mean(), "moved>=3": 100 * (d.move.abs() >= 3).mean(),
        "corr(move, actual-open)": d.move.corr(d.err_open), "source": d.open_source.mode().iloc[0]}))
    table(t)
    RES["open_close_by_season"] = t.reset_index().to_dict(orient="records")
    r = sm.OLS(o.err_open, sm.add_constant(o.move)).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(o.date)[0]})
    emit(f"Regression actual-open on move: slope {r.params['move']:.3f} (t={r.tvalues['move']:.1f}). "
         "Slope 1 = the move is fully informative and the opener was simply stale by that amount.\n")
    RES["move_slope"] = r.params["move"]

    emit("### 1a. Betting WITH the eventual move (not executable - it uses the close - but it sizes the prize)\n")
    rows = []
    for th in (1, 2, 3):
        x = bets(o.move, o.total, o.open_total, th, season=o.season)
        rows.append({"bet open when |close-open| >=": th, **x})
    table(pd.DataFrame(rows), index=False)

    emit("### 1b. OOS factor signal: opening vs closing line, identical games\n")
    oo = o[o.sig.notna()]
    rows = []
    for th in (1.0, 1.5, 2.0):
        for nm, line in (("open", oo.open_total), ("close", oo.close_total)):
            rows.append({"threshold": th, "line": nm, **bets(oo.sig, oo.total, line, th, season=oo.season)})
    table(pd.DataFrame(rows), index=False)
    RES["signal_open_vs_close"] = rows
    emit("By season at threshold 1.5:\n")
    rows = []
    for S, d in oo.groupby("season"):
        a, c = bets(d.sig, d.total, d.open_total, 1.5), bets(d.sig, d.total, d.close_total, 1.5)
        mv = d.move[(d.sig.abs() >= 1.5)] * np.sign(d.sig[(d.sig.abs() >= 1.5)])
        rows.append({"season": S, "open_source": d.open_source.mode().iloc[0], "bets": a.get("bets"), "open_win%": a.get("win%"),
                     "close_win%": c.get("win%"), "avg CLV pts (move toward bet)": mv.mean(),
                     "% bets line moved toward": 100 * (mv > 0).mean(), "% moved against": 100 * (mv < 0).mean(),
                     "corr(sig, move)": d.sig.corr(d.move)})
    table(pd.DataFrame(rows), index=False)
    RES["signal_by_season_open"] = rows

    emit("### 1c. Does anything predict the open-to-close move?\n")
    rows = []
    for nm, x in (("OOS factor signal (trained on close)", oo.sig), ("OOS factor signal (trained on open)", oo.sig_open_model),
                  ("Torvik frozen total - open", oo.pre_total - oo.open_total)):
        ok = x.notna()
        for tgt, y in (("move", oo.move), ("actual-open", oo.err_open), ("actual-close", oo.err_close)):
            rr = sm.OLS(y[ok], sm.add_constant(x[ok].rename("x"))).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(oo.date[ok])[0]})
            rows.append({"predictor": nm, "target": tgt, "n": int(ok.sum()), "slope": rr.params["x"], "t": rr.tvalues["x"],
                         "corr": np.corrcoef(x[ok], y[ok])[0, 1]})
    table(pd.DataFrame(rows), ".3f", index=False)
    RES["move_predictors"] = rows

    emit("### 1d. Direct projection vs market-error model, against the OPENER\n")
    emit("Torvik's frozen total is the only independent pregame projection in hand. Bet the opener when Torvik disagrees by the threshold. "
         "Caveat: Torvik's number is timestamped only to the game day, the opener is not timestamped at all, so it is unknown which existed first.\n")
    oa = o.copy()
    rows = []
    for th in (2, 3, 4, 5):
        rows.append({"model": "Torvik - open", "threshold": th, **bets(oa.pre_total - oa.open_total, oa.total, oa.open_total, th, season=oa.season)})
    for th in (1.0, 1.5):
        rows.append({"model": "factor signal, trained on close", "threshold": th, **bets(oo.sig, oo.total, oo.open_total, th, season=oo.season)})
        k = oo.sig_open_model.notna()
        rows.append({"model": "factor signal, trained on open", "threshold": th,
                     **bets(oo.sig_open_model[k], oo.total[k], oo.open_total[k], th, season=oo.season[k])})
    # agreement: Torvik and factor signal on the same side
    both = oo[(np.sign(oo.pre_total - oo.open_total) == np.sign(oo.sig)) & ((oo.pre_total - oo.open_total).abs() >= 2)]
    rows.append({"model": "Torvik-open >= 2 AND factor signal same side >= 1", "threshold": 1.0,
                 **bets(both.sig, both.total, both.open_total, 1.0, season=both.season)})
    table(pd.DataFrame(rows), index=False)
    RES["direct_vs_market_model_open"] = rows
    emit("Torvik-vs-open by season (threshold 3):\n")
    rows = []
    for S, d in oa.groupby("season"):
        e = d.pre_total - d.open_total
        x = bets(e, d.total, d.open_total, 3)
        mv = (d.move * np.sign(e))[e.abs() >= 3]
        rows.append({"season": S, "bets": x.get("bets"), "win%": x.get("win%"), "avg CLV pts": mv.mean(), "corr(edge, move)": e.corr(d.move)})
    table(pd.DataFrame(rows), index=False)

    emit("### 1e. Which games move most between open and close?\n")
    X = pd.DataFrame({
        "|Torvik - open| (per pt)": (o.pre_total - o.open_total).abs(),
        "games played, min of two teams (per 10)": np.minimum(o.t1_s_gp, o.t2_s_gp) / 10,
        "both teams non-major": (o.majors == 0).astype(float),
        "both teams major": (o.majors == 2).astype(float),
        "neutral site": o.neutral.astype(float),
        "market spread (per 10 pts)": o.mkt_spread_abs / 10,
        "open total level (per 10 pts)": (o.open_total - 140) / 10,
        "roster turnover, avg of two teams (per 0.1)": (1 - o[["t1_ret_min", "t2_ret_min"]].mean(axis=1)) * 10,
        "|OOS factor signal| (per pt)": o.sig.abs(),
    })
    ok = X.drop(columns=["|OOS factor signal| (per pt)"]).notna().all(axis=1)
    Xa = pd.concat([X[ok].drop(columns=["|OOS factor signal| (per pt)"]), pd.get_dummies(o.season[ok], prefix="s", dtype=float)], axis=1)
    rr = sm.OLS(o.move.abs()[ok], Xa).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(o.date[ok])[0]})
    tt = pd.DataFrame({"effect on |move| (pts)": rr.params, "t": rr.tvalues}).loc[[c for c in X.columns if c in rr.params.index]]
    table(tt, ".3f")
    emit(f"Mean |move| {o.move.abs().mean():.2f}; n={int(ok.sum()):,}; season fixed effects.\n")
    gpb = pd.cut(np.minimum(o.t1_s_gp, o.t2_s_gp), [-1, 2, 5, 10, 20, 50], labels=["0-2", "3-5", "6-10", "11-20", "21+"])
    tt = o.groupby(gpb, observed=True).apply(lambda d: pd.Series({
        "games": len(d), "mean|move|": d.move.abs().mean(), "open_MAE": d.err_open.abs().mean(), "close_MAE": d.err_close.abs().mean(),
        "MAE gain open->close": d.err_open.abs().mean() - d.err_close.abs().mean()}))
    emit("By games already played (the less-experienced of the two teams):\n")
    table(tt)

    emit("### 1f. Do the factors matter at different stages?\n")
    emit("Slope per +1 SD, season fixed effects, date-clustered; games with both open and close.\n")
    rows = []
    for col in allf:
        z = (F[col] - F[col].mean()) / F[col].std()
        zo = z.loc[o.index]
        bo_, to_, _, _ = slope(o.err_open, zo, o)
        bc_, tc_, _, _ = slope(o.err_close, zo, o)
        bm_, tm_, _, n_ = slope(o.move, zo, o)
        rows.append({"factor": col, "eight": "*" if col in EIGHT else "", "vs open": bo_, "t_open": to_, "vs close": bc_, "t_close": tc_,
                     "move": bm_, "t_move": tm_, "share of open error corrected by close": (bm_ / bo_) if abs(to_) > 2 else np.nan})
    st = pd.DataFrame(rows)
    table(st[(st.t_open.abs() > 2) | (st.t_close.abs() > 2) | (st.t_move.abs() > 2)], index=False)
    RES["factor_stages"] = rows

    emit("### 1g. Sportsbook-level openers and line shopping (2023-24 only: the one season with per-book open AND close with prices)\n")
    b24 = books[(books.season == 2024) & books.open_total.notna() & (books.book.str.lower() != "consensus")].merge(
        g[["season", "espn_id", "total", "sig", "close_total", "date"]], on=["season", "espn_id"])
    rows = []
    for bk, d in b24.groupby("book"):
        if len(d) < 2000:
            continue
        mv = d.total_x - d.open_total if "total_x" in d else None
        x15 = bets(d.sig, d.total_y, d.open_total, 1.5, d.open_over, d.open_under)
        xc = bets(d.sig, d.total_y, d.total_x, 1.5, d.over_odds, d.under_odds)
        rows.append({"book": bk, "games": len(d), "open_MAE": (d.total_y - d.open_total).abs().mean(),
                     "close_MAE": (d.total_y - d.total_x).abs().mean(), "mean|move|": (d.total_x - d.open_total).abs().mean(),
                     "open - median open (mean abs)": np.nan,
                     "sig bets@open": x15.get("bets"), "win%@open": x15.get("win%"), "ROI%@open (actual price)": x15.get("ROI%"),
                     "win%@close": xc.get("win%"), "ROI%@close (actual price)": xc.get("ROI%"),
                     "avg hold% at open": float(np.nanmean(100 * (1 / (1 + payout(d.open_over)) + 1 / (1 + payout(d.open_under)) - 1)))})
    bt = pd.DataFrame(rows).drop(columns=["open - median open (mean abs)"])
    table(bt, index=False)
    RES["books_2024"] = rows
    # best-of-books
    def best(d, col, oc, uc, side):
        d = d.dropna(subset=[col])
        if side == 1:      # over: lowest total, then best over price
            d = d.sort_values([col, oc], ascending=[True, False])
        else:
            d = d.sort_values([col, uc], ascending=[False, False])
        return d.iloc[0]
    rows = []
    for label, src, col, oc, uc in (("2023-24 openers (10 books)", b24, "open_total", "open_over", "open_under"),
                                    ("2023-24 closes (10 books)", b24, "total_x", "over_odds", "under_odds")):
        s = src[src.sig.abs() >= 1.5]
        rec = []
        for eid, d in s.groupby("espn_id"):
            side = 1 if d.sig.iloc[0] > 0 else -1
            bb = best(d, col, oc, uc, side)
            med = d[col].median()
            rec.append({"sig": d.sig.iloc[0], "total": d.total_y.iloc[0], "best_line": bb[col], "best_over": bb[oc], "best_under": bb[uc],
                        "med_line": med, "gain": (med - bb[col]) * side, "n_books": d[col].notna().sum()})
        rec = pd.DataFrame(rec)
        xb = bets(rec.sig, rec.total, rec.best_line, 1.5, rec.best_over, rec.best_under)
        xm = bets(rec.sig, rec.total, rec.med_line, 1.5)
        rows.append({"set": label, "bets": xb.get("bets"), "median-line win% (-110)": xm.get("win%"), "median ROI%": xm.get("ROI%"),
                     "best-line win%": xb.get("win%"), "best-line ROI% (actual price)": xb.get("ROI%"),
                     "ROI_lo": xb.get("ROI_lo"), "ROI_hi": xb.get("ROI_hi"),
                     "avg pts gained by shopping": rec.gain.mean(), "% games best != median": 100 * (rec.gain > 0).mean()})
    # multi-book closes in other seasons (last quoted number, -110 assumed where no price)
    for S in (2022, 2023):
        bs = books[(books.season == S) & (books.book.str.lower() != "consensus")].merge(
            g[["season", "espn_id", "total", "sig"]], on=["season", "espn_id"])
        s = bs[bs.sig.abs() >= 1.5]
        rec = []
        for eid, d in s.groupby("espn_id"):
            side = 1 if d.sig.iloc[0] > 0 else -1
            bb = best(d, "total_x", "over_odds", "under_odds", side)
            med = d.total_x.median()
            rec.append({"sig": d.sig.iloc[0], "total": d.total_y.iloc[0], "best_line": bb.total_x, "best_over": bb.over_odds,
                        "best_under": bb.under_odds, "med_line": med, "gain": (med - bb.total_x) * side})
        rec = pd.DataFrame(rec)
        xb = bets(rec.sig, rec.total, rec.best_line, 1.5, rec.best_over, rec.best_under)
        xm = bets(rec.sig, rec.total, rec.med_line, 1.5)
        rows.append({"set": f"{S-1}-{str(S)[2:]} last quoted numbers (~10 books)", "bets": xb.get("bets"), "median-line win% (-110)": xm.get("win%"),
                     "median ROI%": xm.get("ROI%"), "best-line win%": xb.get("win%"), "best-line ROI% (actual price)": xb.get("ROI%"),
                     "ROI_lo": xb.get("ROI_lo"), "ROI_hi": xb.get("ROI_hi"),
                     "avg pts gained by shopping": rec.gain.mean(), "% games best != median": 100 * (rec.gain > 0).mean()})
    table(pd.DataFrame(rows), index=False)
    RES["line_shopping"] = rows
    emit("Best-line rows are an UPPER BOUND: the per-book numbers are not timestamped, so the best one may not have been "
         "available at the same moment as the others (most true for openers, which post hours apart).\n")

    emit("### 1h. Actual prices instead of a flat -110 (DraftKings open/close, 2024-25 and 2025-26)\n")
    dk = books[(books.season >= 2025) & (books.book == "DraftKings")].merge(g[["season", "espn_id", "total", "sig"]], on=["season", "espn_id"])
    rows = []
    for th in (1.0, 1.5, 2.0):
        a = bets(dk.sig, dk.total_y, dk.open_total, th, dk.open_over, dk.open_under, season=dk.season)
        a0 = bets(dk.sig, dk.total_y, dk.open_total, th)
        c = bets(dk.sig, dk.total_y, dk.total_x, th, dk.over_odds, dk.under_odds, season=dk.season)
        c0 = bets(dk.sig, dk.total_y, dk.total_x, th)
        rows.append({"threshold": th, "bets": a.get("bets"), "open win%": a.get("win%"), "open ROI% actual": a.get("ROI%"),
                     "open ROI% if -110": a0.get("ROI%"), "close win%": c.get("win%"), "close ROI% actual": c.get("ROI%"),
                     "close ROI% if -110": c0.get("ROI%")})
    table(pd.DataFrame(rows), index=False)
    hold = 100 * (1 / (1 + payout(dk.over_odds)) + 1 / (1 + payout(dk.under_odds)) - 1)
    hold_o = 100 * (1 / (1 + payout(dk.open_over)) + 1 / (1 + payout(dk.open_under)) - 1)
    emit(f"DraftKings average hold on totals: open {np.nanmean(hold_o):.2f}%, close {np.nanmean(hold):.2f}% (-110/-110 = 4.76%).\n")
    RES["dk_actual_prices"] = rows

    # =========================================================== 2. THE EIGHT FACTORS
    emit("## 2. The eight stable factors\n")
    Z = (F[EIGHT] - F[EIGHT].mean()) / F[EIGHT].std()
    emit("### 2a. Overlap: correlation matrix\n")
    table(Z.corr(), ".2f")
    ev = np.linalg.eigvalsh(Z.dropna().corr().values)[::-1]
    emit(f"Principal components: variance shares {', '.join(f'{100*v/8:.0f}%' for v in ev)}. "
         f"Effective number of independent factors (participation ratio): {(ev.sum()**2)/(ev**2).sum():.1f} of 8.\n")
    emit("### 2b. One at a time vs all together (actual - close, per +1 SD, season FE, date-clustered)\n")
    c = g[has_c]
    Xj = pd.concat([Z.loc[c.index], pd.get_dummies(c.season, prefix="s", dtype=float)], axis=1)
    ok = Xj.notna().all(axis=1)
    rj = sm.OLS(c.err_close[ok], Xj[ok]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(c.date[ok])[0]})
    ctrl = pd.DataFrame({"close_lvl": (c.close_total - 140) / 10, "spread": c.mkt_spread_abs / 10, "torvik_edge": c.edge})
    Xc = pd.concat([Xj, ctrl], axis=1)
    okc = Xc.notna().all(axis=1)
    rc = sm.OLS(c.err_close[okc], Xc[okc]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(c.date[okc])[0]})
    rows = []
    for col in EIGHT:
        b_, t_, p_, n_ = slope(c.err_close, Z.loc[c.index, col], c)
        se = b_ / t_
        per = []
        for S, d in c.groupby("season"):
            bb, _, _, _ = slope(d.err_close, Z.loc[d.index, col], d, fe=False)
            per.append(bb)
        per = np.array(per)
        bo_, to_, _, no_ = slope(g.err_open, Z[col], g)
        early, late = c.day_of_season < 60, c.day_of_season >= 60
        be_, te_, _, _ = slope(c.err_close[early], Z.loc[c.index, col][early], c[early])
        bl_, tl_, _, _ = slope(c.err_close[late], Z.loc[c.index, col][late], c[late])
        tier = {}
        for nm, m in (("both major", c.majors == 2), ("mixed", c.majors == 1), ("neither major", c.majors == 0)):
            tb, tt_, _, tn = slope(c.err_close[m], Z.loc[c.index, col][m], c[m])
            tier[nm] = f"{tb:+.2f} ({tt_:.1f})"
        rows.append({"factor": col, "alone": b_, "95% CI": f"[{b_-1.96*se:+.2f}, {b_+1.96*se:+.2f}]", "t": t_,
                     "seasons same sign": f"{int((np.sign(per) == np.sign(b_)).sum())}/{len(per)}",
                     "joint (8 together)": rj.params[col], "t_joint": rj.tvalues[col],
                     "joint + market controls": rc.params[col], "t_ctrl": rc.tvalues[col],
                     "vs open": bo_, "t_open": to_, "before Jan (t)": f"{be_:+.2f} ({te_:.1f})", "Jan on (t)": f"{bl_:+.2f} ({tl_:.1f})", **tier})
    e8 = pd.DataFrame(rows)
    table(e8[["factor", "alone", "95% CI", "t", "seasons same sign", "joint (8 together)", "t_joint", "joint + market controls", "t_ctrl"]], index=False)
    emit(f"n = {int(ok.sum()):,} games with a close. Market controls: closing total level, market spread, Torvik-minus-close.\n")
    emit("### 2c. Stage, calendar and conference tier\n")
    table(e8[["factor", "vs open", "t_open", "before Jan (t)", "Jan on (t)", "both major", "mixed", "neither major"]], index=False)
    RES["eight"] = rows

    emit("### 2d. Does opponent adjustment help?\n")
    adj = opponent_adjusted(g)
    rows = []
    for col, (raw_col, adj_col) in adj["pairs"].items():
        zr = adj["frame"][raw_col]
        za = adj["frame"][adj_col]
        zr, za = (zr - zr.mean()) / zr.std(), (za - za.mean()) / za.std()
        br, tr, _, n1 = slope(c.err_close, zr.loc[c.index], c)
        ba, ta, _, n2 = slope(c.err_close, za.loc[c.index], c)
        Xb = pd.concat([zr.loc[c.index].rename("raw"), za.loc[c.index].rename("adj"), pd.get_dummies(c.season, prefix="s", dtype=float)], axis=1)
        okb = Xb.notna().all(axis=1)
        rb = sm.OLS(c.err_close[okb], Xb[okb]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(c.date[okb])[0]})
        rows.append({"factor": col, "raw (per-game mean)": br, "t_raw": tr, "opponent-adjusted": ba, "t_adj": ta, "corr(raw, adj)": zr.corr(za),
                     "both in: raw": rb.params["raw"], "t": rb.tvalues["raw"], "both in: adj": rb.params["adj"], "t ": rb.tvalues["adj"]})
    table(pd.DataFrame(rows), index=False)
    RES["opp_adjust"] = rows

    emit("### 2e. After the vig: the eight factors alone as a walk-forward model\n")
    rows = []
    c8 = g[g.sig8.notna() & has_c]
    for th in (0.5, 1.0, 1.5):
        rows.append({"model": "8 factors", "threshold": th, "line": "close", **bets(c8.sig8, c8.total, c8.close_total, th, season=c8.season)})
        call = g[g.sig.notna() & has_c]
        rows.append({"model": "all 33 factors", "threshold": th, "line": "close", **bets(call.sig, call.total, call.close_total, th, season=call.season)})
        o8 = c8[c8.open_total.notna()]
        rows.append({"model": "8 factors", "threshold": th, "line": "open", **bets(o8.sig8, o8.total, o8.open_total, th, season=o8.season)})
    table(pd.DataFrame(rows), index=False)
    emit(f"Signal sd: 8 factors {c8.sig8.std():.2f}, 33 factors {call.sig.std():.2f}; correlation between them {c8.sig8.corr(c8.sig):.2f}.\n")
    RES["eight_bets"] = rows

    # =========================================================== 3. NEW HYPOTHESES
    new_hypotheses(g, F)

    emit("## 4. New hypotheses: discovery (2016-22) then validation (2023-26)\n")
    H = pd.DataFrame(HYP)
    H["disc_q"] = A.bh(H.disc_p.fillna(1).values)
    H["replicates"] = np.where((H.disc_q < 0.10) & (np.sign(H.disc_slope) == np.sign(H.valid_slope)) & (H.valid_t.abs() >= 2), "YES", "")
    emit(f"{len(H)} tests, each run once. Slopes are points of (actual - close) per +1 SD (or for a 0/1 flag), season fixed effects, date-clustered. "
         "`open` and `move` columns use all seasons with an opener and are descriptive.\n")
    show = H[["family", "hypothesis", "unit", "disc_n", "disc_slope", "disc_t", "disc_q", "valid_n", "valid_slope", "valid_t", "replicates",
              "open_slope", "open_t", "move_slope", "move_t"]]
    table(show, ".2f", index=False)
    emit(f"Discovery q<0.10: {int((H.disc_q<0.10).sum())}/{len(H)}. Replicated in validation: {int((H.replicates=='YES').sum())}.\n")
    RES["hypotheses"] = H.to_dict(orient="records")

    followups(g, F, allf, H)

    open(os.path.join(OUT, "phase2_results.md"), "w").write("\n".join(md) + "\n")
    json.dump(RES, open(os.path.join(OUT, "phase2_results.json"), "w"), indent=1, default=str)


# ----------------------------------------------------------------------------- follow-ups
def followups(g, F, allf, H):
    emit("## 5. Follow-ups on what replicated\n")
    c_ok = g.close_total.notna()
    neutral = g.neutral == 1
    valid = g.season > DISC_END

    emit("### 5a. Home-gym effect: is it the building or the team?\n")
    def prior_eff(mask, key, k=15):
        t = g[mask & c_ok].groupby(["season", key]).err_close.agg(["mean", "size"]).reset_index()
        t["eff"] = t["mean"] * t["size"] / (t["size"] + k)
        t["season"] += 1
        return t.rename(columns={key: "team"})[["season", "team", "eff"]]
    home_at_home = prior_eff(~neutral, "team2")          # home team's home games last season
    home_on_road = prior_eff(~neutral, "team1")          # same team's road games last season
    away_on_road = home_on_road
    away_at_home = home_at_home
    X = pd.DataFrame({
        "home team: last season's HOME games": g[["season", "team2"]].merge(home_at_home.rename(columns={"team": "team2"}), on=["season", "team2"], how="left").eff.values,
        "home team: last season's ROAD games": g[["season", "team2"]].merge(home_on_road.rename(columns={"team": "team2"}), on=["season", "team2"], how="left").eff.values,
        "road team: last season's ROAD games": g[["season", "team1"]].merge(away_on_road.rename(columns={"team": "team1"}), on=["season", "team1"], how="left").eff.values,
        "road team: last season's HOME games": g[["season", "team1"]].merge(away_at_home.rename(columns={"team": "team1"}), on=["season", "team1"], how="left").eff.values,
    }, index=g.index)
    m = ~neutral & c_ok & X.notna().all(axis=1)
    Z = (X - X[m].mean()) / X[m].std()
    rows = []
    for label, mm in (("all seasons", m), ("discovery 2016-22", m & ~valid), ("validation 2023-26", m & valid),
                      ("validation, altitude homes excluded", m & valid & ~g.team2.isin(HIGH_ALT))):
        Xr = pd.concat([Z[mm], pd.get_dummies(g.season[mm], prefix="s", dtype=float)], axis=1)
        r = sm.OLS(g.err_close[mm], Xr).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(g.date[mm])[0]})
        row = {"sample": label, "n": int(mm.sum())}
        for cname in X.columns:
            row[cname] = f"{r.params[cname]:+.2f} ({r.tvalues[cname]:.1f})"
        rows.append(row)
    table(pd.DataFrame(rows), index=False)
    emit("Each cell: points of (actual - close) per +1 SD, t in brackets, all four in one regression. If the building mattered, "
         "only the first column would carry weight; if it is the team's style, the home team's road games would predict too.\n")
    RES["home_gym"] = rows
    hp = X["home team: last season's HOME games"].where(~neutral)
    th = hp[(g.season <= DISC_END) & c_ok].abs().quantile(0.8)
    rows = []
    for label, mm in (("discovery 2016-22", ~valid), ("validation 2023-26", valid)):
        d = g[mm & c_ok & hp.notna()]
        x = bets(hp[d.index], d.total, d.close_total, th, season=d.season)
        rows.append({"sample": label, "line": "close", "threshold (pts, set on discovery)": th, **x})
        d2 = d[d.open_total.notna()]
        if len(d2) > 500:
            rows.append({"sample": label, "line": "open", "threshold (pts, set on discovery)": th, **bets(hp[d2.index], d2.total, d2.open_total, th, season=d2.season)})
    emit("Betting the home-gym prior alone (over if the home team's prior-season home games ran over the close by the threshold, under if under):\n")
    table(pd.DataFrame(rows), index=False)
    RES["home_gym_bets"] = rows

    emit("### 5b. Altitude\n")
    alt = g.team2.isin(HIGH_ALT) & ~neutral & c_ok
    t = g[alt].groupby("season").agg(games=("err_close", "size"), mean_vs_close=("err_close", "mean"),
                                    over_pct=("err_close", lambda v: 100 * (v > 0).sum() / (v != 0).sum()), mean_vs_open=("err_open", "mean"))
    table(t)
    d = g[alt]
    w, n = int((d.err_close > 0).sum()), int((d.err_close != 0).sum())
    dv = d[d.season > DISC_END]
    wv, nv = int((dv.err_close > 0).sum()), int((dv.err_close != 0).sum())
    emit(f"All altitude home games: overs {w}/{n} = {100*w/n:.1f}% (95% CI {wilson(w,n)[0]:.1f}-{wilson(w,n)[1]:.1f}). "
         f"Validation seasons only: {wv}/{nv} = {100*wv/nv:.1f}% (CI {wilson(wv,nv)[0]:.1f}-{wilson(wv,nv)[1]:.1f}). "
         "The list of 17 schools was fixed before looking at results.\n")
    t = d.groupby("team2").agg(games=("err_close", "size"), mean_vs_close=("err_close", "mean"),
                               over_pct=("err_close", lambda v: 100 * (v > 0).sum() / (v != 0).sum())).sort_values("mean_vs_close", ascending=False)
    table(t)
    RES["altitude"] = {"all": [w, n], "valid": [wv, nv]}

    emit("### 5c. Experimental model: 33 factors plus the new features that passed DISCOVERY only\n")
    exclude = ("closing total", "very high total", "very low total", "books disagree", "ex-post")
    sel = [h for h in H[H.disc_q < 0.10].hypothesis if not any(e in h for e in exclude)]
    X2 = F[allf].copy()
    newcols = []
    for i, h in enumerate(sel):
        col = f"new_{i}"
        v = HX[h]
        # 0/1 flags and sparse features: missing -> 0 (no information), plus keep as is
        X2[col] = v.fillna(0.0)
        newcols.append(col)
    emit("Selected using seasons through 2021-22 only (" + str(len(sel)) + " features): " + "; ".join(sel) + ".\n")
    gm = g[c_ok]
    rows = []
    preds = {}
    for label, cols in (("33 factors (phase-1 set)", allf), ("33 + new", allf + newcols), ("new only", newcols)):
        p, b = A.walk_forward(gm, X2.loc[gm.index], gm.err_close, cols, "ridge", first_test=DISC_END + 1)
        s = (p - b)
        preds[label] = s
        ok = s.notna()
        r2, tval = A.loss_test((gm.err_close - b)[ok].values, (gm.err_close - p)[ok].values, gm.date[ok].values)
        row = {"model": label, "test seasons": "2023-26", "n": int(ok.sum()), "OOS R2%": 100 * r2, "t": tval, "corr": np.corrcoef(s[ok], gm.err_close[ok])[0, 1]}
        for th in (1.0, 1.5):
            x = bets(s[ok], gm.total[ok], gm.close_total[ok], th, season=gm.season[ok])
            row[f"close bets@{th}"], row[f"win%@{th}"], row[f"CI@{th}"], row[f"seasons>BE@{th}"] = x["bets"], x["win%"], f"{x['ci_lo']:.1f}-{x['ci_hi']:.1f}", x["seasons>BE"]
        oo = ok & gm.open_total.notna()
        x = bets(s[oo], gm.total[oo], gm.open_total[oo], 1.5, season=gm.season[oo])
        row["open bets@1.5 (2024-26)"], row["open win%@1.5"], row["open CI"] = x["bets"], x["win%"], f"{x['ci_lo']:.1f}-{x['ci_hi']:.1f}"
        rows.append(row)
    table(pd.DataFrame(rows), index=False)
    RES["experimental_model"] = rows
    emit("This is a clean test of the ADDED features: they were chosen without seeing 2023-26. It is not a clean test of any threshold.\n")


# ----------------------------------------------------------------------------- opponent adjustment
def opponent_adjusted(g):
    """Season-to-date per-game means of selected rates, raw and adjusted for the opponent faced:
    adjusted obs = obs - (opponent's pregame counterpart - league mean of the counterpart) * scale."""
    K = 4
    spec = {  # name: (numerator, denominator, opponent counterpart style column, own-side prefix)
        "opp_ftr (FT rate allowed)": ("o_fta", "o_fga", "o_ftr"),
        "opp_3p_pct (3P% allowed)": ("o_tpm", "o_tpa", "o_3p_pct"),
        "opp_stl (steal rate)": ("stl", "poss", "o_tov"),
        "opp_foul (fouls per poss)": ("pf", "poss", "o_ftr"),
        "shot_ftr (own FT rate)": ("fta", "fga", "d_ftr"),
        "shot_orb (own off. reb. rate)": ("oreb", "orb_den", "d_orb"),
    }
    longs = []
    for me, opp in (("t1", "t2"), ("t2", "t1")):
        L = pd.DataFrame({"season": g.season, "date": g.date, "gid": g.index, "side": me,
                          "team": g["team1" if me == "t1" else "team2"], "poss": g.poss})
        for b in ("fta", "fga", "tpm", "tpa", "stl", "pf", "oreb", "dreb"):
            L[b] = g[f"{me}_{b}"]
            L["o_" + b] = g[f"{opp}_{b}"]
        L["orb_den"] = L.oreb + L.o_dreb
        for k in ("o_ftr", "o_3p_pct", "o_tov", "d_ftr", "d_orb"):
            L["opp_" + k] = g[f"{opp}_s_{k}"]
        longs.append(L)
    L = pd.concat(longs, ignore_index=True).sort_values(["season", "team", "date"])
    out = L[["gid", "side"]].copy()
    for name, (num, den, cp) in spec.items():
        obs = L[num] / L[den].replace(0, np.nan)
        cpd = L["opp_" + cp] - L["opp_" + cp].mean()
        ok = obs.notna() & cpd.notna()
        scale = np.polyfit(cpd[ok], obs[ok], 1)[0]            # how much the opponent's tendency shows up in one game
        for tag, v in (("raw", obs), ("adj", obs - scale * cpd)):
            mu = v.mean()
            vv = v.fillna(mu)
            cs = vv.groupby([L.season, L.team]).cumsum() - vv
            n = v.notna().astype(float).groupby([L.season, L.team]).cumsum() - v.notna().astype(float)
            out[f"{name}|{tag}"] = (cs - (vv.where(v.isna(), 0)).groupby([L.season, L.team]).cumsum() + (vv.where(v.isna(), 0))
                                    + K * mu) / (n + K)
    frame = pd.DataFrame(index=g.index)
    pairs = {}
    for name in spec:
        for tag in ("raw", "adj"):
            col = f"{name}|{tag}"
            a = out[out.side == "t1"].set_index("gid")[col]
            b = out[out.side == "t2"].set_index("gid")[col]
            frame[col] = a.reindex(g.index) + b.reindex(g.index)
        pairs[name] = (f"{name}|raw", f"{name}|adj")
    return {"frame": frame, "pairs": pairs}


# ----------------------------------------------------------------------------- new hypotheses
HIGH_ALT = {"Wyoming", "Air Force", "Colorado", "Colorado St.", "Northern Colorado", "Denver", "Utah", "Utah St.", "BYU",
            "Utah Valley", "Weber St.", "Southern Utah", "New Mexico", "Northern Arizona", "Nevada", "Montana St.", "Idaho St."}


def new_hypotheses(g, F):
    c_ok = g.close_total.notna()

    # ---------- team-game history from ALL games (incl. non-D1 opponents) for rest / last-game stats
    full = pd.concat([B.load_sked(y) for y in range(2016, 2027)], ignore_index=True)
    longs = []
    for me, opp in (("t1", "t2"), ("t2", "t1")):
        L = pd.DataFrame({"season": full.season, "date": full.date, "muid": full.muid, "team": full["team1" if me == "t1" else "team2"],
                          "poss_40": full.poss_40, "ot": (full.overtimes > 0).astype(float),
                          "tp": full[f"{me}_tpm"] / full[f"{me}_tpa"].replace(0, np.nan), "tpa": full[f"{me}_tpa"],
                          "o_tp": full[f"{opp}_tpm"] / full[f"{opp}_tpa"].replace(0, np.nan),
                          "efg": (full[f"{me}_fgm"] + 0.5 * full[f"{me}_tpm"]) / full[f"{me}_fga"].replace(0, np.nan),
                          "ft": full[f"{me}_ftm"] / full[f"{me}_fta"].replace(0, np.nan),
                          "tov": full[f"{me}_to"] / full.poss, "pts": full[f"{me}_pts"], "pf": full[f"{me}_pf"] + full[f"{opp}_pf"],
                          "game_total": full.t1_pts + full.t2_pts})
        longs.append(L)
    L = pd.concat(longs, ignore_index=True).sort_values(["season", "team", "date"]).reset_index(drop=True)
    gb = L.groupby(["season", "team"])
    L["rest"] = (L.date - gb.date.shift(1)).dt.days
    for k in ("tp", "o_tp", "efg", "ft", "tov", "poss_40", "ot", "game_total", "pf"):
        L["last_" + k] = gb[k].shift(1)
        L["avg_" + k] = gb[k].transform(lambda v: v.shift(1).expanding().mean())
        L["avgprev_" + k] = gb[k].transform(lambda v: v.shift(2).expanding().mean())     # baseline BEFORE the last game
    L["last3_tp"] = gb.tp.transform(lambda v: v.shift(1).rolling(3, min_periods=3).mean())
    L["gp"] = gb.cumcount()
    keep = ["season", "muid", "team", "rest", "gp", "last3_tp"] + [c for c in L.columns if c.startswith(("last_", "avg_", "avgprev_"))]
    for side, key in (("a", "team1"), ("b", "team2")):
        g = g.merge(L[keep].rename(columns={c: f"{side}_{c}" for c in keep if c not in ("season", "muid", "team")}).rename(columns={"team": key}),
                    on=["season", "muid", key], how="left")
    # previous game's market miss for each team (needs that game to have had a line)
    mk = pd.concat([g[["season", "date", "team1", "err_close"]].rename(columns={"team1": "team"}),
                    g[["season", "date", "team2", "err_close"]].rename(columns={"team2": "team"})]).dropna().sort_values(["season", "team", "date"])
    mk["prev_mkt_err"] = mk.groupby(["season", "team"]).err_close.shift(1)
    mk["avg_mkt_err"] = mk.groupby(["season", "team"]).err_close.transform(lambda v: v.shift(1).expanding().mean())
    mk["n_mkt"] = mk.groupby(["season", "team"]).cumcount()
    for side, key in (("a", "team1"), ("b", "team2")):
        g = g.merge(mk.drop(columns="err_close").rename(columns={"team": key, "prev_mkt_err": f"{side}_prev_mkt_err",
                    "avg_mkt_err": f"{side}_avg_mkt_err", "n_mkt": f"{side}_n_mkt"}).drop_duplicates(["season", "date", key]),
                    on=["season", "date", key], how="left")
    g.index = F.index

    def both(k):
        return g["a_" + k] + g["b_" + k]

    # ---------- B. outliers / shooting regression / overreaction
    fam = "B. last-game outliers"
    hyp(fam, "last game 3P% minus own prior average (hot shooting last time out)", (g.a_last_tp - g.a_avgprev_tp).fillna(0) + (g.b_last_tp - g.b_avgprev_tp).fillna(0)
        + 0 * both("avgprev_tp"), g)
    hyp(fam, "last game OPPONENT 3P% minus prior average allowed", (g.a_last_o_tp - g.a_avgprev_o_tp) + (g.b_last_o_tp - g.b_avgprev_o_tp), g)
    hyp(fam, "last 3 games 3P% minus season-to-date", (g.a_last3_tp - g.a_avg_tp) + (g.b_last3_tp - g.b_avg_tp), g)
    hyp(fam, "last game eFG% minus prior average", (g.a_last_efg - g.a_avgprev_efg) + (g.b_last_efg - g.b_avgprev_efg), g)
    hyp(fam, "last game FT% minus prior average", (g.a_last_ft - g.a_avgprev_ft) + (g.b_last_ft - g.b_avgprev_ft), g)
    hyp(fam, "last game turnover rate minus prior average", (g.a_last_tov - g.a_avgprev_tov) + (g.b_last_tov - g.b_avgprev_tov), g)
    hyp(fam, "last game pace minus prior average", (g.a_last_poss_40 - g.a_avgprev_poss_40) + (g.b_last_poss_40 - g.b_avgprev_poss_40), g)
    hyp(fam, "last game total fouls minus prior average", (g.a_last_pf - g.a_avgprev_pf) + (g.b_last_pf - g.b_avgprev_pf), g)
    hyp(fam, "either team's last game went to overtime", ((g.a_last_ot == 1) | (g.b_last_ot == 1)).astype(float).where(g.a_last_ot.notna() & g.b_last_ot.notna()), g, standardize=False)
    hyp(fam, "teams' previous game vs its closing total (sum of both teams' last market miss)", g.a_prev_mkt_err + g.b_prev_mkt_err, g,
        note="market overreaction test: negative = market over-adjusts after an over")
    hyp(fam, "extreme last game: either team's last game >= 25 pts off its close", (((g.a_prev_mkt_err.abs() >= 25) | (g.b_prev_mkt_err.abs() >= 25)).astype(float)
        * np.sign(g.a_prev_mkt_err.fillna(0) + g.b_prev_mkt_err.fillna(0))).where(g.a_prev_mkt_err.notna() & g.b_prev_mkt_err.notna()), g, standardize=False)
    fam = "F. team-level market persistence"
    ae = (g.a_avg_mkt_err * g.a_n_mkt / (g.a_n_mkt + 8)) + (g.b_avg_mkt_err * g.b_n_mkt / (g.b_n_mkt + 8))
    hyp(fam, "teams' season-to-date average miss vs the close (shrunk)", ae, g, note="do 'over teams' stay over teams?")
    # prior-season team effect and coach effect
    te = pd.concat([g[["season", "team1", "err_close"]].rename(columns={"team1": "team"}), g[["season", "team2", "err_close"]].rename(columns={"team2": "team"})]).dropna()
    ps = te.groupby(["season", "team"]).err_close.agg(["mean", "size"]).reset_index()
    ps["eff"] = ps["mean"] * ps["size"] / (ps["size"] + 20)
    ps["season"] += 1
    m1 = g[["season", "team1"]].merge(ps.rename(columns={"team": "team1"}), on=["season", "team1"], how="left").eff.values
    m2 = g[["season", "team2"]].merge(ps.rename(columns={"team": "team2"}), on=["season", "team2"], how="left").eff.values
    hyp(fam, "teams' PRIOR-season average miss vs the close (shrunk)", m1 + m2, g)
    ce = pd.concat([g[["season", "t1_coach", "err_close"]].rename(columns={"t1_coach": "coach"}), g[["season", "t2_coach", "err_close"]].rename(columns={"t2_coach": "coach"})]).dropna()
    cs = ce.groupby(["coach", "season"]).err_close.agg(["sum", "size"]).reset_index().sort_values(["coach", "season"])
    cs["csum"] = cs.groupby("coach")["sum"].cumsum() - cs["sum"]
    cs["cn"] = cs.groupby("coach")["size"].cumsum() - cs["size"]
    cs["ceff"] = cs.csum / (cs.cn + 40)
    c1 = g[["season", "t1_coach"]].merge(cs.rename(columns={"coach": "t1_coach"}), on=["season", "t1_coach"], how="left").ceff.values
    c2 = g[["season", "t2_coach"]].merge(cs.rename(columns={"coach": "t2_coach"}), on=["season", "t2_coach"], how="left").ceff.values
    hyp(fam, "coaches' career-to-date (prior seasons) average miss vs the close (shrunk)", c1 + c2, g)

    # ---------- A. venue / schedule
    fam = "A. venue & schedule"
    neutral = g.neutral == 1
    v = g[neutral & g.venue_id.notna() & c_ok][["season", "venue_id", "err_close"]]
    vs = v.groupby(["venue_id", "season"]).err_close.agg(["sum", "size"]).reset_index().sort_values(["venue_id", "season"])
    # expanding prior-seasons venue effect, shrunk with k=40 games
    allv = pd.MultiIndex.from_product([vs.venue_id.unique(), range(2016, 2028)], names=["venue_id", "season"]).to_frame(index=False)
    vs = allv.merge(vs, on=["venue_id", "season"], how="left").fillna({"sum": 0, "size": 0}).sort_values(["venue_id", "season"])
    vs["csum"] = vs.groupby("venue_id")["sum"].cumsum() - vs["sum"]
    vs["cn"] = vs.groupby("venue_id")["size"].cumsum() - vs["size"]
    vs["venue_prior"] = vs.csum / (vs.cn + 40)
    gv = g[["season", "venue_id"]].merge(vs[["venue_id", "season", "venue_prior", "cn"]], on=["season", "venue_id"], how="left")
    gv.index = g.index
    vp = gv.venue_prior.where(neutral & (gv.cn >= 10))
    hyp(fam, "neutral-site venue's prior-seasons average miss vs close (shrunk, >=10 prior games)", vp, g)
    # home venue: home team's prior-season home-game effect
    hv = g[~neutral & c_ok].groupby(["season", "team2"]).err_close.agg(["mean", "size"]).reset_index()
    hv["eff"] = hv["mean"] * hv["size"] / (hv["size"] + 15)
    hv["season"] += 1
    hp = g[["season", "team2"]].merge(hv, on=["season", "team2"], how="left").eff.values
    hyp(fam, "home gym: home team's prior-season home-game average miss vs close (shrunk)", pd.Series(hp, index=g.index).where(~neutral), g)
    dts = g.date
    feast = neutral & (dts.dt.month == 11) & (dts.dt.day >= 18)
    hyp(fam, "Feast Week neutral-site game (Nov 18-30)", feast.astype(float), g, standardize=False)
    hyp(fam, "any neutral-site game", neutral.astype(float), g, standardize=False)
    hyp(fam, "conference tournament game", (g.game_type == "conf_tourney").astype(float), g, standardize=False)
    hyp(fam, "postseason (NCAA/NIT/other) game", (g.game_type == "postseason").astype(float), g, standardize=False)
    b2b_any = ((g.a_rest == 1) | (g.b_rest == 1)).astype(float).where(g.a_rest.notna() & g.b_rest.notna())
    b2b_both = ((g.a_rest == 1) & (g.b_rest == 1)).astype(float).where(g.a_rest.notna() & g.b_rest.notna())
    hyp(fam, "either team played yesterday", b2b_any, g, standardize=False)
    hyp(fam, "both teams played yesterday (tournament day 2+)", b2b_both, g, standardize=False)
    hyp(fam, "long rest: both teams 7+ days off", ((g.a_rest >= 7) & (g.b_rest >= 7)).astype(float).where(g.a_rest.notna() & g.b_rest.notna()), g, standardize=False)
    hyp(fam, "home game at altitude (>4,000 ft home team)", (g.team2.isin(HIGH_ALT) & ~neutral).astype(float), g, standardize=False)
    hyp(fam, "altitude home team hosting a non-altitude visitor", (g.team2.isin(HIGH_ALT) & ~g.team1.isin(HIGH_ALT) & ~neutral).astype(float), g, standardize=False)

    # ---------- C. pace control
    fam = "C. pace control"
    a1, a2 = g.t1_tm_adjt, g.t2_tm_adjt
    hyp(fam, "tempo gap x slower team's defence forces few turnovers (slow team controls)", (a1 - a2).abs() * -np.where(a1 < a2, g.t1_s_d_tov, g.t2_s_d_tov), g)
    hyp(fam, "faster team's offensive rebound rate x tempo gap", (a1 - a2).abs() * np.where(a1 > a2, g.t1_s_o_orb, g.t2_s_o_orb), g)
    hyp(fam, "raw pace to date minus Torvik adjusted tempo (both teams)", (g.t1_s_pace - a1) + (g.t2_s_pace - a2), g)
    hyp(fam, "home team is the faster team (non-neutral)", (a2 > a1).astype(float).where(~neutral), g, standardize=False)
    hyp(fam, "tempo gap >= 6 possessions", ((a1 - a2).abs() >= 6).astype(float).where(a1.notna() & a2.notna()), g, standardize=False)

    # ---------- D. early season / roster
    fam = "D. early season & roster"
    gp = np.minimum(g.t1_s_gp, g.t2_s_gp)
    turn = 1 - g[["t1_ret_min", "t2_ret_min"]].mean(axis=1)
    hyp(fam, "season opener for either team (0 games played)", (gp == 0).astype(float), g, standardize=False)
    hyp(fam, "first 5 games for either team", (gp < 5).astype(float), g, standardize=False)
    hyp(fam, "roster turnover in the first 5 games", turn.where(gp < 5), g)
    hyp(fam, "new head coach (either) in the first 10 games", ((g.t1_new_coach == 1) | (g.t2_new_coach == 1)).astype(float).where(gp < 10), g, standardize=False)
    hyp(fam, "ex-post transfer minutes share, first 10 games [uses later info]", (g.t1_xp_transfer_share + g.t2_xp_transfer_share).where(gp < 10), g,
        note="descriptive only: minute shares are known only after the season")
    hyp(fam, "early opponents were weak: team rank now minus preseason-ish (rank gap of the two teams)", (g.t1_tm_rank - g.t2_tm_rank).abs().where(gp < 8), g)

    # ---------- E. game state
    fam = "E. game state"
    sp = g.mkt_spread_abs
    hyp(fam, "market spread size (bigger favourite)", sp, g)
    hyp(fam, "pick'em-ish game: spread <= 3", (sp <= 3).astype(float).where(sp.notna()), g, standardize=False)
    hyp(fam, "blowout expected: spread >= 15", (sp >= 15).astype(float).where(sp.notna()), g, standardize=False)
    hyp(fam, "close spread x both teams' FT rate (late fouling pays)", ((sp <= 5).astype(float) * (g.t1_s_o_ftr + g.t2_s_o_ftr - 0.66)).where(sp.notna()), g)
    hyp(fam, "close spread x both teams' FT% (late fouling pays)", ((sp <= 5).astype(float) * (g.t1_s_o_ft_pct + g.t2_s_o_ft_pct - 1.42)).where(sp.notna()), g)
    hyp(fam, "teams' season-to-date overtime rate", both("avg_ot"), g)

    # ---------- F. other profiles
    fam = "F. other market profiles"
    hyp(fam, "closing total level", g.close_total, g)
    hyp(fam, "very high total (close >= 160)", (g.close_total >= 160).astype(float).where(c_ok), g, standardize=False)
    hyp(fam, "very low total (close <= 125)", (g.close_total <= 125).astype(float).where(c_ok), g, standardize=False)
    hyp(fam, "both teams from major conferences", (g.majors == 2).astype(float), g, standardize=False)
    hyp(fam, "neither team from a major conference", (g.majors == 0).astype(float), g, standardize=False)
    hyp(fam, "weekend game (Sat/Sun)", (g.date.dt.dayofweek >= 5).astype(float), g, standardize=False)
    hyp(fam, "combined team quality (sum of Torvik barthag)", g.t1_tm_barthag + g.t2_tm_barthag, g)
    hyp(fam, "defence-heavy matchup: both adj. defences better than both adj. offences are good", -(g.t1_tm_adjde + g.t2_tm_adjde) - (g.t1_tm_adjoe + g.t2_tm_adjoe), g)
    hyp(fam, "books disagree: range of totals across books (2+ books)", (g.book_max - g.book_min).where(g.n_books >= 3), g)
    hyp(fam, "3-point volume: both offences' 3PA rate x both defences' 3PA allowed", (g.t1_s_o_3par + g.t2_s_o_3par) * (g.t1_s_d_3par + g.t2_s_d_3par), g)
    hyp(fam, "second half of conference season (Feb on), conference games", ((g.date.dt.month.isin([2, 3])) & (g.game_type == "conf")).astype(float), g, standardize=False)

    # ---------- descriptive venue / game-state tables
    emit("## 3. Descriptive tables behind the new hypotheses\n")
    emit("### 3a. Named neutral-site venues (all seasons; raw means, NOT out-of-sample)\n")
    nv = g[neutral & g.venue.notna() & c_ok]
    vt = nv.groupby(["venue_id", "venue"]).agg(games=("err_close", "size"), seasons=("season", "nunique"), mean_vs_close=("err_close", "mean"),
                                               sd=("err_close", "std"), over_pct=("err_close", lambda v: 100 * (v > 0).sum() / max((v != 0).sum(), 1)),
                                               mean_vs_torvik=("err_total", "mean"), poss40_vs_torvik=("err_poss_40", "mean"),
                                               ppp_vs_torvik_x100=("err_ppp", lambda v: 100 * v.mean())).reset_index()
    vt["t"] = vt.mean_vs_close / (vt.sd / np.sqrt(vt.games))
    vt["shrunk_effect"] = vt.mean_vs_close * vt.games / (vt.games + 40)
    named = vt[vt.venue.str.contains("Mohegan|Lahaina|Imperial Arena|Atlantis|T-Mobile|Barclays|Madison Square|MGM Grand|Orleans|HTC|Ocean Center|"
                                    "State Farm Field House|ESPN Wide World|Baha Mar|Michelob|Gainbridge|Greensboro Coliseum|United Center|"
                                    "Enterprise Center|Thomas & Mack|Stan Sheriff|Sprint Center|T-Mobile Center|Capital One Arena", case=False, na=False)]
    table(named.sort_values("games", ascending=False)[["venue", "games", "seasons", "mean_vs_close", "t", "over_pct", "shrunk_effect",
                                                        "mean_vs_torvik", "poss40_vs_torvik", "ppp_vs_torvik_x100"]].head(28), index=False)
    big = vt[vt.games >= 40]
    emit(f"All neutral venues with >=40 lined games: {len(big)}. Venues with |t| >= 2: {int((big.t.abs()>=2).sum())} "
         f"(expected by chance: {0.0455*len(big):.1f}). Spread of venue means: observed sd {big.mean_vs_close.std():.2f} pts vs "
         f"{(big.sd/np.sqrt(big.games)).mean():.2f} expected from noise alone.\n")
    RES["venues"] = vt.sort_values("games", ascending=False).head(60).to_dict(orient="records")
    fw = g[feast & c_ok]
    t = fw.groupby("season").agg(games=("err_close", "size"), mean_vs_close=("err_close", "mean"),
                                 over_pct=("err_close", lambda v: 100 * (v > 0).sum() / max((v != 0).sum(), 1)),
                                 mean_vs_open=("err_open", "mean"), mean_vs_torvik=("err_total", "mean"))
    emit("Feast Week neutral-site games by season:\n")
    table(t)
    w, n = int((fw.err_close > 0).sum()), int((fw.err_close != 0).sum())
    emit(f"Feast Week overall: {n:,} games, overs {100*w/n:.1f}% (95% CI {wilson(w,n)[0]:.1f}-{wilson(w,n)[1]:.1f}), mean vs close {fw.err_close.mean():+.2f}.\n")

    emit("### 3b. Spread size, overtime and second-half scoring\n")
    cc = g[c_ok & g.mkt_spread_abs.notna()]
    sb = pd.cut(cc.mkt_spread_abs, [-0.1, 2.5, 5.5, 9.5, 14.5, 60], labels=["0-2.5", "3-5.5", "6-9.5", "10-14.5", "15+"])
    t = cc.groupby(sb, observed=True).apply(lambda d: pd.Series({
        "games": len(d), "OT%": 100 * (d.overtimes > 0).mean(), "mean vs close": d.err_close.mean(),
        "median vs close": d.err_close.median(), "over%": 100 * (d.err_close > 0).sum() / (d.err_close != 0).sum(),
        "over% regulation only": 100 * ((d.err_close > 0) & (d.overtimes == 0)).sum() / ((d.err_close != 0) & (d.overtimes == 0)).sum(),
        "2H minus 1H pts": (d.h2_total - d.h1_total).mean()}))
    table(t)
    RES["spread_buckets"] = t.reset_index().to_dict(orient="records")

    emit("### 3c. Who controls pace?\n")
    lg = g.groupby("date")[["t1_tm_adjt", "t2_tm_adjt"]].transform("mean").mean(axis=1)
    X = pd.DataFrame({"slow": np.minimum(a1, a2) - lg, "fast": np.maximum(a1, a2) - lg})
    ok = X.notna().all(axis=1) & (g.overtimes >= 0)
    r = sm.OLS((g.poss_40 - lg)[ok], sm.add_constant(X[ok])).fit()
    emit(f"Actual per-40 possessions on the two teams' pregame adjusted tempos (deviations from average): slower team {r.params['slow']:.3f} "
         f"(se {r.bse['slow']:.3f}), faster team {r.params['fast']:.3f} (se {r.bse['fast']:.3f}); difference t = "
         f"{(r.params['slow']-r.params['fast'])/np.sqrt(r.bse['slow']**2+r.bse['fast']**2 - 2*r.cov_params().loc['slow','fast']):.1f}. "
         "Equal weights mean neither side dictates; an additive model predicts ~1.0 each.\n")
    gap = pd.cut((a1 - a2).abs(), [-0.1, 2, 4, 6, 20], labels=["0-2", "2-4", "4-6", "6+"])
    t = g[c_ok].groupby(gap[c_ok], observed=True).agg(games=("err_close", "size"), poss40_vs_torvik=("err_poss_40", "mean"),
                                                     total_vs_torvik=("err_total", "mean"), total_vs_close=("err_close", "mean"),
                                                     over_pct=("err_close", lambda v: 100 * (v > 0).sum() / (v != 0).sum()))
    emit("By tempo gap between the two teams:\n")
    table(t)

    emit("### 3d. Early season: how good is the market before teams have played?\n")
    gpb = pd.cut(gp, [-1, 0, 2, 5, 10, 20, 50], labels=["0", "1-2", "3-5", "6-10", "11-20", "21+"])
    t = g[c_ok].groupby(gpb[c_ok], observed=True).apply(lambda d: pd.Series({
        "games": len(d), "close_MAE": d.err_close.abs().mean(), "torvik_MAE": d.err_total.abs().mean(),
        "mean vs close": d.err_close.mean(), "over%": 100 * (d.err_close > 0).sum() / (d.err_close != 0).sum(),
        "open_MAE (where open exists)": d.err_open.abs().mean(), "mean|move|": d.move.abs().mean()}))
    table(t)
    t = g[c_ok & (gp < 5)].groupby("season").agg(games=("err_close", "size"), mean_vs_close=("err_close", "mean"),
                                                over_pct=("err_close", lambda v: 100 * (v > 0).sum() / (v != 0).sum()))
    emit("First five games, by season (is the early-season under still there?):\n")
    table(t)


if __name__ == "__main__":
    main()
