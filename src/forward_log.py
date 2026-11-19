"""Forward test of the FROZEN v1 model on the current season.  Runs unattended.

    python src/forward_log.py predict   # refresh Torvik, score games, log predictions
    python src/forward_log.py odds      # snapshot sportsbook totals, log changes + opportunities
    python src/forward_log.py all       # both (default)

The frozen model is a MARKET-ERROR signal (which side of a posted total is likely wrong), not a
projected total.  Nothing here refits or tunes it.

Append-only logs in data/forward/ (commit them: the git history is the timestamp audit trail)
  predictions.csv    one row per (game, run date).  kind = prospective if logged before tip-off.
  lines.csv          one row each time a book's total or price is first seen or CHANGES
                     (observed = pre_tip), plus one post-game row per book with the provider's own
                     open/close record (observed = post_game).
  polls.csv          one row per odds poll per source: proves the screen was checked at that time,
                     so a line with no newer row was unchanged as of the last poll.
  opportunities.csv  for games the frozen rule flags: the best available total/price across the
                     books seen, logged when first available and whenever the best number changes.

Odds sources
  espn       ESPN's public event odds feed (unofficial; currently DraftKings only).  Always on.
  oddsapi    The Odds API v4 (supported, keyed).  Used only if env ODDS_API_KEY is set.
             Regions via env ODDS_API_REGIONS (default "us").  1 credit per region per poll.
  kalshi     Kalshi's public market-data API (documented, no key).  Always on.  Each game is a
             ladder of "over X" contracts; the full ladder with bid/ask sizes goes to
             kalshi_ladder.csv (rows only when a quote changes) and the strike priced closest to
             50/50 goes into lines.csv as provider "Kalshi".  Prices exclude Kalshi's trading fee.

Not crawled, on purpose: 4codds.com and betwatch.io.  Both restrict automated collection (see
docs/DATA_SOURCES.md); they need the owner's permission first.
"""
import datetime as dt
import difflib
import glob
import gzip
import json
import os
import re
import sys
import urllib.parse
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
SEASON = 2027
DAYS_BACK, DAYS_AHEAD = 2, 4
LINE_COLS = ["obs_ts_utc", "source", "espn_id", "observed", "provider", "total", "over_odds", "under_odds",
             "open_total", "open_over", "open_under", "close_total", "close_over", "close_under", "book_last_update"]
NOT_A_BOOK = re.compile(r"live|accuscore|numberfire|teamrankings|consensus", re.I)


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def dl(url, path, required=True):
    try:
        body = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    except Exception as e:
        if required:
            raise RuntimeError(f"download failed: {url}: {e}")
        return False
    if len(body) > 200:
        open(path, "wb").write(body)
        return True
    if required:
        raise RuntimeError(f"download empty: {url}")
    return False


def read_log(name, cols=None):
    p = f"{FWD}/{name}"
    if os.path.exists(p):
        return pd.read_csv(p, dtype=str)
    return pd.DataFrame(columns=cols or [])


def append(name, df, cols):
    if len(df) == 0:
        return
    p = f"{FWD}/{name}"
    df[cols].to_csv(p, mode="a", header=not os.path.exists(p), index=False)


# ----------------------------------------------------------------------------- ESPN slate
def espn_window(today_et):
    """ESPN events from DAYS_BACK ago to DAYS_AHEAD ahead (completed or not)."""
    ev = []
    for k in range(-DAYS_BACK, DAYS_AHEAD + 1):
        ev += E2.day_events(today_et + dt.timedelta(days=k), completed_only=False)
    ev = pd.DataFrame(list({e["id"]: e for e in ev}.values()))
    if not len(ev):
        return ev
    ev["tip_utc"] = pd.to_datetime(ev.date_utc, utc=True)
    ev["date"] = ev.tip_utc.dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    ev["key"] = ["|".join(sorted([str(h), str(a)])) for h, a in zip(ev.home_id, ev.away_id)]
    return ev


def team_map():
    return pd.read_csv(os.path.join(ROOT, "data", "processed", "team_map.csv"), dtype={"espn_team_id": str})


