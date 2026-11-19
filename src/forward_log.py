"""Forward test of the FROZEN v1 model on the current season.

Each run:
  1. refreshes Torvik current-season files and ESPN events/odds,
  2. scores every game that has all pregame inputs with frozen/v1 (no refitting, ever),
  3. appends to append-only logs in data/forward/:
       predictions.csv  one row per (game, run date); `kind` = prospective if the run happened
                        before tip-off, reconstruction otherwise
       lines.csv        every sportsbook total/price seen, with the observation timestamp
Evaluation lives in src/forward_eval.py.  Usage: python src/forward_log.py [season]
"""
import datetime as dt
import glob
import gzip
import json
import os
import sys
import urllib.request

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "frozen", "v1"))
import build_dataset as B          # noqa: E402
import fetch_espn_v2 as E2         # noqa: E402
import features as FZ              # noqa: E402
import predict as PZ               # noqa: E402

RAW = os.path.join(ROOT, "data", "raw")
FWD = os.path.join(ROOT, "data", "forward")
UA = {"User-Agent": "Mozilla/5.0"}


def dl(url, path):
    req = urllib.request.Request(url, headers=UA)
    body = urllib.request.urlopen(req, timeout=120).read()
    if len(body) > 200:
        open(path, "wb").write(body)
        return True
    return False


def refresh_torvik(y, today):
    for sub in ("sked", "gamestats", "players", "tm"):
        os.makedirs(f"{RAW}/torvik/{sub}", exist_ok=True)
    dl(f"https://barttorvik.com/{y}_super_sked.csv", f"{RAW}/torvik/sked/{y}.csv")
    dl(f"https://barttorvik.com/getgamestats.php?year={y}&csv=1", f"{RAW}/torvik/gamestats/{y}.csv")
    dl(f"https://barttorvik.com/getadvstats.php?year={y}&csv=1", f"{RAW}/torvik/players/{y}.csv")
    d = dt.date(y - 1, 11, 1)
    while d <= today:
        s = d.strftime("%Y%m%d")
        p = f"{RAW}/torvik/tm/{s}.json.gz"
        if not os.path.exists(p):
            try:
                dl(f"https://barttorvik.com/timemachine/team_results/{s}_team_results.json.gz", p)
            except Exception:
                pass
        d += dt.timedelta(days=1)


def load_tm_season(y):
    rows = []
    for p in sorted(glob.glob(f"{RAW}/torvik/tm/*.json.gz")):
        day = pd.Timestamp(os.path.basename(p)[:8])
        if day < pd.Timestamp(f"{y-1}-10-25"):
            continue
        try:
            js = json.load(gzip.open(p))
        except Exception:
            continue
        for x in js:
            rows.append((day, x[1], x[4], x[6], x[8], x[0], x[44] if len(x) > 44 else np.nan))
    tm = pd.DataFrame(rows, columns=["tm_date", "team", "adjoe", "adjde", "barthag", "rank", "adjt"])
    for c in ("adjoe", "adjde", "barthag", "rank", "adjt"):
        tm[c] = pd.to_numeric(tm[c], errors="coerce")
    tm["team"] = tm.team.replace(B.TM_ALIAS)
    return tm.sort_values(["tm_date", "team"])


