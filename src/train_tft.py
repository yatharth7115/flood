"""Temporal Fusion Transformer on the same gauges, inputs and periods as the LSTM.

Outputs P10 / P50 / P90 discharge for 1..7 days ahead and the input importance learned by
the variable selection networks. Saves results/tft_test_predictions.parquet and
results/tft_variable_importance.csv.
"""
import argparse
import os
import re
import sys

import numpy as np
import pandas as pd
import torch
import yaml
import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss

sys.path.insert(0, os.path.dirname(__file__))
from dataset import load_processed  # noqa: E402


def prepare(cfg, extra=(), peak_weight=0.0):
    d = cfg["data"]
    df, static, _ = load_processed(cfg)
    feats = [f for f in d["dynamic_features"] if f in df.columns]
    known = ["doy_sin", "doy_cos"]
    if extra or peak_weight:
        from features import add_features
        groups = [g for g in extra if g != "future_rain"]  # TFT takes future rain as a known input instead
        df, new, cn2 = add_features(df, static, groups, cfg.get("peak_quantile", 0.95), d["train"][1])
        feats += new
        if "cn" in extra:
            static = static.assign(phys_cn=cn2.reindex(static.index))
    if "future_rain" in extra:
        df["prcp_fcst"] = df["prcp"].astype("float32")  # observed future rain = perfect forecast (upper bound)
        known.append("prcp_fcst")
    df["w"] = (1.0 + peak_weight * (df["q"] > df["q_thr"]).astype("float32")) if peak_weight else 1.0
    static = static.copy()
    static.columns = [re.sub(r"[^0-9a-zA-Z_]", "_", c) for c in static.columns]
    static_cols = list(static.columns)
    static = ((static - static.mean()) / static.std().replace(0, 1)).fillna(0)
    df = df.merge(static, left_on="gauge_id", right_index=True, how="left")
    df = df.dropna(subset=["q"]).copy()
    t0 = pd.Timestamp(d["train"][0])
    df["time_idx"] = (df["date"] - t0).dt.days.astype(int)
    doy = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.25).astype("float32")
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.25).astype("float32")
    df["gauge_id"] = df["gauge_id"].astype(str)
    idx = lambda s: int((pd.Timestamp(s) - t0).days)  # noqa: E731
    return df, feats, static_cols, idx, known


