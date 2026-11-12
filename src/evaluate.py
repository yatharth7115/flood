"""Compare LSTM and TFT on the test period (2016-2020): metrics per gauge, summary table and plots."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from metrics import all_metrics  # noqa: E402
from dataset import find_focus  # noqa: E402


def per_gauge(pred, model):
    rows = []
    for (g, lead), gd in pred.groupby(["gauge_id", "lead"]):
        r = all_metrics(gd["obs"], gd["p50"])
        if "p10" in gd:
            r["P10-P90 coverage%"] = 100 * np.mean((gd["obs"] >= gd["p10"]) & (gd["obs"] <= gd["p90"]))
        rows.append({"model": model, "gauge_id": g, "lead": lead, **r})
    return pd.DataFrame(rows)


def run(cfg_path="configs/step1.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    R = cfg["results_dir"]
    preds = {}
    for name in ("LSTM", "TFT"):
        p = os.path.join(R, f"{name.lower()}_test_predictions.parquet")
        if os.path.exists(p):
            preds[name] = pd.read_parquet(p)
            preds[name]["gauge_id"] = preds[name]["gauge_id"].astype(str)
    if not preds:
        raise FileNotFoundError("No prediction files found. Run the training scripts first.")

    # compare on the same gauges and dates only
    if len(preds) == 2:
        keys = preds["LSTM"][["gauge_id", "date", "lead"]].merge(preds["TFT"][["gauge_id", "date", "lead"]])
        preds = {k: v.merge(keys) for k, v in preds.items()}

    m = pd.concat([per_gauge(v, k) for k, v in preds.items()], ignore_index=True)
    m.to_csv(os.path.join(R, "metrics_per_gauge.csv"), index=False)

    cols = ["NSE", "KGE", "RMSE", "PeakErr%"] + (["P10-P90 coverage%"] if "P10-P90 coverage%" in m else [])
    summary = m[m.lead.isin([1, 3, 7])].groupby(["lead", "model"])[cols].median().round(3)
    summary.to_csv(os.path.join(R, "metrics_summary.csv"))

    names_p = cfg["data"]["processed_file"].replace(".parquet", "_names.parquet")
    names = pd.read_parquet(names_p) if os.path.exists(names_p) else None
    focus = find_focus(names, cfg["data"].get("focus_gauge_name"))

    lines = ["# Step 1 results: LSTM vs TFT (CAMELS-IND, test period 2016-2020)", "",
             f"Gauges compared: {m.gauge_id.nunique()}", "",
             "Median across gauges (discharge, m3/s):", "", summary.to_markdown(), ""]
    if focus is not None and focus in set(m.gauge_id):
        fm = m[(m.gauge_id == focus) & (m.lead.isin([1, 3, 7]))].set_index(["lead", "model"])[cols].round(3)
        lines += [f"Focus gauge ({cfg['data']['focus_gauge_name']}, id {focus}):", "", fm.to_markdown(), ""]
    open(os.path.join(R, "summary.md"), "w").write("\n".join(lines))
    print("\n".join(lines))

    # plot 1: NSE distribution across gauges (lead 1)
    fig, ax = plt.subplots(figsize=(6, 4))
    for name in preds:
        v = np.sort(m[(m.model == name) & (m.lead == 1)]["NSE"].dropna().clip(-1, 1))
        ax.plot(v, np.linspace(0, 1, len(v)), label=name)
    ax.set_xlabel("NSE (1-day ahead, test period)")
    ax.set_ylabel("Fraction of gauges")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(R, "nse_cdf.png"), dpi=150)

    # plot 2: hydrograph at the focus gauge (or best-observed gauge) for its wettest test year
    g = focus if focus in set(m.gauge_id) else m.gauge_id.mode()[0]
    base = list(preds.values())[0]
    gd = base[(base.gauge_id == g) & (base.lead == 1)].dropna(subset=["obs"])
    year = pd.to_datetime(gd.loc[gd.obs.idxmax(), "date"]).year
    fig, ax = plt.subplots(figsize=(10, 4))
    for name, p in preds.items():
        x = p[(p.gauge_id == g) & (p.lead == 1)].copy()
        x["date"] = pd.to_datetime(x["date"])
        x = x[x.date.dt.year == year].sort_values("date")
        if name == list(preds)[0]:
            ax.plot(x.date, x.obs, color="black", lw=1.5, label="Observed")
        ax.plot(x.date, x.p50, lw=1.2, label=f"{name} (1-day ahead)")
        if "p10" in x:
            ax.fill_between(x.date, x.p10, x.p90, alpha=0.2, label=f"{name} P10-P90")
    ax.set_ylabel("Discharge (m3/s)")
    ax.set_title(f"Gauge {g}, {year}")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(R, "hydrograph_focus.png"), dpi=150)

    # plot 3: TFT variable importance
    vi = os.path.join(R, "tft_variable_importance.csv")
    if os.path.exists(vi):
        v = pd.read_csv(vi)
        v = v[v.type == "encoder"].sort_values("importance_%").tail(12)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(v.variable, v["importance_%"])
        ax.set_xlabel("Importance (%)")
        ax.set_title("TFT: most important past inputs")
        fig.tight_layout()
        fig.savefig(os.path.join(R, "tft_variable_importance.png"), dpi=150)
    print("Saved metrics and plots to", R)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
