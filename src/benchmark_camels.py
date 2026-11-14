"""Benchmark: the LSTM streamflow predictions published with CAMELS-IND (lstm_pred_streamflow.csv).

Saved as results/camels_lstm_test_predictions.parquet (same prediction for every lead), so evaluate.py
can compare it on the same gauges and dates. Caveat: it is a simulation model (no past discharge input)
and its training years are those of the dataset paper, which may overlap our test years.
"""
import glob
import os
import sys

import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from dataset import add_date, is_gauge_col, load_processed, norm_id, read_table  # noqa: E402


def run(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    d = cfg["data"]
    files = [f for f in glob.glob(os.path.join(d["data_dir"], "**", "*.csv"), recursive=True) if "lstm_pred" in os.path.basename(f).lower()]
    if not files:
        print("No lstm_pred file found in the data; benchmark skipped.")
        return
    raw = add_date(read_table(files[0]))
    gcols = [c for c in raw.columns if is_gauge_col(c)]
    sim = raw.melt(id_vars="date", value_vars=gcols, var_name="gauge_id", value_name="p50")
    sim["gauge_id"] = sim["gauge_id"].map(norm_id)
    df, _, _ = load_processed(cfg)
    obs = df[(df.date >= d["test"][0]) & (df.date <= d["test"][1])][["gauge_id", "date", "q"]].dropna()
    obs["gauge_id"] = obs["gauge_id"].astype(str)
    m = obs.merge(sim, on=["gauge_id", "date"]).rename(columns={"q": "obs"}).dropna(subset=["p50"])
    out = pd.concat([m.assign(lead=h) for h in range(1, cfg["model"]["horizon"] + 1)], ignore_index=True)
    os.makedirs(cfg["results_dir"], exist_ok=True)
    out[["gauge_id", "date", "lead", "obs", "p50"]].to_parquet(
        os.path.join(cfg["results_dir"], "camels_lstm_test_predictions.parquet"), index=False)
    print(f"CAMELS-IND LSTM benchmark: {m.gauge_id.nunique()} gauges, {len(m):,} days")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