def run(cfg_path="configs/step1.yaml", name="TFT", extra=(), peak_weight=0.0):
    cfg = yaml.safe_load(open(cfg_path))
    d, c, m = cfg["data"], cfg["tft"], cfg["model"]
    pl.seed_everything(0)
    df, feats, static_cols, idx, known = prepare(cfg, extra, peak_weight)
    print(f"Model {name}: extra={list(extra)} peak_weight={peak_weight} dynamic={len(feats)} known={known}")
    L, H = m["lookback"], m["horizon"]

    training = TimeSeriesDataSet(
        df[df.time_idx <= idx(d["train"][1])],
        time_idx="time_idx", target="q", group_ids=["gauge_id"],
        max_encoder_length=L, min_encoder_length=L // 2, max_prediction_length=H,
        static_reals=static_cols,
        time_varying_known_reals=known,
        weight="w" if peak_weight else None,
        time_varying_unknown_reals=["q"] + feats,
        target_normalizer=GroupNormalizer(groups=["gauge_id"], transformation="softplus"),
        add_relative_time_idx=True, add_target_scales=True, allow_missing_timesteps=True,
    )
    validation = TimeSeriesDataSet.from_dataset(
        training, df[df.time_idx <= idx(d["val"][1])], min_prediction_idx=idx(d["val"][0]), stop_randomization=True)
    test = TimeSeriesDataSet.from_dataset(
        training, df, min_prediction_idx=idx(d["test"][0]), stop_randomization=True)

    nw = 4
    train_dl = training.to_dataloader(train=True, batch_size=c["batch_size"], num_workers=nw)
    val_dl = validation.to_dataloader(train=False, batch_size=c["batch_size"] * 4, num_workers=nw)
    test_dl = test.to_dataloader(train=False, batch_size=c["batch_size"] * 4, num_workers=nw)
    print(f"Windows  train {len(training):,}  val {len(validation):,}  test {len(test):,}")

    tft = TemporalFusionTransformer.from_dataset(
        training, learning_rate=c["lr"], hidden_size=c["hidden"], attention_head_size=c["attention_heads"],
        dropout=c["dropout"], hidden_continuous_size=max(8, c["hidden"] // 2),
        loss=QuantileLoss(c["quantiles"]), reduce_on_plateau_patience=2, log_interval=-1,
    )
    ckpt = ModelCheckpoint(monitor="val_loss", mode="min", save_top_k=1, dirpath=os.path.join(cfg["results_dir"], f"{name.lower()}_ckpt"))
    trainer = pl.Trainer(
        max_epochs=c["epochs"], accelerator="auto", devices=1, gradient_clip_val=0.1,
        limit_train_batches=c["train_batches_per_epoch"], limit_val_batches=300,
        callbacks=[EarlyStopping(monitor="val_loss", patience=c["patience"]), ckpt],
        enable_model_summary=False, logger=False,
    )
    trainer.fit(tft, train_dataloaders=train_dl, val_dataloaders=val_dl)
    best = TemporalFusionTransformer.load_from_checkpoint(ckpt.best_model_path)

    # ---- test predictions (quantiles)
    pred = best.predict(test_dl, mode="quantiles", return_index=True, trainer_kwargs=dict(accelerator="auto", devices=1, logger=False))
    out = pred.output.cpu().numpy()  # (N, H, n_quantiles)
    ind = pred.index.reset_index(drop=True)
    obs = df.set_index(["gauge_id", "time_idx"])[["q", "date"]]
    rows = []
    for h in range(H):
        key = pd.MultiIndex.from_arrays([ind["gauge_id"].astype(str), ind["time_idx"] + h])
        o = obs.reindex(key)
        rows.append(pd.DataFrame({
            "gauge_id": ind["gauge_id"].astype(str).values, "date": o["date"].values, "lead": h + 1,
            "obs": o["q"].values, "p10": out[:, h, 0], "p50": out[:, h, 1], "p90": out[:, h, 2],
        }))
    res = pd.concat(rows, ignore_index=True).dropna(subset=["obs"])
    res = res[(res.date >= d["test"][0]) & (res.date <= d["test"][1])]
    os.makedirs(cfg["results_dir"], exist_ok=True)
    res.to_parquet(os.path.join(cfg["results_dir"], f"{name.lower()}_test_predictions.parquet"), index=False)
    print(f"Saved {name} test predictions:", len(res), "rows")

    # ---- which inputs mattered (variable selection weights), from a random sample of test windows.
    # Done batch by batch so memory stays small (the full raw output does not fit in RAM).
    try:
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        best = best.to(dev).eval()
        dl = test.to_dataloader(train=False, batch_size=256, num_workers=nw, shuffle=True)
        acc = {}
        with torch.no_grad():
            for i, (x, _) in enumerate(dl):
                if i >= 80:  # about 20,000 windows
                    break
                x = {k: (v.to(dev) if torch.is_tensor(v) else v) for k, v in x.items()}
                interp = best.interpret_output(best(x), reduction="sum")
                for kind in ("static", "encoder", "decoder"):
                    w = interp[f"{kind}_variables"].detach().cpu().numpy()
                    acc[kind] = acc.get(kind, 0) + w
        imp = []
        for kind, names in [("static", best.static_variables), ("encoder", best.encoder_variables), ("decoder", best.decoder_variables)]:
            w = acc[kind]
            w = 100 * w / w.sum()
            imp += [{"type": kind, "variable": n, "importance_%": float(v)} for n, v in zip(names, w)]
        pd.DataFrame(imp).sort_values(["type", "importance_%"], ascending=[True, False]).to_csv(
            os.path.join(cfg["results_dir"], f"{name.lower()}_variable_importance.csv"), index=False)
        print("Saved variable importance.")
    except Exception as e:  # interpretation is a bonus; do not fail the run
        print("Variable importance skipped:", e)
    finally:
        import shutil
        shutil.rmtree(os.path.join(cfg["results_dir"], f"{name.lower()}_ckpt"), ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?", default="configs/step1.yaml")
    ap.add_argument("--name", default="TFT")
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--peak-weight", type=float, default=0.0)
    a = ap.parse_args()
    run(a.config, a.name, a.extra, a.peak_weight)
