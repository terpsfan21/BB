"""Phase-2 ESPN collector: richer event fields (venue, tournament note, half scores) and
per-sportsbook totals WITH prices and open/close where ESPN publishes them.

Output: data/raw/espn2/events_{season}.json, data/raw/espn2/odds_{season}.json
Usage:  python src/fetch_espn_v2.py [first_season] [last_season] [--refresh-last-days N]
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "espn2")
SB = ("https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/"
      "scoreboard?dates={d}&groups=50&limit=500")
ODDS = ("https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/"
        "events/{i}/competitions/{i}/odds?limit=50")


def fetch(url):
    for attempt in range(5):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=40).read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1.5 ** attempt)
        except Exception:
            time.sleep(1.5 ** attempt)
    return "FAILED"


def num(x, keys=("american", "alternateDisplayValue", "displayValue")):
    if isinstance(x, dict):
        for k in keys:
            try:
                return float(str(x[k]).replace("EVEN", "100").replace("+", ""))
            except (KeyError, TypeError, ValueError):
                pass
    return None


def day_events(d, completed_only=True):
    js = fetch(SB.format(d=d.strftime("%Y%m%d")))
    out = []
    if not isinstance(js, dict):
        return out
    for ev in js.get("events", []):
        c = ev["competitions"][0]
        done = bool(c["status"]["type"].get("completed"))
        if completed_only and not done:
            continue
        v = c.get("venue") or {}
        row = {"id": ev["id"], "date_utc": ev["date"], "completed": done, "neutral": c.get("neutralSite"),
               "conf_game": c.get("conferenceCompetition"), "period": c["status"].get("period"),
               "venue_id": v.get("id"), "venue": v.get("fullName"),
               "venue_city": (v.get("address") or {}).get("city"), "venue_state": (v.get("address") or {}).get("state"),
               "note": "; ".join(n.get("headline", "") for n in c.get("notes", []) if n.get("headline")),
               "attendance": c.get("attendance")}
        for t in c["competitors"]:
            p = t["homeAway"]
            row[p] = t["team"].get("location") or t["team"].get("displayName")
            row[p + "_id"] = t["team"]["id"]
            row[p + "_score"] = t.get("score")
            row[p + "_halves"] = [l.get("value") for l in t.get("linescores", [])]
        out.append(row)
    return out


def side(o, k):
    b = o.get(k) or {}
    return {"total": num(b.get("total")), "over": num(b.get("over")), "under": num(b.get("under"))}


def event_odds(i):
    js = fetch(ODDS.format(i=i))
    if js == "FAILED":
        return i, "FAILED"
    rows = []
    for it in (js or {}).get("items", []):
        rows.append({"provider": it.get("provider", {}).get("name"), "ou": it.get("overUnder"),
                     "spread": it.get("spread"), "over_odds": it.get("overOdds"), "under_odds": it.get("underOdds"),
                     "open": side(it, "open"), "close": side(it, "close")})
    return i, rows


def main(first=2015, last=2027):
    os.makedirs(RAW, exist_ok=True)
    today = dt.date.today()
    for y in range(first, last + 1):
        ep, op = f"{RAW}/events_{y}.json", f"{RAW}/odds_{y}.json"
        end = min(dt.date(y, 4, 10), today)
        if os.path.exists(ep) and end < today:
            events = json.load(open(ep))
        else:
            days, d = [], dt.date(y - 1, 11, 1)
            while d <= end:
                days.append(d)
                d += dt.timedelta(days=1)
            with ThreadPoolExecutor(12) as ex:
                events = [e for lst in ex.map(day_events, days) for e in lst]
            events = list({e["id"]: e for e in events}.values())
            json.dump(events, open(ep, "w"))
        odds = json.load(open(op)) if os.path.exists(op) else {}
        todo = [e["id"] for e in events if e["id"] not in odds]
        with ThreadPoolExecutor(24) as ex:
            for i, rows in ex.map(event_odds, todo):
                if rows != "FAILED":
                    odds[i] = rows
        json.dump(odds, open(op, "w"))
        print(y, "events", len(events), "odds", len(odds), "with lines", sum(1 for v in odds.values() if v), flush=True)


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:]]
    main(*a)
