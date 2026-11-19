"""Download raw Torvik files: season schedules (with frozen pregame lines), per-game
box stats, player-season stats and daily point-in-time ("time machine") ratings.

Usage: python src/fetch_torvik.py [first_season] [last_season]   (season = ending year)
"""
import datetime as dt
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "torvik")
UA = {"User-Agent": "Mozilla/5.0"}
BASE = "https://barttorvik.com"


def get(url, path, min_bytes=200):
    if os.path.exists(path) and os.path.getsize(path) >= min_bytes:
        return "cached"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            body = urllib.request.urlopen(req, timeout=90).read()
            if len(body) < min_bytes:
                return "missing"
            with open(path, "wb") as f:
                f.write(body)
            return "ok"
        except urllib.error.HTTPError as e:
            if e.code in (302, 404):
                return "missing"
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return "failed"


def main(first=2015, last=2026):
    for sub in ("sked", "gamestats", "players", "tm"):
        os.makedirs(os.path.join(RAW, sub), exist_ok=True)
    jobs = []
    for y in range(first, last + 1):
        jobs.append((f"{BASE}/{y}_super_sked.csv", f"{RAW}/sked/{y}.csv"))
        jobs.append((f"{BASE}/getgamestats.php?year={y}&csv=1", f"{RAW}/gamestats/{y}.csv"))
    for y in range(first - 1, last + 1):
        jobs.append((f"{BASE}/getadvstats.php?year={y}&csv=1", f"{RAW}/players/{y}.csv"))
    for y in range(first, last + 1):
        d, end = dt.date(y - 1, 11, 1), dt.date(y, 4, 10)
        while d <= end:
            s = d.strftime("%Y%m%d")
            jobs.append((f"{BASE}/timemachine/team_results/{s}_team_results.json.gz", f"{RAW}/tm/{s}.json.gz"))
            d += dt.timedelta(days=1)
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda j: get(*j), jobs))
    print({k: res.count(k) for k in set(res)})


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:]]
    main(*a)
