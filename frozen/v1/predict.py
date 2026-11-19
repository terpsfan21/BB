"""FROZEN v1 scorer.  signal = predicted (actual total - closing total), centred.
Bet rule under test: OVER if signal >= +1.5, UNDER if signal <= -1.5, otherwise no bet."""
import json
import os

import numpy as np
import pandas as pd

from features import model_features

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = json.load(open(os.path.join(HERE, "model.json")))


def score(g):
    """g: one row per game with the pregame columns described in MODEL_CARD.md.
    Returns DataFrame[signal, direction]; signal is NaN if any input is missing."""
    F = model_features(g, MODEL["lgm"])[MODEL["features"]]
    z = (F - pd.Series(MODEL["mean"])) / pd.Series(MODEL["sd"])
    raw = MODEL["intercept"] + z.values @ np.array([MODEL["coef"][c] for c in MODEL["features"]])
    sig = pd.Series(raw - MODEL["centre"], index=g.index)
    sig[F.isna().any(axis=1)] = np.nan
    th = MODEL["threshold"]
    return pd.DataFrame({"signal": sig, "direction": np.where(sig >= th, "OVER", np.where(sig <= -th, "UNDER", ""))})
