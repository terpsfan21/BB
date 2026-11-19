"""Build the game-level historical dataset.

One row per D1-vs-D1 game, 2014-15 .. 2025-26, with
  * Torvik FROZEN pregame projection (points, total, possessions)  -> pre_*
  * Torvik retroactively recomputed projection (leaky; kept only as a warning) -> retro_*
  * actual score / possessions / overtime
  * point-in-time Torvik ratings (time machine, strictly before game day) -> tm_*
  * pregame rolling style / shot-profile features built only from earlier games
  * roster continuity and coaching change
  * sportsbook totals (ESPN multi-book close, SBR archive close)

Output: data/processed/games.parquet
"""
import ast
import datetime as dt
import glob
import gzip
import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
SEASONS = range(2015, 2027)

BOX = ["fgm", "fga", "tpm", "tpa", "ftm", "fta", "oreb", "dreb", "reb", "ast", "stl", "blk", "to", "pf", "pts"]


def parse_list(s):
    if not isinstance(s, str):
        return None
    try:
        return ast.literal_eval(s)
    except Exception:
        return None


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


# ----------------------------------------------------------------------------- Torvik schedule
def load_sked(y):
    d = pd.read_csv(f"{RAW}/torvik/sked/{y}.csv", header=None)
    out = pd.DataFrame({
        "season": y,
        "muid": d[0],
        "date": pd.to_datetime(d[1], format="%m/%d/%y"),
        "game_type": d[6].map({0: "nonconf", 1: "conf", 2: "conf_tourney", 3: "postseason", 99: "non_d1"}),
        "neutral": d[7].astype(int),
        "team1": d[8], "team2": d[14],           # team1 = away (or first listed at neutral), team2 = home
        "retro_t1_pts": d[13], "retro_t2_pts": d[19], "retro_poss": d[20],
        "played": d[23],
        "poss_40": d[25], "poss": d[26],           # poss_40 = possessions per 40 min, poss = incl. overtime
        "t1_pts": d[27], "t2_pts": d[28],
        "overtimes": d[51].fillna(0).astype(int),
    })
    fr = d[54].map(parse_list)
    out["pre_line"] = fr.map(lambda v: v[2] if v else None)
    out["pre_t1_pts"] = fr.map(lambda v: fnum(v[3]) if v else np.nan)
    out["pre_t2_pts"] = fr.map(lambda v: fnum(v[4]) if v else np.nan)
    out["pre_t1_rank"] = fr.map(lambda v: fnum(v[7]) if v and len(v) > 7 else np.nan)
    out["pre_t2_rank"] = fr.map(lambda v: fnum(v[8]) if v and len(v) > 8 else np.nan)
    out["pre_poss_stored"] = fr.map(lambda v: fnum(v[9]) if v and len(v) > 9 else np.nan)
    box = d[50].map(parse_list)
    for side, off in (("t1", 4), ("t2", 19)):
        for k, name in enumerate(BOX):
            out[f"{side}_{name}"] = box.map(lambda v, i=off + k: fnum(v[i]) if v and len(v) > 34 else np.nan)
    out = out[(out.played == 1) & out.t1_pts.notna()].drop(columns="played")
    return out


# ----------------------------------------------------------------------------- time machine
# older snapshots use the school names of the day; schedule files use current names
TM_ALIAS = {
    "Arkansas Little Rock": "Little Rock", "College of Charleston": "Charleston", "Detroit": "Detroit Mercy",
    "Houston Baptist": "Houston Christian", "IPFW": "Purdue Fort Wayne", "Fort Wayne": "Purdue Fort Wayne",
    "IUPUI": "IU Indy", "LIU Brooklyn": "LIU", "Louisiana Lafayette": "Louisiana",
    "North Carolina St.": "N.C. State", "St. Francis PA": "Saint Francis", "Dixie St.": "Utah Tech",
    "Texas A&M Commerce": "East Texas A&M",
}

def load_tm():
    rows = []
    for p in sorted(glob.glob(f"{RAW}/torvik/tm/*.json.gz")):
        day = pd.Timestamp(os.path.basename(p)[:8])
        try:
            js = json.load(gzip.open(p))
        except Exception:
            continue
        for x in js:
            rows.append((day, x[1], x[4], x[6], x[8], x[0], x[44] if len(x) > 44 else np.nan))
    tm = pd.DataFrame(rows, columns=["tm_date", "team", "adjoe", "adjde", "barthag", "rank", "adjt"])
    for c in ("adjoe", "adjde", "barthag", "rank", "adjt"):
        tm[c] = pd.to_numeric(tm[c], errors="coerce")
    tm["team"] = tm.team.replace(TM_ALIAS)
    return tm.sort_values(["tm_date", "team"])