def team_map():
    """Torvik name -> ESPN team id, learned from historical games matched on date + score."""
    p = os.path.join(ROOT, "data", "processed", "team_map.csv")
    if os.path.exists(p):
        return pd.read_csv(p, dtype={"espn_team_id": str})
    g = pd.read_parquet(os.path.join(ROOT, "data", "processed", "games.parquet"),
                        columns=["season", "date", "team1", "team2", "t1_pts", "t2_pts"])
    votes = []
    for f in sorted(glob.glob(f"{RAW}/espn2/events_*.json")):
        ev = pd.DataFrame(json.load(open(f)))
        if not len(ev) or "home_score" not in ev:
            continue
        ev["date"] = pd.to_datetime(ev.date_utc, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
        ev["hs"], ev["as_"] = pd.to_numeric(ev.home_score, errors="coerce"), pd.to_numeric(ev.away_score, errors="coerce")
        m = g.merge(ev, left_on=["date", "t2_pts", "t1_pts"], right_on=["date", "hs", "as_"])
        m = m[~m.duplicated(["date", "team1", "team2"], keep=False)]
        votes.append(pd.DataFrame({"team": pd.concat([m.team2, m.team1]), "espn_team_id": pd.concat([m.home_id, m.away_id])}))
    v = pd.concat(votes).value_counts().reset_index(name="n")
    v = v.sort_values("n", ascending=False).drop_duplicates("team").drop_duplicates("espn_team_id")
    v[["team", "espn_team_id", "n"]].sort_values("team").to_csv(p, index=False)
    return v


def espn_slate(y, today, days_ahead=3):
    """All ESPN events this season (played) plus the next few days, with current odds rows."""
    os.makedirs(f"{RAW}/espn2", exist_ok=True)
    E2.main(y, y)                                     # refresh completed events + their odds
    events = json.load(open(f"{RAW}/espn2/events_{y}.json"))
    odds = json.load(open(f"{RAW}/espn2/odds_{y}.json"))
    done = {e["id"] for e in events}
    up = []
    for k in range(0, days_ahead + 1):
        up += [e for e in E2.day_events(today + dt.timedelta(days=k), completed_only=False) if e["id"] not in done]
    up = list({e["id"]: e for e in up}.values())
    for e in up:
        i, rows = E2.event_odds(e["id"])
        odds[i] = rows if rows != "FAILED" else []
    return events + up, odds


def main(y=2027):
    now = dt.datetime.now(dt.timezone.utc)
    today_et = pd.Timestamp(now).tz_convert("America/New_York").date()
    os.makedirs(FWD, exist_ok=True)
    refresh_torvik(y, today_et)

    g = B.load_sked(y, played_only=False)
    g = g[g.game_type != "non_d1"].reset_index(drop=True) if False else g
    full = g.copy()
    st = FZ.style_features(full, PZ.MODEL["league_means_per_game"], PZ.MODEL["shrink_K"])
    g = g.merge(st, on=["muid", "season"], how="left")
    g = g[g.game_type != "non_d1"].copy()
    g = B.attach_tm(g, load_tm_season(y).copy())
    B.SEASONS = range(y, y + 1)
    ros, coach = B.roster_features(), B.coach_features()
    for side, key in (("t1", "team1"), ("t2", "team2")):
        r = ros.merge(coach, on=["season", "team"], how="outer")
        r = r.rename(columns={c: f"{side}_{c}" for c in r.columns if c not in ("season", "team")}).rename(columns={"team": key})
        g = g.merge(r, on=["season", key], how="left")
    g = g.reset_index(drop=True)
    sc = PZ.score(g)
    g["signal"], g["direction"] = sc.signal.values, sc.direction.values

    # ---- ESPN join (tip time, event id) by date + team ids
    tmap = team_map().set_index("team").espn_team_id.astype(str)
    events, odds = espn_slate(y, today_et)
    ev = pd.DataFrame(events)
    ev["tip_utc"] = pd.to_datetime(ev.date_utc, utc=True)
    ev["date"] = ev.tip_utc.dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    ev["key"] = ev.apply(lambda r: "|".join(sorted([str(r.home_id), str(r.away_id)])), axis=1)
    g["key"] = [("|".join(sorted([tmap.get(a, "?" + a), tmap.get(b, "?" + b)]))) for a, b in zip(g.team1, g.team2)]
    g = g.merge(ev[["date", "key", "id", "tip_utc"]].drop_duplicates(["date", "key"]).rename(columns={"id": "espn_id"}),
                on=["date", "key"], how="left")

    # ---- predictions log
    run_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    tip = g.tip_utc
    kind = np.where(tip.notna() & (tip > pd.Timestamp(now)), "prospective",
                    np.where(tip.isna() & (g.date > pd.Timestamp(today_et)), "prospective", "reconstruction"))
    horizon = pd.Timestamp(today_et) + pd.Timedelta(days=2)
    out = pd.DataFrame({
        "model": "frozen_v1", "run_ts_utc": run_ts, "kind": kind, "season": g.season, "muid": g.muid,
        "game_date": g.date.dt.strftime("%Y-%m-%d"), "team1_away": g.team1, "team2_home": g.team2,
        "neutral": g.neutral, "espn_id": g.espn_id, "tip_utc": g.tip_utc.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "signal": g.signal.round(3), "direction": g.direction,
        "ratings_snapshot": pd.concat([g.t1_tm_asof, g.t2_tm_asof], axis=1).max(axis=1).dt.strftime("%Y-%m-%d"),
        "t1_games_in_inputs": g.t1_s_gp, "t2_games_in_inputs": g.t2_s_gp,
    })
    out = out[g.signal.notna() & (g.date <= horizon)]
    pp = f"{FWD}/predictions.csv"
    old = pd.read_csv(pp, dtype=str) if os.path.exists(pp) else pd.DataFrame(columns=out.columns)
    # reconstructions are logged once; prospective predictions once per run date (inputs may update)
    seen_recon = set(old[old.kind == "reconstruction"].muid) | set(old[old.kind == "prospective"].muid)
    seen_pros = set(zip(old[old.kind == "prospective"].muid, old[old.kind == "prospective"].run_ts_utc.str[:10]))
    keep = [(k == "reconstruction" and m not in seen_recon) or (k == "prospective" and (m, run_ts[:10]) not in seen_pros)
            for k, m in zip(out.kind, out.muid)]
    new = out[keep]
    new.to_csv(pp, mode="a", header=not os.path.exists(pp), index=False)

    # ---- lines log (every book row, stamped with when we saw it)
    rows = []
    tipmap = ev.set_index("id").tip_utc
    for eid in g.espn_id.dropna().unique():
        for o in odds.get(eid) or []:
            pre = tipmap.get(eid) > pd.Timestamp(now)
            rows.append({"obs_ts_utc": run_ts, "espn_id": eid, "observed": "pre_tip" if pre else "post_game",
                         "provider": o["provider"], "total": o["ou"], "over_odds": o["over_odds"], "under_odds": o["under_odds"],
                         "open_total": o["open"]["total"], "open_over": o["open"]["over"], "open_under": o["open"]["under"],
                         "close_total": o["close"]["total"], "close_over": o["close"]["over"], "close_under": o["close"]["under"]})
    ln = pd.DataFrame(rows)
    lp = f"{FWD}/lines.csv"
    if len(ln):
        if os.path.exists(lp):
            oldl = pd.read_csv(lp, dtype=str)
            post_seen = set(zip(oldl[oldl.observed == "post_game"].espn_id, oldl[oldl.observed == "post_game"].provider))
            ln = ln[[not (o == "post_game" and (str(e), p) in post_seen) for o, e, p in zip(ln.observed, ln.espn_id, ln.provider)]]
        ln.to_csv(lp, mode="a", header=not os.path.exists(lp), index=False)
    print(f"run {run_ts}: scored {int(g.signal.notna().sum())} games; logged {len(new)} predictions "
          f"({int((new.kind=='prospective').sum())} prospective, {int((new.kind=='reconstruction').sum())} reconstruction), "
          f"{len(ln)} line rows; unmatched to ESPN among logged: {int(new.espn_id.isna().sum())}")
    pros = new[(new.kind == "prospective") & (new.direction != "")]
    if len(pros):
        print(pros[["game_date", "team1_away", "team2_home", "signal", "direction", "tip_utc"]].to_string(index=False))


if __name__ == "__main__":
    main(*[int(x) for x in sys.argv[1:]])
