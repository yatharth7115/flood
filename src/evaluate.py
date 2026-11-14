"""Compare all models that saved <name>_test_predictions.parquet in results_dir, on the test period.

Optional: --reference results/step1/metrics_per_gauge.csv adds earlier results (e.g. Step 1) to the
summary tables as "<model>_STEP1" rows, for the same gauges.
"""
import argparse
import glob
import os
import re
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

COLS = ["NSE", "KGE", "RMSE", "PeakErr%", "P10-P90 coverage%"]


def dedupe(v):
    """One row per (gauge, date, lead). The TFT can predict the same target date twice around data gaps."""
    cols = [c for c in ("obs", "p10", "p50", "p90") if c in v]
    return v.groupby(["gauge_id", "date", "lead"], as_index=False)[cols].mean()


def per_gauge(pred, model):
    rows = []
    for (g, lead), gd in pred.groupby(["gauge_id", "lead"]):
        r = all_metrics(gd["obs"], gd["p50"])
        if "p10" in gd:
            r["P10-P90 coverage%"] = 100 * np.mean((gd["obs"] >= gd["p10"]) & (gd["obs"] <= gd["p90"]))
        rows.append({"model": model, "gauge_id": g, "lead": lead, **r})
    return pd.DataFrame(rows)


def run(cfg_path="configs/step1.yaml", reference=None, plot_models=None, ref_tag="STEP1"):
    cfg = yaml.safe_load(open(cfg_path))
    R = cfg["results_dir"]
    preds = {}
    for p in sorted(glob.glob(os.path.join(R, "*_test_predictions.parquet"))):
        name = os.path.basename(p).replace("_test_predictions.parquet", "").upper()
        v = pd.read_parquet(p)
        v["gauge_id"] = v["gauge_id"].astype(str)
        v["date"] = pd.to_datetime(v["date"])
        preds[name] = dedupe(v.dropna(subset=["obs"]))
    if not preds:
        raise FileNotFoundError("No prediction files found. Run the training scripts first.")
    print("Models found:", list(preds))

    # compare every model on the same gauges, dates and leads
    keys = None
    for v in preds.values():
        k = v[["gauge_id", "date", "lead"]]
        keys = k if keys is None else keys.merge(k)
    preds = {k: v.merge(keys) for k, v in preds.items()}

    # seed ensembles: models named <BASE>_S<n> with 2+ seeds -> <BASE>_ENS (mean of the seeds' predictions)
    groups = {}
    for k in preds:
        mt = re.match(r"(.+)_S\d+$", k)
        if mt:
            groups.setdefault(mt.group(1), []).append(k)
    for base_name, members in groups.items():
        if len(members) < 2:
            continue
        cols = [c for c in ("p10", "p50", "p90") if all(c in preds[x] for x in members)]
        ens = preds[members[0]][["gauge_id", "date", "lead", "obs"]].copy()
        for c in cols:
            ens[c] = sum(preds[x][c].values for x in members) / len(members)
        preds[f"{base_name}_ENS"] = ens

    m = pd.concat([per_gauge(v, k) for k, v in preds.items()], ignore_index=True)
    if reference and os.path.exists(reference):
        ref = pd.read_csv(reference)
        ref["gauge_id"] = ref["gauge_id"].astype(str)
        ref = ref[ref.gauge_id.isin(set(m.gauge_id))]
        ref = ref[ref.lead.isin(set(m.lead))]
        ref["model"] = ref["model"].astype(str) + f"_{ref_tag}"
        m = pd.concat([m, ref], ignore_index=True)
    m.to_csv(os.path.join(R, "metrics_per_gauge.csv"), index=False)

    cols = [c for c in COLS if c in m and m[c].notna().any()]
    summary = m[m.lead.isin([1, 3, 7])].groupby(["lead", "model"])[cols].median().round(3)
    summary.to_csv(os.path.join(R, "metrics_summary.csv"))

    # spread across seeds: mean and std of the per-seed median NSE
    seed_rows = []
    for base_name, members in groups.items():
        if len(members) < 2:
            continue
        med = m[m.model.isin(members) & m.lead.isin([1, 3, 7])].groupby(["lead", "model"])["NSE"].median().unstack()
        for lead, row in med.iterrows():
            seed_rows.append({"model": base_name, "lead": lead, "seeds": len(members),
                              "median NSE mean": round(row.mean(), 3), "std across seeds": round(row.std(), 3)})
    seed_tab = pd.DataFrame(seed_rows)

    # share of gauges where each model beats the first baseline at lead 1
    base = "LSTM_BASE" if "LSTM_BASE" in set(m.model) else sorted(set(m.model))[0]
    l1 = m[m.lead == 1].pivot_table(index="gauge_id", columns="model", values="NSE")
    wins = ((l1.sub(l1[base], axis=0) > 0).mean() * 100).round(0).drop(base, errors="ignore")

    names_p = cfg["data"]["processed_file"].replace(".parquet", "_names.parquet")
    names = pd.read_parquet(names_p) if os.path.exists(names_p) else None
    focus = find_focus(names, cfg["data"].get("focus_gauge_name"))

    lines = [f"# Results on the test period ({cfg['data']['test'][0]} to {cfg['data']['test'][1]})", "",
             f"Gauges compared: {m.gauge_id.nunique()}", "",
             "Median across gauges (discharge, m3/s):", "", summary.to_markdown(), "",
             f"Share of gauges with higher 1-day NSE than {base} (%):", "", wins.to_frame("% gauges").to_markdown(), ""]
    if len(seed_tab):
        lines += ["Variation across random seeds (median NSE over gauges):", "", seed_tab.to_markdown(index=False), ""]
    if focus is not None and focus in set(m.gauge_id):
        fm = m[(m.gauge_id == focus) & (m.lead.isin([1, 3, 7]))].set_index(["lead", "model"])[cols].sort_index().round(3)
        lines += [f"Focus gauge ({cfg['data']['focus_gauge_name']}, id {focus}):", "", fm.to_markdown(), ""]
    open(os.path.join(R, "summary.md"), "w").write("\n".join(lines))
    print("\n".join(lines))

    show = [p for p in (plot_models or list(preds)) if p in preds][:4]

    # plot 1: NSE distribution across gauges (lead 1)
    fig, ax = plt.subplots(figsize=(6, 4))
    for name in show:
        v = np.sort(m[(m.model == name) & (m.lead == 1)]["NSE"].dropna().clip(-1, 1))
        ax.plot(v, np.linspace(0, 1, len(v)), label=name)
    ax.set_xlabel("NSE (1-day ahead, test period)")
    ax.set_ylabel("Fraction of gauges")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(R, "nse_cdf.png"), dpi=150)

    # plot 2: hydrograph at the focus gauge for its wettest test year
    g = focus if focus in set(m.gauge_id) else m.gauge_id.mode()[0]
    base_p = preds[show[0]]
    gd = base_p[(base_p.gauge_id == g) & (base_p.lead == 1)].dropna(subset=["obs"])
    year = pd.to_datetime(gd.loc[gd.obs.idxmax(), "date"]).year
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, name in enumerate(show):
        x = preds[name]
        x = x[(x.gauge_id == g) & (x.lead == 1)].copy()
        x["date"] = pd.to_datetime(x["date"])
        x = x[x.date.dt.year == year].sort_values("date")
        if i == 0:
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

    # plot 3: variable importance of each TFT that saved one
    for vi in glob.glob(os.path.join(R, "*_variable_importance.csv")):
        v = pd.read_csv(vi)
        v = v[v.type == "encoder"].sort_values("importance_%").tail(12)
        tag = os.path.basename(vi).replace("_variable_importance.csv", "")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(v.variable, v["importance_%"])
        ax.set_xlabel("Importance (%)")
        ax.set_title(f"{tag.upper()}: most important past inputs")
        fig.tight_layout()
        fig.savefig(os.path.join(R, f"{tag}_variable_importance.png"), dpi=150)
    print("Saved metrics and plots to", R)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?", default="configs/step1.yaml")
    ap.add_argument("--reference", default=None)
    ap.add_argument("--plot", nargs="*", default=None)
    ap.add_argument("--ref-tag", default="STEP1")
    a = ap.parse_args()
    run(a.config, a.reference, a.plot, a.ref_tag)