def attach_tm(g, tm):
    """Ratings from the latest snapshot dated strictly BEFORE the game day.  Reconstructing
    Torvik's frozen line from snapshots shows the file dated D-1 reproduces it best
    (r=0.990 vs 0.972 for the file dated D), i.e. the file dated D already reflects D's games."""
    g = g.sort_values("date")
    tm = tm.rename(columns={"tm_date": "date"})
    tm["tm_asof"] = tm["date"]
    for side in ("t1", "t2"):
        r = tm.rename(columns={c: f"{side}_tm_{c}" for c in ("adjoe", "adjde", "barthag", "rank", "adjt")})
        r = r.rename(columns={"team": {"t1": "team1", "t2": "team2"}[side], "tm_asof": f"{side}_tm_asof"})
        key = {"t1": "team1", "t2": "team2"}[side]
        g = pd.merge_asof(g, r, on="date", by=key, direction="backward", tolerance=pd.Timedelta(days=10),
                          allow_exact_matches=False)
    # season guard: never take a snapshot from an earlier season
    for side in ("t1", "t2"):
        bad = g[f"{side}_tm_asof"].notna() & (g[f"{side}_tm_asof"] < pd.to_datetime((g.season - 1).astype(str) + "-10-25"))
        g.loc[bad, [c for c in g.columns if c.startswith(f"{side}_tm_")]] = np.nan
    return g


# ----------------------------------------------------------------------------- rolling style features
def style_features(g):
    """Season-to-date team style, using ONLY games before the game date.
    Shrunk toward the league mean with K pseudo-games so early-season values are stable."""
    K = 4
    a = g[["season", "date", "muid", "team1", "team2", "poss", "poss_40"] +
          [f"{s}_{b}" for s in ("t1", "t2") for b in BOX]]
    longs = []
    for me, opp in (("t1", "t2"), ("t2", "t1")):
        L = pd.DataFrame({"season": a.season, "date": a.date, "muid": a.muid,
                          "team": a["team1" if me == "t1" else "team2"], "poss": a.poss, "poss_40": a.poss_40})
        for b in BOX:
            L[b] = a[f"{me}_{b}"]
            L["o_" + b] = a[f"{opp}_{b}"]
        L["side"] = me
        longs.append(L)
    L = pd.concat(longs).dropna(subset=["fga", "o_fga"]).sort_values(["season", "team", "date"])
    L["n"] = 1.0
    sums = ["n", "poss", "poss_40"] + BOX + ["o_" + b for b in BOX]
    # cumulative totals strictly before this date (same-day games excluded via per-date aggregation)
    daily = L.groupby(["season", "team", "date"])[sums].sum().groupby(level=[0, 1]).cumsum()
    prior = daily.groupby(level=[0, 1]).shift(1).fillna(0).reset_index()
    P = L[["season", "team", "date", "muid", "side"]].merge(prior, on=["season", "team", "date"], how="left")

    # league per-game means for the shrinkage prior (computed from all prior seasons' scale: use global means)
    m = L[sums].mean()

    def shr(numer_cols, denom_cols):
        num = sum(P[c] for c in numer_cols)
        den = sum(P[c] for c in denom_cols)
        mnum = sum(m[c] for c in numer_cols)
        mden = sum(m[c] for c in denom_cols)
        return (num + K * mnum) / (den + K * mden)

    F = P[["season", "team", "date", "muid", "side"]].copy()
    F["gp"] = P.n
    F["pace"] = shr(["poss_40"], ["n"])                       # raw possessions per 40
    # offence
    F["o_3par"] = shr(["tpa"], ["fga"])
    F["o_3p_pct"] = shr(["tpm"], ["tpa"])
    F["o_2p_pct"] = (P.fgm - P.tpm + K * (m.fgm - m.tpm)) / (P.fga - P.tpa + K * (m.fga - m.tpa))
    F["o_ftr"] = shr(["fta"], ["fga"])
    F["o_ft_pct"] = shr(["ftm"], ["fta"])
    F["o_tov"] = shr(["to"], ["poss"])
    F["o_orb"] = shr(["oreb"], ["oreb", "o_dreb"])
    F["o_efg"] = (P.fgm + 0.5 * P.tpm + K * (m.fgm + 0.5 * m.tpm)) / (P.fga + K * m.fga)
    F["o_ast"] = shr(["ast"], ["fgm"])
    F["o_ppp"] = shr(["pts"], ["poss"])
    # defence (what opponents do against this team)
    F["d_3par"] = shr(["o_tpa"], ["o_fga"])
    F["d_3p_pct"] = shr(["o_tpm"], ["o_tpa"])
    F["d_ftr"] = shr(["o_fta"], ["o_fga"])
    F["d_tov"] = shr(["o_to"], ["poss"])
    F["d_orb"] = shr(["o_oreb"], ["o_oreb", "dreb"])
    F["d_efg"] = (P.o_fgm + 0.5 * P.o_tpm + K * (m.o_fgm + 0.5 * m.o_tpm)) / (P.o_fga + K * m.o_fga)
    F["d_stl"] = shr(["stl"], ["poss"])
    F["d_blk"] = shr(["blk"], ["o_fga"])
    F["d_foul"] = shr(["pf"], ["poss"])
    F["d_ppp"] = shr(["o_pts"], ["poss"])
    feats = [c for c in F.columns if c not in ("season", "team", "date", "muid", "side")]
    for side in ("t1", "t2"):
        sub = F[F.side == side][["muid", "season"] + feats].rename(columns={c: f"{side}_s_{c}" for c in feats})
        g = g.merge(sub, on=["muid", "season"], how="left")
    return g