# ----------------------------------------------------------------------------- predictions
def refresh_torvik(y, today):
    for sub in ("sked", "gamestats", "players", "tm"):
        os.makedirs(f"{RAW}/torvik/{sub}", exist_ok=True)
    dl(f"https://barttorvik.com/{y}_super_sked.csv", f"{RAW}/torvik/sked/{y}.csv")
    for yy in (y - 1, y):                                  # prior season needed for roster / coach flags
        for sub, url in (("gamestats", f"https://barttorvik.com/getgamestats.php?year={yy}&csv=1"),
                         ("players", f"https://barttorvik.com/getadvstats.php?year={yy}&csv=1")):
            p = f"{RAW}/torvik/{sub}/{yy}.csv"
            if yy == y or not os.path.exists(p):
                dl(url, p)
    d = max(dt.date(y - 1, 11, 1), today - dt.timedelta(days=14))    # only recent snapshots are ever used
    while d <= today:
        s = d.strftime("%Y%m%d")
        p = f"{RAW}/torvik/tm/{s}.json.gz"
        if not os.path.exists(p):
            dl(f"https://barttorvik.com/timemachine/team_results/{s}_team_results.json.gz", p, required=False)
        d += dt.timedelta(days=1)


def load_tm_recent(y):
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


def predict(y=SEASON):
    now = now_utc()
    today_et = pd.Timestamp(now).tz_convert("America/New_York").date()
    refresh_torvik(y, today_et)
    g = B.load_sked(y, played_only=False)
    st = FZ.style_features(g, PZ.MODEL["league_means_per_game"], PZ.MODEL["shrink_K"])
    g = g.merge(st, on=["muid", "season"], how="left")
    g = g[g.game_type != "non_d1"].copy()
    lo, hi = pd.Timestamp(today_et) - pd.Timedelta(days=DAYS_BACK), pd.Timestamp(today_et) + pd.Timedelta(days=DAYS_AHEAD)
    g = g[(g.date >= lo) & (g.date <= hi)].copy()
    if not len(g):
        print("predict: no games in window")
        return
    g = B.attach_tm(g, load_tm_recent(y))
    B.SEASONS = range(y, y + 1)
    ros, coach = B.roster_features(), B.coach_features()
    for side, key in (("t1", "team1"), ("t2", "team2")):
        r = ros.merge(coach, on=["season", "team"], how="outer")
        r = r.rename(columns={c: f"{side}_{c}" for c in r.columns if c not in ("season", "team")}).rename(columns={"team": key})
        g = g.merge(r, on=["season", key], how="left")
    g = g.reset_index(drop=True)
    # day-level tempo centring needs each full day's slate, which the window filter preserves
    sc = PZ.score(g)
    g["signal"], g["direction"] = sc.signal.values, sc.direction.values

    tmap = team_map().set_index("team").espn_team_id.astype(str)
    ev = espn_window(today_et)
    g["key"] = ["|".join(sorted([tmap.get(a, "?" + a), tmap.get(b, "?" + b)])) for a, b in zip(g.team1, g.team2)]
    if len(ev):
        g = g.merge(ev[["date", "key", "id", "tip_utc"]].drop_duplicates(["date", "key"]).rename(columns={"id": "espn_id"}),
                    on=["date", "key"], how="left")
    else:
        g["espn_id"], g["tip_utc"] = None, pd.NaT
    run_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    tip = pd.to_datetime(g.tip_utc, utc=True)
    kind = np.where(tip.notna() & (tip > pd.Timestamp(now)), "prospective",
                    np.where(tip.isna() & (g.date > pd.Timestamp(today_et)), "prospective", "reconstruction"))
    out = pd.DataFrame({
        "model": "frozen_v1", "run_ts_utc": run_ts, "kind": kind, "season": g.season, "muid": g.muid,
        "game_date": g.date.dt.strftime("%Y-%m-%d"), "team1_away": g.team1, "team2_home": g.team2,
        "neutral": g.neutral, "espn_id": g.espn_id, "tip_utc": tip.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "signal": g.signal.round(3), "direction": g.direction,
        "ratings_snapshot": pd.concat([g.t1_tm_asof, g.t2_tm_asof], axis=1).max(axis=1).dt.strftime("%Y-%m-%d"),
        "t1_games_in_inputs": g.t1_s_gp, "t2_games_in_inputs": g.t2_s_gp,
    })
    out = out[g.signal.notna().values]
    cols = list(out.columns)
    old = read_log("predictions.csv", cols)
    seen_any = set(old.muid)
    seen_pros = set(zip(old[old.kind == "prospective"].muid, old[old.kind == "prospective"].run_ts_utc.str[:10]))
    keep = [(k == "reconstruction" and m not in seen_any) or (k == "prospective" and (m, run_ts[:10]) not in seen_pros)
            for k, m in zip(out.kind, out.muid)]
    new = out[keep]
    os.makedirs(FWD, exist_ok=True)
    append("predictions.csv", new.copy(), cols)
    print(f"predict {run_ts}: window games {len(g)}, scored {int(g.signal.notna().sum())}, logged {len(new)} "
          f"({int((new.kind=='prospective').sum())} prospective, {int((new.kind=='reconstruction').sum())} reconstruction), "
          f"flagged prospective {int(((new.kind=='prospective') & (new.direction!='')).sum())}, "
          f"no ESPN match {int(new.espn_id.isna().sum())}")


