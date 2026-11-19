"""FROZEN v1 feature code.  Do not edit: any change makes it a new model version.

Self-contained copy of the feature definitions used to train the factors-only market-error
model (repo commit 8527a46).  All data-dependent constants (league means used for shrinkage
and centring) are read from model.json so that adding new seasons cannot shift the features.
"""
import numpy as np
import pandas as pd

BOX = ["fgm", "fga", "tpm", "tpa", "ftm", "fta", "oreb", "dreb", "reb", "ast", "stl", "blk", "to", "pf", "pts"]
SUMS = ["n", "poss", "poss_40"] + BOX + ["o_" + b for b in BOX]


def style_features(g, m, K=4):
    """Season-to-date team rates from games strictly BEFORE each game's date, shrunk toward the
    frozen league means `m` with K pseudo-games.  `g` needs: season, date, muid, team1, team2,
    poss, poss_40 and box columns t1_*/t2_* (NaN for games not yet played).
    Rows without a box score contribute nothing but still receive features."""
    longs = []
    for me, opp in (("t1", "t2"), ("t2", "t1")):
        L = pd.DataFrame({"season": g.season.values, "date": g.date.values, "muid": g.muid.values,
                          "team": g["team1" if me == "t1" else "team2"].values,
                          "poss": g.poss.values, "poss_40": g.poss_40.values})
        for b in BOX:
            L[b] = g[f"{me}_{b}"].values
            L["o_" + b] = g[f"{opp}_{b}"].values
        L["side"] = me
        longs.append(L)
    L = pd.concat(longs, ignore_index=True)
    has_box = L.fga.notna() & L.o_fga.notna()
    L["n"] = has_box.astype(float)
    L.loc[~has_box, [c for c in SUMS if c != "n"]] = 0.0
    L[SUMS] = L[SUMS].fillna(0.0)
    daily = L.groupby(["season", "team", "date"])[SUMS].sum().groupby(level=[0, 1]).cumsum()
    prior = daily.groupby(level=[0, 1]).shift(1).fillna(0).reset_index()
    P = L[["season", "team", "date", "muid", "side"]].merge(prior, on=["season", "team", "date"], how="left")
    m = pd.Series(m)

    def shr(numer, denom):
        return (sum(P[c] for c in numer) + K * sum(m[c] for c in numer)) / \
               (sum(P[c] for c in denom) + K * sum(m[c] for c in denom))

    F = P[["season", "muid", "side"]].copy()
    F["gp"] = P.n
    F["pace"] = shr(["poss_40"], ["n"])
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
    feats = [c for c in F.columns if c not in ("season", "muid", "side")]
    out = g[["season", "muid"]].copy()
    for side in ("t1", "t2"):
        sub = F[F.side == side][["muid", "season"] + feats].rename(columns={c: f"{side}_s_{c}" for c in feats})
        out = out.merge(sub, on=["muid", "season"], how="left")
    return out


def model_features(g, lgm):
    """The 33 model inputs.  `g` needs t?_tm_adjt, t?_s_*, t?_ret_min, t?_new_coach, date."""
    f = pd.DataFrame(index=g.index)
    a1, a2 = g.t1_tm_adjt, g.t2_tm_adjt
    # centre tempo on the mean snapshot tempo of the teams playing that date
    lg = g.groupby("date")[["t1_tm_adjt", "t2_tm_adjt"]].transform("mean").mean(axis=1)
    f["pace_absdiff"] = (a1 - a2).abs()
    f["pace_sum"] = a1 + a2 - 2 * lg
    f["pace_inter"] = (a1 - lg) * (a2 - lg)
    f["pace_fast_slow"] = np.maximum(a1, a2) - lg
    f["pace_slow_side"] = np.minimum(a1, a2) - lg
    gp = np.minimum(g.t1_s_gp, g.t2_s_gp)
    early = np.exp(-gp / 6.0)
    turn = 1 - g[["t1_ret_min", "t2_ret_min"]].mean(axis=1)
    f["roster_turnover"] = turn
    f["roster_turnover_max"] = 1 - g[["t1_ret_min", "t2_ret_min"]].min(axis=1)
    f["roster_new_coach"] = g[["t1_new_coach", "t2_new_coach"]].sum(axis=1, min_count=2)
    f["roster_early"] = early
    f["roster_turnover_x_early"] = (turn - 0.5) * early
    f["roster_new_coach_x_early"] = f.roster_new_coach * early

    def s(name):
        return g[f"t1_s_{name}"] + g[f"t2_s_{name}"]

    for k in ("o_3par", "o_ftr", "o_orb", "o_tov", "o_ast", "o_3p_pct", "o_2p_pct", "o_ft_pct"):
        f["shot_" + k[2:]] = s(k)
    f["shot_3par_absdiff"] = (g.t1_s_o_3par - g.t2_s_o_3par).abs()
    for k in ("d_3par", "d_3p_pct", "d_ftr", "d_tov", "d_orb", "d_stl", "d_blk", "d_foul"):
        f["opp_" + k[2:]] = s(k)

    def cross(o, d):
        return ((g[f"t1_s_{o}"] - lgm[o]) * (g[f"t2_s_{d}"] - lgm[d]) +
                (g[f"t2_s_{o}"] - lgm[o]) * (g[f"t1_s_{d}"] - lgm[d]))

    f["opp_x_3par"] = cross("o_3par", "d_3par")
    f["opp_x_tov"] = cross("o_tov", "d_tov")
    f["opp_x_orb"] = cross("o_orb", "d_orb")
    f["opp_x_ftr"] = cross("o_ftr", "d_ftr")
    f["opp_x_pace_press"] = (a1 - lg) * (g.t2_s_d_tov - lgm["d_tov"]) + (a2 - lg) * (g.t1_s_d_tov - lgm["d_tov"])
    return f