# ----------------------------------------------------------------------------- roster / coach
def roster_features():
    pl = {}
    for y in range(min(SEASONS) - 1, max(SEASONS) + 1):
        p = pd.read_csv(f"{RAW}/torvik/players/{y}.csv", header=None, low_memory=False)
        p = p[[0, 1, 3, 4, 25, 32]].copy()
        p.columns = ["name", "team", "gp", "min_pct", "cls", "pid"]
        p["min_pct"] = pd.to_numeric(p.min_pct, errors="coerce").fillna(0)
        pl[y] = p
    rows = []
    for y in SEASONS:
        cur, prev = pl[y], pl[y - 1]
        prev_team = prev.groupby("pid").team.first()
        cur = cur.assign(prev_team=cur.pid.map(prev_team))
        for team, c in cur.groupby("team"):
            pv = prev[prev.team == team]
            if len(pv) == 0:
                ret = np.nan
            else:
                ret = pv[pv.pid.isin(c.pid)].min_pct.sum() / max(pv.min_pct.sum(), 1e-9)
            tot = max(c.min_pct.sum(), 1e-9)
            same = c.prev_team == team
            rows.append({
                "season": y, "team": team,
                # share of LAST season's minutes played by players on this season's roster (knowable preseason)
                "ret_min": ret,
                # composition of THIS season's minutes (ex-post; descriptive only)
                "xp_returner_share": c[same].min_pct.sum() / tot,
                "xp_transfer_share": c[c.prev_team.notna() & ~same].min_pct.sum() / tot,
                "xp_newcomer_share": c[c.prev_team.isna()].min_pct.sum() / tot,
            })
    return pd.DataFrame(rows)


def coach_features():
    rows = []
    for y in range(min(SEASONS) - 1, max(SEASONS) + 1):
        p = f"{RAW}/torvik/gamestats/{y}.csv"
        if not os.path.exists(p):
            continue
        d = pd.read_csv(p, header=None, low_memory=False)
        d = d[[0, 2, 25]].copy()
        d.columns = ["date", "team", "coach"]
        d["date"] = pd.to_datetime(d.date, format="%m/%d/%y", errors="coerce")
        d = d.sort_values("date")
        first = d.groupby("team").coach.first()
        last = d.groupby("team").coach.last()
        rows.append(pd.DataFrame({"season": y, "team": first.index, "coach_first": first.values,
                                  "coach_last": last.reindex(first.index).values}))
    c = pd.concat(rows)
    prev = c[["season", "team", "coach_last"]].assign(season=lambda x: x.season + 1).rename(
        columns={"coach_last": "coach_prev"})
    c = c.merge(prev, on=["season", "team"], how="left")
    c["new_coach"] = np.where(c.coach_prev.isna(), np.nan, (c.coach_first != c.coach_prev).astype(float))
    return c[["season", "team", "coach_first", "new_coach"]].rename(columns={"coach_first": "coach"})


