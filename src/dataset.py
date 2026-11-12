"""Load CAMELS-IND into one clean table: one row per (gauge_id, date).

The loader looks for files by name and content rather than fixed paths, because the
zip layout can differ between releases:
  * attribute files:  camels_ind_<group>.csv or camels_India_<group>.csv
  * forcing:          per-gauge files containing a 'prcp' column, OR one wide file per variable
  * streamflow:       a file with 'streamflow'/'discharge' in its name (wide: dates x gauges,
                      or per-gauge files), excluding simulated/LSTM-predicted flow
Run src/explore.py first if this raises an error, and adjust the patterns below.
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import yaml

ATTR_RE = re.compile(r"camels_(ind|india)_(name|topo|clim|hydro|land|soil|geol|anth)", re.I)
SIM_WORDS = ("pred", "sim", "lstm", "model")


# ---------------------------------------------------------------- helpers
def read_table(path):
    df = pd.read_csv(path, low_memory=False)
    if df.shape[1] == 1:
        df = pd.read_csv(path, sep=r"\s+", low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def add_date(df):
    low = {c.lower(): c for c in df.columns}
    if "date" in low:
        d = pd.to_datetime(df[low["date"]], errors="coerce")
    elif {"year", "month", "day"} <= set(low):
        d = pd.to_datetime(dict(year=df[low["year"]], month=df[low["month"]], day=df[low["day"]]), errors="coerce")
    elif {"yr", "mnth", "dy"} <= set(low):
        d = pd.to_datetime(dict(year=df[low["yr"]], month=df[low["mnth"]], day=df[low["dy"]]), errors="coerce")
    else:
        d = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    if d.notna().mean() < 0.9:
        raise ValueError("could not find a date column")
    df = df.copy()
    df["date"] = d
    drop = [low[k] for k in ("year", "month", "day", "yr", "mnth", "dy", "hr") if k in low and low[k] != "date"]
    return df.drop(columns=drop)


def gauge_from_filename(path):
    nums = re.findall(r"\d+", os.path.basename(path))
    return str(int(max(nums, key=len))) if nums else None


def norm_id(x):
    s = str(x).strip()
    return str(int(float(s))) if re.fullmatch(r"\d+(\.0+)?", s) else s


def is_gauge_col(c):
    return re.fullmatch(r"\d+(\.0+)?", str(c).strip()) is not None


# ---------------------------------------------------------------- attributes
def load_attributes(data_dir, groups):
    files = [f for f in glob.glob(os.path.join(data_dir, "**", "*.*"), recursive=True) if ATTR_RE.search(os.path.basename(f))]
    names, static = None, []
    for f in files:
        grp = ATTR_RE.search(os.path.basename(f)).group(2).lower()
        df = read_table(f)
        idcol = next((c for c in df.columns if "gauge" in c.lower() or c.lower() in ("id", "gauge_id")), df.columns[0])
        df = df.rename(columns={idcol: "gauge_id"})
        df["gauge_id"] = df["gauge_id"].map(norm_id)
        df = df.drop_duplicates("gauge_id").set_index("gauge_id")
        if grp == "name":
            names = df
        elif grp in groups:
            num = df.select_dtypes("number").add_prefix(f"{grp}_")
            static.append(num)
    if not static:
        raise FileNotFoundError("No attribute files found. Run src/explore.py and check file names.")
    attrs = pd.concat(static, axis=1)
    attrs = attrs.loc[:, attrs.isna().mean() < 0.2]
    attrs = attrs.loc[:, attrs.std() > 0]
    attrs = attrs.fillna(attrs.median())
    return attrs, names


# ---------------------------------------------------------------- streamflow
def load_streamflow(data_dir):
    cand = [f for f in glob.glob(os.path.join(data_dir, "**", "*.*"), recursive=True)
            if f.lower().endswith((".csv", ".txt"))
            and any(w in os.path.basename(f).lower() for w in ("streamflow", "discharge", "flow_observed", "obs_q"))
            and not any(w in os.path.basename(f).lower() for w in SIM_WORDS)]
    if not cand:
        raise FileNotFoundError("No streamflow file found. Run src/explore.py and check file names.")
    frames = []
    if len(cand) <= 3:  # wide table(s): dates x gauges
        for f in cand:
            df = add_date(read_table(f))
            gcols = [c for c in df.columns if is_gauge_col(c)]
            if len(gcols) < 5:
                continue
            long = df.melt(id_vars="date", value_vars=gcols, var_name="gauge_id", value_name="q")
            frames.append(long)
    if not frames:  # per-gauge files
        for f in cand:
            g = gauge_from_filename(f)
            df = add_date(read_table(f))
            qcol = next((c for c in df.columns if re.search(r"streamflow|discharge|^q", c, re.I)), None)
            qcol = qcol or df.select_dtypes("number").columns[-1]
            frames.append(pd.DataFrame({"date": df["date"], "gauge_id": g, "q": df[qcol]}))
    q = pd.concat(frames, ignore_index=True)
    q["gauge_id"] = q["gauge_id"].map(norm_id)
    q["q"] = pd.to_numeric(q["q"], errors="coerce")
    q.loc[q["q"] < 0, "q"] = np.nan
    return q.drop_duplicates(["gauge_id", "date"])


# ---------------------------------------------------------------- forcing
def load_forcing(data_dir, features):
    files = [f for f in glob.glob(os.path.join(data_dir, "**", "*.*"), recursive=True) if f.lower().endswith((".csv", ".txt"))]
    per_gauge, wide = [], {}
    for f in files:
        base = os.path.basename(f).lower()
        if ATTR_RE.search(base) or "streamflow" in base:
            continue
        try:
            head = read_table(f).head(0) if os.path.getsize(f) < 5e8 else None
        except Exception:
            continue
        if head is None:
            continue
        cols = [c.lower() for c in head.columns]
        if "prcp" in cols:
            per_gauge.append(f)
        else:
            stem = os.path.splitext(base)[0]
            var = next((v for v in features if re.search(rf"(^|_){v}($|_)", stem)), None)
            if var and sum(is_gauge_col(c) for c in head.columns) >= 5:
                wide[var] = f

    if per_gauge:
        frames = []
        for f in per_gauge:
            df = add_date(read_table(f))
            df.columns = [c.lower() if c != "date" else c for c in df.columns]
            keep = ["date"] + [c for c in features if c in df.columns]
            gid = df["gauge_id"].map(norm_id) if "gauge_id" in df.columns else gauge_from_filename(f)
            frames.append(df[keep].assign(gauge_id=gid))
        forc = pd.concat(frames, ignore_index=True)
    elif wide:
        forc = None
        for var, f in wide.items():
            df = add_date(read_table(f))
            gcols = [c for c in df.columns if is_gauge_col(c)]
            long = df.melt(id_vars="date", value_vars=gcols, var_name="gauge_id", value_name=var)
            long["gauge_id"] = long["gauge_id"].map(norm_id)
            forc = long if forc is None else forc.merge(long, on=["gauge_id", "date"], how="outer")
    else:
        raise FileNotFoundError("No forcing files found. Run src/explore.py and check file names.")
    forc["gauge_id"] = forc["gauge_id"].map(norm_id)
    return forc.drop_duplicates(["gauge_id", "date"])


# ---------------------------------------------------------------- main build
def build(cfg_path="configs/step1.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    d = cfg["data"]
    print("Loading attributes ...")
    attrs, names = load_attributes(d["data_dir"], d["static_groups"])
    print(f"  {attrs.shape[0]} gauges, {attrs.shape[1]} static attributes")
    print("Loading streamflow ...")
    q = load_streamflow(d["data_dir"])
    print(f"  {q['gauge_id'].nunique()} gauges with streamflow")
    print("Loading forcing ...")
    forc = load_forcing(d["data_dir"], d["dynamic_features"])
    feats = [c for c in d["dynamic_features"] if c in forc.columns]
    print(f"  features found: {feats}")

    df = forc.merge(q, on=["gauge_id", "date"], how="left")
    df = df[(df["date"] >= d["train"][0]) & (df["date"] <= d["test"][1])]
    df = df[df["gauge_id"].isin(attrs.index)]
    df = df.sort_values(["gauge_id", "date"]).reset_index(drop=True)

    # fill short gaps in forcing (<=5 days); flow is left as observed
    df[feats] = df.groupby("gauge_id")[feats].transform(lambda s: s.interpolate(limit=5, limit_direction="both"))

    # quality screen
    tr = df[(df["date"] >= d["train"][0]) & (df["date"] <= d["train"][1])]
    te = df[(df["date"] >= d["test"][0]) & (df["date"] <= d["test"][1])]
    ok_train = tr.groupby("gauge_id")["q"].count() >= d["min_train_years"] * 365
    ok_test = te.groupby("gauge_id")["q"].count() >= d["min_test_days"]
    keep = sorted(set(ok_train[ok_train].index) & set(ok_test[ok_test].index))
    if d.get("max_gauges"):
        focus = find_focus(names, d.get("focus_gauge_name"))
        keep = ([focus] if focus in keep else []) + [g for g in keep if g != focus][: d["max_gauges"] - 1]
    df = df[df["gauge_id"].isin(keep)].dropna(subset=feats)
    print(f"Kept {len(keep)} gauges after quality screening, {len(df):,} rows")

    os.makedirs(os.path.dirname(d["processed_file"]), exist_ok=True)
    df.to_parquet(d["processed_file"], index=False)
    attrs.loc[keep].to_parquet(d["processed_file"].replace(".parquet", "_static.parquet"))
    if names is not None:
        names.to_parquet(d["processed_file"].replace(".parquet", "_names.parquet"))
    return df, attrs.loc[keep], names


def find_focus(names, word):
    if names is None or not word:
        return None
    hit = names.apply(lambda r: r.astype(str).str.contains(word, case=False).any(), axis=1)
    return hit[hit].index[0] if hit.any() else None


def load_processed(cfg):
    p = cfg["data"]["processed_file"]
    df = pd.read_parquet(p)
    static = pd.read_parquet(p.replace(".parquet", "_static.parquet"))
    npath = p.replace(".parquet", "_names.parquet")
    names = pd.read_parquet(npath) if os.path.exists(npath) else None
    return df, static, names


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
