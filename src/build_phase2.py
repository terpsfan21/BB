"""Phase-2 research tables (the phase-1 games.parquet is frozen training data and is NOT rebuilt).

  data/processed/p2_games.parquet   one row per game: venue, tournament note, half scores, market
                                    spread, opening total (best available source), conference info
  data/processed/odds_books.parquet one row per game x sportsbook: last/close total, prices, open
"""
import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
NOT_A_BOOK = re.compile(r"accuscore|numberfire|teamrankings|live|fantasy911|unknown", re.I)
MAJORS = {"ACC", "B10", "B12", "BE", "P12", "SEC"}


def main():
    g = pd.read_parquet(f"{OUT}/games.parquet")
    ev_rows, book_rows = [], []
    for y in range(2015, 2027):
        events = json.load(open(f"{RAW}/espn2/events_{y}.json"))
        odds = json.load(open(f"{RAW}/espn2/odds_{y}.json"))
        for e in events:
            hh, ah = e.get("home_halves") or [], e.get("away_halves") or []
            r = {"season": y, "espn_id": e["id"], "tip_utc": e["date_utc"], "espn_neutral": e.get("neutral"),
                 "venue_id": e.get("venue_id"), "venue": e.get("venue"), "venue_city": e.get("venue_city"),
                 "venue_state": e.get("venue_state"), "note": e.get("note"), "attendance": e.get("attendance"),
                 "h1_total": (hh[0] + ah[0]) if len(hh) >= 2 and len(ah) >= 2 and hh[0] is not None and ah[0] is not None else np.nan,
                 "h2_total": (hh[1] + ah[1]) if len(hh) >= 2 and len(ah) >= 2 and hh[1] is not None and ah[1] is not None else np.nan}
            spreads, opening = [], (np.nan, np.nan, np.nan)
            for o in odds.get(e["id"]) or []:
                name = o.get("provider") or ""
                if name.lower() == "opening":
                    opening = (o.get("ou"), o.get("over_odds"), o.get("under_odds"))
                    continue
                if NOT_A_BOOK.search(name):
                    continue
                c = o["close"]["total"] if o["close"]["total"] is not None else o.get("ou")
                if c is None or not (80 <= c <= 250):
                    continue
                has_close = o["close"]["total"] is not None
                book_rows.append({
                    "season": y, "espn_id": e["id"], "book": name, "total": c,
                    "over_odds": o["close"]["over"] if has_close else o.get("over_odds"),
                    "under_odds": o["close"]["under"] if has_close else o.get("under_odds"),
                    "is_close_field": has_close,
                    "open_total": o["open"]["total"], "open_over": o["open"]["over"], "open_under": o["open"]["under"]})
                if o.get("spread") is not None and name.lower() != "consensus":
                    spreads.append(abs(o["spread"]))
            r["mkt_spread_abs"] = float(np.median(spreads)) if spreads else np.nan
            r["espn_opening_total"], r["espn_opening_over"], r["espn_opening_under"] = opening
            ev_rows.append(r)
    ev = pd.DataFrame(ev_rows)
    books = pd.DataFrame(book_rows)
    for c in ("over_odds", "under_odds", "open_over", "open_under", "open_total", "total"):
        books[c] = pd.to_numeric(books[c], errors="coerce")
    books.loc[~books.open_total.between(80, 250), ["open_total", "open_over", "open_under"]] = np.nan
    bk = books[books.book.str.lower() != "consensus"]
    agg = bk.groupby(["season", "espn_id"]).agg(
        n_books=("total", "size"), book_min=("total", "min"), book_max=("total", "max"), book_med=("total", "median"),
        n_open_books=("open_total", "count"), open_min=("open_total", "min"), open_max=("open_total", "max"),
        open_med=("open_total", "median")).reset_index()
    p2 = g[["season", "muid", "espn_id"]].merge(ev, on=["season", "espn_id"], how="left").merge(
        agg, on=["season", "espn_id"], how="left")

    # conference labels from the raw Torvik schedule ("B12 vs. P12", "MWC at MWC")
    conf = []
    for y in range(2015, 2027):
        d = pd.read_csv(f"{RAW}/torvik/sked/{y}.csv", header=None, usecols=[0, 2])
        sp = d[2].astype(str).str.split(r" at | vs\. ", regex=True)
        conf.append(pd.DataFrame({"season": y, "muid": d[0], "t1_conf": sp.str[0], "t2_conf": sp.str[-1]}))
    p2 = p2.merge(pd.concat(conf).drop_duplicates(["season", "muid"]), on=["season", "muid"], how="left")
    p2["majors"] = p2.t1_conf.isin(MAJORS).astype(int) + p2.t2_conf.isin(MAJORS).astype(int)

    # opening total: SBR archive (2014-15..2020-21), else ESPN "Opening" row, else median of per-book opens
    p2 = p2.merge(g[["season", "muid", "sbr_open"]], on=["season", "muid"], how="left")
    p2["open_total"] = p2.sbr_open.fillna(p2.espn_opening_total).fillna(p2.open_med)
    p2["open_source"] = np.where(p2.sbr_open.notna(), "sbr", np.where(p2.espn_opening_total.notna(), "espn_opening_row",
                                 np.where(p2.open_med.notna(), "espn_book_median", None)))
    p2.loc[~p2.open_total.between(80, 250), ["open_total", "open_source"]] = [np.nan, None]
    p2 = p2.drop(columns=["sbr_open"])
    p2.to_parquet(f"{OUT}/p2_games.parquet", index=False, compression="zstd")
    books.to_parquet(f"{OUT}/odds_books.parquet", index=False, compression="zstd")
    print("p2_games", p2.shape, "odds_books", books.shape)
    print(p2.groupby("season").agg(n=("muid", "size"), venue=("venue_id", "count"), halves=("h1_total", "count"),
                                   spread=("mkt_spread_abs", "count"), open=("open_total", "count"),
                                   books_med=("n_books", "median"), open_books=("n_open_books", "median")))
    print(p2.groupby(["season", "open_source"]).size().unstack(fill_value=0))
    print(books.groupby("season").apply(lambda d: pd.Series({"books": d.book.nunique(), "price_rows": d.over_odds.notna().sum(), "open_rows": d.open_total.notna().sum()})))


if __name__ == "__main__":
    main()