# ----------------------------------------------------------------------------- odds
NON_BOOKS = re.compile(r"accuscore|numberfire|teamrankings|live", re.I)


def espn_odds():
    rows = []
    for y in SEASONS:
        ep, op = f"{RAW}/espn/events_{y}.json", f"{RAW}/espn/odds_{y}.json"
        if not (os.path.exists(ep) and os.path.exists(op)):
            continue
        events, odds = json.load(open(ep)), json.load(open(op))
        for e in events:
            ts = pd.Timestamp(e["date_utc"]).tz_convert("America/New_York")
            r = {"season": y, "espn_id": e["id"], "date": ts.tz_localize(None).normalize(),
                 "espn_home": e.get("home"), "espn_away": e.get("away"),
                 "hs": fnum(e.get("home_score")), "as": fnum(e.get("away_score"))}
            closes, opens, cons = [], [], np.nan
            for o in odds.get(e["id"]) or []:
                name = o.get("provider") or ""
                if NON_BOOKS.search(name):
                    continue
                if name.lower() == "opening":
                    if o.get("ou") is not None and 80 <= o["ou"] <= 250:
                        opens.append(o["ou"])
                    continue
                c = o.get("close_total") if o.get("close_total") is not None else o.get("ou")
                if c is None or not (80 <= c <= 250):
                    continue
                if name.lower() == "consensus":
                    cons = c
                closes.append(c)
                if o.get("open_total") is not None and 80 <= o["open_total"] <= 250:
                    opens.append(o["open_total"])
            r["espn_close"] = float(np.median(closes)) if closes else np.nan
            r["espn_open"] = float(np.median(opens)) if opens else np.nan
            r["espn_n_books"] = len(closes)
            r["espn_close_min"] = min(closes) if closes else np.nan
            r["espn_close_max"] = max(closes) if closes else np.nan
            rows.append(r)
    return pd.DataFrame(rows)


def sbro_odds():
    rows = []
    for p in sorted(glob.glob(f"{RAW}/sbro/*.xlsx")):
        y = int(os.path.basename(p)[:4]) + 1
        d = pd.read_excel(p)
        d.columns = [str(c).strip() for c in d.columns]
        d = d.reset_index(drop=True)
        for i in range(0, len(d) - 1, 2):
            a, b = d.iloc[i], d.iloc[i + 1]
            try:
                md = int(a["Date"])
                m, day = md // 100, md % 100
                date = pd.Timestamp(year=y - 1 if m >= 8 else y, month=m, day=day)
            except Exception:
                continue
            ca, cb = fnum(a["Close"]), fnum(b["Close"])
            oa, ob = fnum(a["Open"]), fnum(b["Open"])
            close = np.nanmax([ca, cb]) if not (np.isnan(ca) and np.isnan(cb)) else np.nan
            opn = np.nanmax([oa, ob]) if not (np.isnan(oa) and np.isnan(ob)) else np.nan
            rows.append({"season": y, "date": date, "s1": fnum(a["Final"]), "s2": fnum(b["Final"]),
                         "sbr_close": close if close and close >= 90 else np.nan,
                         "sbr_open": opn if opn and opn >= 90 else np.nan})
    return pd.DataFrame(rows)


def attach_by_score(g, o, s_cols, val_cols, tag):
    """Join an odds table to games on (season, date +/- 1 day, unordered score pair).
    Only unambiguous matches are kept."""
    o = o.dropna(subset=s_cols).copy()
    o["lo"] = o[s_cols].min(axis=1)
    o["hi"] = o[s_cols].max(axis=1)
    g = g.copy()
    g["lo"] = g[["t1_pts", "t2_pts"]].min(axis=1)
    g["hi"] = g[["t1_pts", "t2_pts"]].max(axis=1)
    pairs = []
    matched = pd.Series(False, index=g.index)
    used = pd.Series(False, index=o.index)
    for shift in (0, -1, 1):
        left = g.loc[~matched, ["season", "date", "lo", "hi"]].reset_index()
        right = o.loc[~used].reset_index().rename(columns={"index": "oidx"})
        right["date"] = right["date"] + pd.Timedelta(days=shift)
        m = left.merge(right[["season", "date", "lo", "hi", "oidx"] + val_cols], on=["season", "date", "lo", "hi"])
        m = m[~m.duplicated("index", keep=False) & ~m.duplicated("oidx", keep=False)]
        pairs.append(m[["index", "oidx"]])
        matched.loc[m["index"].values] = True
        used.loc[m["oidx"].values] = True
    pr = pd.concat(pairs).set_index("index").oidx
    for c in val_cols:
        g[c] = pr.map(o[c]).reindex(g.index)
    print(f"{tag}: matched {matched.sum()} of {len(g)} games ({len(o)} odds rows)")
    return g.drop(columns=["lo", "hi"])


