"""Score the frozen-model forward log.  Reconstructions and genuinely prospective predictions are
reported separately and never pooled.  Writes reports/forward_test.md.

Bet rule (frozen): OVER if signal >= 1.5, UNDER if signal <= -1.5.
Lines: DraftKings open and close with actual prices from the post-game ESPN record; for prospective
predictions also the first line observed before tip-off after the prediction was logged.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_dataset as B      # noqa: E402
from phase2 import bets, wilson  # noqa: E402

FWD = os.path.join(ROOT, "data", "forward")


def main(y=2027):
    p = pd.read_csv(f"{FWD}/predictions.csv", dtype={"espn_id": str})
    ln = pd.read_csv(f"{FWD}/lines.csv", dtype={"espn_id": str})
    res = B.load_sked(y)[["muid", "t1_pts", "t2_pts", "overtimes"]]
    res["total"] = res.t1_pts + res.t2_pts
    post = ln[(ln.observed == "post_game") & (ln.provider == "DraftKings")].drop_duplicates("espn_id", keep="last")
    pre = ln[(ln.observed == "pre_tip") & (ln.provider == "DraftKings")].sort_values("obs_ts_utc")
    out = ["# Frozen v1 forward test, season %d-%02d\n" % (y - 1, y % 100)]
    out.append(f"Generated {pd.Timestamp.utcnow():%Y-%m-%d %H:%M} UTC. Log rows: {len(p)}; "
               f"prospective {int((p.kind=='prospective').sum())}, reconstruction {int((p.kind=='reconstruction').sum())}.\n")
    for kind in ("prospective", "reconstruction"):
        d = p[p.kind == kind].sort_values("run_ts_utc").drop_duplicates("muid", keep="first")   # earliest prediction counts
        d = d.merge(res, on="muid", how="inner").merge(post[["espn_id", "open_total", "open_over", "open_under", "close_total",
                                                             "close_over", "close_under"]], on="espn_id", how="left")
        out.append(f"## {kind.capitalize()} predictions\n")
        if kind == "reconstruction":
            out.append("These were computed AFTER the games were played, from inputs dated before each game. They are a "
                       "check that the pipeline works, not a forward test.\n")
        if len(d) == 0:
            out.append("No settled games yet.\n")
            continue
        lined = d[d.close_total.notna()]
        out.append(f"Settled games: {len(d)}; with a DraftKings close: {len(lined)}; flagged bets (|signal| >= 1.5): "
                   f"{int((lined.signal.abs() >= 1.5).sum())}; overtime games: {int((d.overtimes > 0).sum())}.\n")
        rows = []
        for nm, line, oo, uo in (("DK open", "open_total", "open_over", "open_under"), ("DK close", "close_total", "close_over", "close_under")):
            for th in (1.5,):
                x = bets(lined.signal, lined.total, lined[line], th, lined[oo], lined[uo])
                if x.get("bets"):
                    rows.append({"line": nm, "threshold": th, "bets": x["bets"], "win%": round(x["win%"], 1),
                                 "95% CI": f"{x['ci_lo']:.1f}-{x['ci_hi']:.1f}", "ROI% at actual price": round(x["ROI%"], 1),
                                 "ROI 95% CI": f"{x['ROI_lo']:.1f} to {x['ROI_hi']:.1f}"})
        if kind == "prospective" and len(pre):
            first = pre.merge(d[["espn_id", "run_ts_utc"]], on="espn_id")
            first = first[first.obs_ts_utc >= first.run_ts_utc].drop_duplicates("espn_id", keep="first")
            dd = d.merge(first[["espn_id", "total", "over_odds", "under_odds", "obs_ts_utc"]].rename(columns={"total": "obs_total"}), on="espn_id")
            x = bets(dd.signal, dd.total, dd.obs_total, 1.5, dd.over_odds, dd.under_odds)
            if x.get("bets"):
                rows.append({"line": "first DK line seen after prediction", "threshold": 1.5, "bets": x["bets"], "win%": round(x["win%"], 1),
                             "95% CI": f"{x['ci_lo']:.1f}-{x['ci_hi']:.1f}", "ROI% at actual price": round(x["ROI%"], 1),
                             "ROI 95% CI": f"{x['ROI_lo']:.1f} to {x['ROI_hi']:.1f}"})
        if rows:
            out.append(pd.DataFrame(rows).to_markdown(index=False) + "\n")
        b = lined[lined.signal.abs() >= 1.5]
        if len(b):
            clv = (b.close_total - b.open_total) * np.sign(b.signal)
            out.append(f"Closing-line value on flagged bets taken at the DK open: mean {clv.mean():+.2f} pts; line moved toward the bet "
                       f"{100*(clv>0).mean():.0f}%, against {100*(clv<0).mean():.0f}%, unchanged {100*(clv==0).mean():.0f}%.\n")
        e_line = lined.total - lined.close_total
        e_mod = lined.total - (lined.close_total + lined.signal)
        out.append(f"All lined games: MAE of the close {e_line.abs().mean():.2f}; MAE of close + signal {e_mod.abs().mean():.2f}; "
                   f"corr(signal, actual - close) {np.corrcoef(lined.signal, e_line)[0,1]:+.3f}; "
                   f"corr(signal, close - open) {np.corrcoef(lined.signal[lined.open_total.notna()], (lined.close_total-lined.open_total)[lined.open_total.notna()])[0,1]:+.3f}; "
                   f"calibration slope of (actual - close) on signal {np.polyfit(lined.signal, e_line, 1)[0]:+.2f} (1.0 = signal sized correctly).\n")
    open(os.path.join(ROOT, "reports", "forward_test.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main(*[int(a) for a in sys.argv[1:]])