# ----------------------------------------------------------------------------- odds sources
def espn_lines(ev, now, known_post):
    """Current ESPN odds rows for events not yet tipped, and one post-game record per finished event."""
    rows = []
    run_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    for _, e in ev.iterrows():
        pre = e.tip_utc > pd.Timestamp(now)
        if not pre and (not e.completed or e.id in known_post):
            continue                                        # in progress, or already recorded
        i, odds = E2.event_odds(e.id)
        if odds == "FAILED":
            continue
        for o in odds:
            name = o.get("provider") or ""
            if NOT_A_BOOK.search(name) or o.get("ou") is None:
                continue
            rows.append({"obs_ts_utc": run_ts, "source": "espn", "espn_id": e.id, "observed": "pre_tip" if pre else "post_game",
                         "provider": name, "total": o["ou"], "over_odds": o["over_odds"], "under_odds": o["under_odds"],
                         "open_total": o["open"]["total"], "open_over": o["open"]["over"], "open_under": o["open"]["under"],
                         "close_total": o["close"]["total"], "close_over": o["close"]["over"], "close_under": o["close"]["under"],
                         "book_last_update": ""})
    return rows


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower().replace("&", "and").replace("st.", "state")).strip()


def oddsapi_lines(ev, now):
    """The Odds API v4, totals market.  Returns (rows, credits_remaining).  Needs ODDS_API_KEY."""
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        return [], None
    regions = os.environ.get("ODDS_API_REGIONS") or "us"
    url = ("https://api.the-odds-api.com/v4/sports/basketball_ncaab/odds?" +
           urllib.parse.urlencode({"apiKey": key, "regions": regions, "markets": "totals", "oddsFormat": "american"}))
    resp = urllib.request.urlopen(url, timeout=60)
    remaining = resp.headers.get("x-requests-remaining")
    data = json.loads(resp.read())
    run_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    cand = ev.assign(hn=ev.home_name.map(norm), an=ev.away_name.map(norm)) if len(ev) else ev
    rows = []
    for g in data:
        tip = pd.Timestamp(g["commence_time"])
        if tip <= pd.Timestamp(now):
            continue                                        # pre-game numbers only
        eid = "oddsapi:" + g["id"]
        if len(cand):
            c = cand[(cand.tip_utc - tip).abs() <= pd.Timedelta(hours=3)]
            best, score = None, 0.0
            for _, e in c.iterrows():
                s = min(difflib.SequenceMatcher(None, norm(g["home_team"]), e.hn).ratio(),
                        difflib.SequenceMatcher(None, norm(g["away_team"]), e.an).ratio())
                if s > score:
                    best, score = e.id, s
            if best is not None and score >= 0.8:
                eid = best
        for bk in g.get("bookmakers", []):
            for m in bk.get("markets", []):
                if m.get("key") != "totals":
                    continue
                oc = {o["name"]: o for o in m.get("outcomes", [])}
                if "Over" not in oc or "Under" not in oc:
                    continue
                rows.append({"obs_ts_utc": run_ts, "source": "oddsapi", "espn_id": eid, "observed": "pre_tip",
                             "provider": bk.get("title") or bk.get("key"), "total": oc["Over"].get("point"),
                             "over_odds": oc["Over"].get("price"), "under_odds": oc["Under"].get("price"),
                             "open_total": "", "open_over": "", "open_under": "", "close_total": "", "close_over": "",
                             "close_under": "", "book_last_update": m.get("last_update") or bk.get("last_update") or ""})
    return rows, remaining