# ----------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    g = pd.concat([load_sked(y) for y in SEASONS], ignore_index=True)
    print("games in schedule files:", len(g))
    g = style_features(g)                    # uses every game incl. non-D1 opponents' box lines
    g = g[g.game_type != "non_d1"].copy()
    tm = load_tm()
    g = attach_tm(g, tm)

    ros, coach = roster_features(), coach_features()
    for side, key in (("t1", "team1"), ("t2", "team2")):
        r = ros.merge(coach, on=["season", "team"], how="outer")
        r = r.rename(columns={c: f"{side}_{c}" for c in r.columns if c not in ("season", "team")}).rename(
            columns={"team": key})
        g = g.merge(r, on=["season", key], how="left")

    eo = espn_odds()
    if len(eo):
        g = attach_by_score(g, eo, ["hs", "as"],
                            ["espn_id", "espn_close", "espn_open", "espn_n_books", "espn_close_min", "espn_close_max"],
                            "ESPN")
    so = sbro_odds()
    if len(so):
        g = attach_by_score(g, so, ["s1", "s2"], ["sbr_close", "sbr_open"], "SBR")

    # ---- derived targets
    g["pre_total"] = g.pre_t1_pts + g.pre_t2_pts
    g["retro_total"] = g.retro_t1_pts + g.retro_t2_pts
    g["total"] = g.t1_pts + g.t2_pts
    lg_t = g.groupby("season")[["t1_tm_adjt", "t2_tm_adjt"]].transform("mean").mean(axis=1)
    g["pre_poss_recon"] = g.t1_tm_adjt * g.t2_tm_adjt / lg_t
    g["pre_poss"] = g.pre_poss_stored.fillna(g.pre_poss_recon)
    g["pre_poss_source"] = np.where(g.pre_poss_stored.notna(), "stored", np.where(g.pre_poss_recon.notna(), "reconstructed", None))
    g["pre_ppp"] = g.pre_total / (2 * g.pre_poss)
    g["ppp"] = g.total / (2 * g.poss)
    g["err_total"] = g.total - g.pre_total                    # actual minus Torvik
    g["err_poss"] = g.poss - g.pre_poss                       # incl. overtime possessions
    g["err_poss_40"] = g.poss_40 - g.pre_poss                 # regulation-pace error
    g["err_ppp"] = g.ppp - g.pre_ppp
    g["close_total"] = g.get("sbr_close", pd.Series(np.nan, index=g.index)).fillna(g.get("espn_close"))
    g["close_source"] = np.where(g.get("sbr_close").notna(), "sbr", np.where(g.get("espn_close").notna(), "espn", None))
    g["err_close"] = g.total - g.close_total                  # actual minus market
    g["edge"] = g.pre_total - g.close_total                   # Torvik minus market
    g["day_of_season"] = (g.date - pd.to_datetime((g.season - 1).astype(str) + "-11-01")).dt.days
    g = g.sort_values(["date", "muid"]).reset_index(drop=True)
    f64 = g.select_dtypes("float64").columns
    g[f64] = g[f64].astype("float32")
    g.to_parquet(f"{OUT}/games.parquet", index=False, compression="zstd")
    print("rows", len(g), "cols", g.shape[1])
    print(g.groupby("season").agg(n=("muid", "size"), pre=("pre_total", "count"), poss=("pre_poss", "count"),
                                  tm=("t1_tm_adjt", "count"), espn=("espn_close", "count"),
                                  sbr=("sbr_close", "count"), close=("close_total", "count")))


if __name__ == "__main__":
    main()
