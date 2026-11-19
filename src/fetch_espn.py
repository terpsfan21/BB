"""Download ESPN scoreboards (event ids, teams, scores) and per-event sportsbook odds.

Output: data/raw/espn/events_{season}.json  (list of events)
        data/raw/espn/odds_{season}.json    ({event_id: [provider rows]})
Usage: python src/fetch_espn.py [first_season] [last_season]
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "espn")
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


def num(x):
    if isinstance(x, dict):
        for k in ("american", "alternateDisplayValue", "displayValue"):
            try:
                return float(x[k])
            except (KeyError, TypeError, ValueError):
                pass
    return None


def day_events(d):
    js = fetch(SB.format(d=d.strftime("%Y%m%d")))
    out = []
    if not isinstance(js, dict):
        return out
    for ev in js.get("events", []):
        c = ev["competitions"][0]
        if not c["status"]["type"].get("completed"):
            continue
        row = {"id": ev["id"], "date_utc": ev["date"], "neutral": c.get("neutralSite"),
               "period": c["status"].get("period")}
        for t in c["competitors"]:
            p = t["homeAway"]
            row[p] = t["team"].get("location") or t["team"].get("displayName")
            row[p + "_id"] = t["team"]["id"]
            row[p + "_score"] = t.get("score")
        out.append(row)
    return out


def event_odds(i):
    js = fetch(ODDS.format(i=i))
    if js == "FAILED":
        return i, "FAILED"
    rows = []
    for it in (js or {}).get("items", []):
        rows.append({
            "provider": it.get("provider", {}).get("name"),
            "ou": it.get("overUnder"), "spread": it.get("spread"),
            "open_total": num((it.get("open") or {}).get("total")),
            "close_total": num((it.get("close") or {}).get("total")),
        })
    return i, rows


def main(first=2015, last=2026):
    os.makedirs(RAW, exist_ok=True)
    for y in range(first, last + 1):
        ep, op = f"{RAW}/events_{y}.json", f"{RAW}/odds_{y}.json"
        if os.path.exists(ep):
            events = json.load(open(ep))
        else:
            days, d = [], dt.date(y - 1, 11, 1)
            while d <= dt.date(y, 4, 10):
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
        n = sum(1 for v in odds.values() if v)
        print(y, "events", len(events), "odds fetched", len(odds), "with lines", n, flush=True)


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:]]
    main(*a)