KALSHI = "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXNCAAMBTOTAL&status=open&limit=1000"
KALSHI_COLS = ["obs_ts_utc", "espn_id", "event_ticker", "ticker", "strike", "yes_bid", "yes_ask", "no_bid", "no_ask",
               "yes_bid_size", "yes_ask_size", "volume", "open_interest", "market_created_utc", "market_updated_utc"]


def american(p):
    """American odds for buying a $1-payout contract at price p (fees excluded)."""
    if not (0 < p < 1):
        return None
    return round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)


def kalshi_lines(ev, now):
    """Returns (summary rows for lines.csv, ladder rows for kalshi_ladder.csv, n_events)."""
    markets, cursor = [], ""
    for _ in range(10):
        req = urllib.request.Request(KALSHI + (f"&cursor={cursor}" if cursor else ""), headers={"Accept": "application/json"})
        d = json.loads(urllib.request.urlopen(req, timeout=60).read())
        markets += d.get("markets", [])
        cursor = d.get("cursor") or ""
        if not cursor:
            break
    run_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    cand = ev.assign(hn=ev.home.map(norm), an=ev.away.map(norm)) if len(ev) else ev

    def f(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return np.nan

    by_event = {}
    for m in markets:
        by_event.setdefault(m["event_ticker"], []).append(m)
    lines, ladder = [], []
    for et, ms in by_event.items():
        tip = pd.Timestamp(ms[0].get("occurrence_datetime") or ms[0].get("expected_expiration_time"))
        if tip <= pd.Timestamp(now):
            continue                                        # pre-game quotes only
        mt = re.search(r"in the (.+?) vs\.? (.+?) men's college basketball game", ms[0].get("rules_primary") or "")
        eid = "kalshi:" + et
        if mt and len(cand):
            a, b = norm(mt.group(1)), norm(mt.group(2))
            c = cand[(cand.tip_utc - tip).abs() <= pd.Timedelta(hours=4)]
            best, score = None, 0.0
            for _, e in c.iterrows():
                sm = difflib.SequenceMatcher
                sc = max(min(sm(None, a, e.an).ratio(), sm(None, b, e.hn).ratio()),
                         min(sm(None, a, e.hn).ratio(), sm(None, b, e.an).ratio()))
                if sc > score:
                    best, score = e.id, sc
            if best is not None and score >= 0.85:
                eid = best
        main = None
        for m in ms:
            yb, ya, nb, na = f(m.get("yes_bid_dollars")), f(m.get("yes_ask_dollars")), f(m.get("no_bid_dollars")), f(m.get("no_ask_dollars"))
            ladder.append({"obs_ts_utc": run_ts, "espn_id": eid, "event_ticker": et, "ticker": m["ticker"], "strike": m.get("floor_strike"),
                           "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na,
                           "yes_bid_size": f(m.get("yes_bid_size_fp")), "yes_ask_size": f(m.get("yes_ask_size_fp")),
                           "volume": f(m.get("volume_fp")), "open_interest": f(m.get("open_interest_fp")),
                           "market_created_utc": m.get("created_time", ""), "market_updated_utc": m.get("updated_time", "")})
            two_sided = yb > 0 and nb > 0 and 0 < ya < 1 and 0 < na < 1 and (ya - yb) <= 0.10
            if two_sided:
                mid = (yb + ya) / 2
                if main is None or abs(mid - 0.5) < main[0]:
                    main = (abs(mid - 0.5), m, ya, na)
        if main is not None and main[0] <= 0.10:            # a strike priced within 40-60%
            _, m, ya, na = main
            lines.append({"obs_ts_utc": run_ts, "source": "kalshi", "espn_id": eid, "observed": "pre_tip", "provider": "Kalshi",
                          "total": m.get("floor_strike"), "over_odds": american(ya), "under_odds": american(na),
                          "open_total": "", "open_over": "", "open_under": "", "close_total": "", "close_over": "", "close_under": "",
                          "book_last_update": m.get("updated_time", "")})
    return lines, ladder, len(by_event)


def payout(a):
    a = float(a)
    return a / 100.0 if a > 0 else 100.0 / abs(a)


def odds():
    now = now_utc()
    today_et = pd.Timestamp(now).tz_convert("America/New_York").date()
    os.makedirs(FWD, exist_ok=True)
    run_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ev = espn_window(today_et)
    old = read_log("lines.csv", LINE_COLS)
    if len(old) and "source" not in old.columns:           # one-time schema upgrade of the first day's log
        old["source"], old["book_last_update"] = "espn", ""
        old[LINE_COLS].to_csv(f"{FWD}/lines.csv", index=False)
    known_post = set(old[old.observed == "post_game"].espn_id) if len(old) else set()
    polls = []
    rows = espn_lines(ev, now, known_post) if len(ev) else []
    polls.append({"obs_ts_utc": run_ts, "source": "espn", "events_checked": len(ev), "pre_tip_lines": sum(r["observed"] == "pre_tip" for r in rows),
                  "note": ""})
    try:
        r2, remaining = oddsapi_lines(ev, now)
        if remaining is not None or r2:
            polls.append({"obs_ts_utc": run_ts, "source": "oddsapi", "events_checked": len({r["espn_id"] for r in r2}),
                          "pre_tip_lines": len(r2), "note": f"credits_remaining={remaining}"})
        rows += r2
    except Exception as e:                                  # a failed keyed source must not stop the free one
        polls.append({"obs_ts_utc": run_ts, "source": "oddsapi", "events_checked": 0, "pre_tip_lines": 0, "note": f"error: {str(e)[:80]}"})
    try:
        r3, lad, nev = kalshi_lines(ev, now)
        rows += r3
        lad = pd.DataFrame(lad, columns=KALSHI_COLS)
        oldk = read_log("kalshi_ladder.csv", KALSHI_COLS)
        if len(lad):
            q = ["yes_bid", "yes_ask", "no_bid", "no_ask"]
            lastq = {}
            if len(oldk):
                ol = oldk.sort_values("obs_ts_utc").drop_duplicates("ticker", keep="last")
                lastq = {r.ticker: tuple(round(float(getattr(r, c)), 4) if str(getattr(r, c)) not in ("", "nan") else None for c in q) for r in ol.itertuples()}
            cur_q = [tuple(None if pd.isna(getattr(r, c)) else round(float(getattr(r, c)), 4) for c in q) for r in lad.itertuples()]
            keepk = [lastq.get(t) != cq for t, cq in zip(lad.ticker, cur_q)]
            append("kalshi_ladder.csv", lad[keepk].copy(), KALSHI_COLS)
        matched = sum(not str(r["espn_id"]).startswith("kalshi:") for r in r3)
        polls.append({"obs_ts_utc": run_ts, "source": "kalshi", "events_checked": nev, "pre_tip_lines": len(r3),
                      "note": f"matched_to_games={matched}"})
    except Exception as e:
        polls.append({"obs_ts_utc": run_ts, "source": "kalshi", "events_checked": 0, "pre_tip_lines": 0, "note": f"error: {str(e)[:80]}"})
    append("polls.csv", pd.DataFrame(polls), ["obs_ts_utc", "source", "events_checked", "pre_tip_lines", "note"])

    cur = pd.DataFrame(rows, columns=LINE_COLS)
    # log a pre-tip row only when that book's number or price is new or changed
    if len(cur):
        last = (old[old.observed == "pre_tip"].sort_values("obs_ts_utc").drop_duplicates(["source", "espn_id", "provider"], keep="last")
                if len(old) else old)
        lastkey = {(r.source, str(r.espn_id), r.provider): (float(r.total), str(r.over_odds), str(r.under_odds)) for r in last.itertuples()} if len(last) else {}

        def changed(r):
            if r.observed != "pre_tip":
                return True
            k = lastkey.get((r.source, str(r.espn_id), r.provider))
            def f(v):
                try:
                    return str(float(v))
                except (TypeError, ValueError):
                    return str(v)
            return k is None or (float(r.total), f(r.over_odds), f(r.under_odds)) != (k[0], f(k[1]), f(k[2]))
        new = cur[[changed(r) for r in cur.itertuples()]]
        append("lines.csv", new.copy(), LINE_COLS)
    else:
        new = cur

    # ---- opportunities: flagged prospective games x best number currently on the screen
    pred = read_log("predictions.csv")
    n_opp = 0
    if len(pred) and len(cur):
        p = pred[(pred.kind == "prospective") & pred.direction.isin(["OVER", "UNDER"])].sort_values("run_ts_utc")
        p = p.drop_duplicates("muid", keep="last")          # latest pre-tip signal for the game
        live = cur[cur.observed == "pre_tip"].copy()
        live["total"] = pd.to_numeric(live.total, errors="coerce")
        opp = []
        for r in p.itertuples():
            L = live[live.espn_id.astype(str) == str(r.espn_id)].dropna(subset=["total"])
            if not len(L):
                continue
            over = r.direction == "OVER"
            L = L.assign(price=pd.to_numeric(L.over_odds if over else L.under_odds, errors="coerce")).dropna(subset=["price"])
            if not len(L):
                continue
            L = L.sort_values(["total", "price"], ascending=[over, False])     # over: lowest total; under: highest
            b = L.iloc[0]
            opp.append({"obs_ts_utc": run_ts, "muid": r.muid, "espn_id": r.espn_id, "game_date": r.game_date, "team1_away": r.team1_away,
                        "team2_home": r.team2_home, "tip_utc": r.tip_utc, "signal": r.signal, "direction": r.direction,
                        "signal_logged_utc": r.run_ts_utc, "best_book": b.provider, "best_source": b.source, "best_total": b.total,
                        "best_price": b.price, "books_seen": len(L), "median_total": L.total.median(),
                        "worst_total": L.total.max() if over else L.total.min()})
        opp = pd.DataFrame(opp)
        oc = ["obs_ts_utc", "muid", "espn_id", "game_date", "team1_away", "team2_home", "tip_utc", "signal", "direction", "signal_logged_utc",
              "best_book", "best_source", "best_total", "best_price", "books_seen", "median_total", "worst_total"]
        if len(opp):
            prev = read_log("opportunities.csv", oc)
            lastb = {}
            if len(prev):
                pl = prev.sort_values("obs_ts_utc").drop_duplicates("muid", keep="last")
                lastb = {r.muid: (r.best_book, float(r.best_total), float(r.best_price), r.direction) for r in pl.itertuples()}
            keep = [lastb.get(r.muid) != (r.best_book, float(r.best_total), float(r.best_price), r.direction) for r in opp.itertuples()]
            append("opportunities.csv", opp[keep].copy(), oc)
            n_opp = int(sum(keep))
    print(f"odds {run_ts}: events {len(ev)}, lines seen {len(cur)}, new/changed logged {len(new)}, opportunity rows {n_opp}; "
          + "; ".join(f"{q['source']}: {q['pre_tip_lines']} pre-tip {q['note']}" for q in polls))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("predict", "all"):
        predict()
    if mode in ("odds", "all"):
        odds()
