"""Multi-basin LSTM baseline: 90 days of inputs -> discharge for the next 1..7 days.

Trained on all kept CAMELS-IND gauges together (one shared model), as recommended by
Kratzert et al. (2019, 2024). Saves test-period predictions to results/lstm_test_predictions.parquet.
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from dataset import load_processed  # noqa: E402


class Windows:
    """Holds per-gauge arrays and builds (input window, target) samples on the fly."""

    def __init__(self, df, static, feats, cfg):
        d, m = cfg["data"], cfg["model"]
        self.L, self.H = m["lookback"], m["horizon"]
        train = df[(df.date >= d["train"][0]) & (df.date <= d["train"][1])]
        self.f_mean, self.f_std = train[feats].mean(), train[feats].std().replace(0, 1)
        ly = np.log1p(train["q"])
        self.y_mean, self.y_std = float(ly.mean()), float(ly.std())
        s = static.loc[sorted(df.gauge_id.unique())]
        self.s_norm = ((s - s.mean()) / s.std().replace(0, 1)).fillna(0)

        self.gauges, self.X, self.Y, self.D = [], [], [], []
        for g, gd in df.groupby("gauge_id", sort=True):
            gd = gd.set_index("date").asfreq("D")  # make daily index continuous
            x = ((gd[feats] - self.f_mean) / self.f_std).astype("float32")
            y = ((np.log1p(gd["q"]) - self.y_mean) / self.y_std).astype("float32").values
            stat = np.repeat(self.s_norm.loc[g].values[None, :].astype("float32"), len(gd), axis=0)
            yin = np.nan_to_num(y, nan=0.0)[:, None]
            ymask = np.isfinite(y).astype("float32")[:, None]
            X = np.concatenate([x.values, yin, ymask, stat], axis=1)
            self.gauges.append(g)
            self.X.append(np.nan_to_num(X))
            self.Y.append(y)
            self.D.append(gd.index.values)
        self.n_in = self.X[0].shape[1]

    def index(self, start, end, need_all_targets=True):
        """All (gauge, t) where t is the last input day and t+1 falls in [start, end]."""
        out = []
        s, e = np.datetime64(start), np.datetime64(end)
        for gi, (Y, D, X) in enumerate(zip(self.Y, self.D, self.X)):
            T = len(Y)
            t = np.arange(self.L - 1, T - self.H)
            nxt = D[t + 1]
            t = t[(nxt >= s) & (nxt <= e)]
            if need_all_targets:
                fut = np.stack([Y[t + h] for h in range(1, self.H + 1)], 1)
                t = t[np.isfinite(fut).all(1)]
            else:
                t = t[np.isfinite(Y[t + 1])]
            # skip windows whose forcing was missing (rows were dropped -> all-zero after asfreq)
            out.append(np.stack([np.full(len(t), gi), t], 1))
        return np.concatenate(out).astype(np.int64)

    def batch(self, idx):
        xs = np.stack([self.X[g][t - self.L + 1: t + 1] for g, t in idx])
        ys = np.stack([self.Y[g][t + 1: t + self.H + 1] for g, t in idx])
        return torch.from_numpy(xs), torch.from_numpy(ys)

    def to_q(self, y_norm):
        return np.expm1(y_norm * self.y_std + self.y_mean)


class LSTMModel(nn.Module):
    def __init__(self, n_in, hidden, horizon, dropout):
        super().__init__()
        self.lstm = nn.LSTM(n_in, hidden, batch_first=True)
        self.drop = nn.Dropout(dropout)
        self.head = nn.Linear(hidden, horizon)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(self.drop(out[:, -1]))


def masked_mse(pred, y):
    m = torch.isfinite(y)
    return ((pred[m] - y[m]) ** 2).mean()


def run(cfg_path="configs/step1.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    d, c = cfg["data"], cfg["lstm"]
    torch.manual_seed(0)
    np.random.seed(0)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device:", dev)

    df, static, _ = load_processed(cfg)
    feats = [f for f in d["dynamic_features"] if f in df.columns]
    W = Windows(df, static, feats, cfg)
    tr_idx = W.index(*d["train"])
    va_idx = W.index(*d["val"])
    te_idx = W.index(*d["test"], need_all_targets=False)
    print(f"Samples  train {len(tr_idx):,}  val {len(va_idx):,}  test {len(te_idx):,}  inputs per day {W.n_in}")

    model = LSTMModel(W.n_in, c["hidden"], cfg["model"]["horizon"], c["dropout"]).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"])
    sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5, patience=2)
    va_sub = va_idx[np.random.choice(len(va_idx), min(50000, len(va_idx)), replace=False)]

    best, best_state, wait = np.inf, None, 0
    for ep in range(1, c["epochs"] + 1):
        t0 = time.time()
        model.train()
        pick = tr_idx[np.random.choice(len(tr_idx), min(c["samples_per_epoch"], len(tr_idx)), replace=False)]
        losses = []
        for i in range(0, len(pick), c["batch_size"]):
            x, y = W.batch(pick[i: i + c["batch_size"]])
            x, y = x.to(dev), y.to(dev)
            loss = masked_mse(model(x), y)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            losses.append(loss.item())
        model.eval()
        with torch.no_grad():
            vl = []
            for i in range(0, len(va_sub), 2048):
                x, y = W.batch(va_sub[i: i + 2048])
                vl.append(masked_mse(model(x.to(dev)), y.to(dev)).item())
        vloss = float(np.mean(vl))
        sched.step(vloss)
        print(f"epoch {ep:2d}  train {np.mean(losses):.4f}  val {vloss:.4f}  ({time.time() - t0:.0f}s)")
        if vloss < best - 1e-4:
            best, wait = vloss, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= c["patience"]:
                print("Early stopping.")
                break
    model.load_state_dict(best_state)

    # predict the test period
    model.eval()
    rows = []
    with torch.no_grad():
        for i in range(0, len(te_idx), 2048):
            chunk = te_idx[i: i + 2048]
            x, y = W.batch(chunk)
            p = model(x.to(dev)).cpu().numpy()
            for h in range(cfg["model"]["horizon"]):
                tgt = chunk[:, 1] + h + 1
                rows.append(pd.DataFrame({
                    "gauge_id": [W.gauges[g] for g in chunk[:, 0]],
                    "date": [W.D[g][t] for g, t in zip(chunk[:, 0], tgt)],
                    "lead": h + 1,
                    "obs": W.to_q(y[:, h].numpy()),
                    "p50": W.to_q(p[:, h]),
                }))
    pred = pd.concat(rows, ignore_index=True)
    pred = pred[(pred.date >= d["test"][0]) & (pred.date <= d["test"][1])]
    os.makedirs(cfg["results_dir"], exist_ok=True)
    pred.to_parquet(os.path.join(cfg["results_dir"], "lstm_test_predictions.parquet"), index=False)
    torch.save(model.state_dict(), os.path.join(cfg["results_dir"], "lstm_model.pt"))
    print("Saved LSTM test predictions:", len(pred), "rows")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
