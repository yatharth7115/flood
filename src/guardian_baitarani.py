"""Find Baitarani stations in the GUARDIAN dataset (Patidar, Indu & Karmakar, Scientific Data 2024).

GUARDIAN: sub-daily / hourly water level and discharge for 210 CWC stations from 2020, scraped from the
CWC flood forecasting portal. Data: Figshare DOI 10.6084/m9.figshare.27004282.

Steps: list the Figshare files -> download -> unzip -> look for Baitarani station names in file names and
inside tables -> summarise each matching series (period, time step, number of records per year) and save
the Baitarani series as small CSVs in the results folder.
"""
import json
import os
import re
import sys
import urllib.request
import zipfile

import pandas as pd

ARTICLE = 27004282
API = f"https://api.figshare.com/v2/articles/{ARTICLE}"
BAITARANI = ["anandpur", "akhuapada", "champua", "swampatna", "keonjhar", "thakurmunda", "bhadrak",
             "jajpur", "baitarani", "jaraikela", "kesdih", "bhejdih"]


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())


def download(out_dir, max_mb=3000):
    os.makedirs(out_dir, exist_ok=True)
    meta = get_json(API)
    print("Title:", meta.get("title"))
    files = meta.get("files", [])
    for f in files:
        print(f"  {f['name']}  {f['size'] / 1e6:.1f} MB")
    for f in files:
        dst = os.path.join(out_dir, f["name"])
        if os.path.exists(dst) or f["size"] / 1e6 > max_mb:
            continue
        print("Downloading", f["name"], "...")
        req = urllib.request.Request(f["download_url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=600) as r, open(dst, "wb") as w:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                w.write(chunk)
    # unzip everything, including nested zips
    done = set()
    while True:
        zips = [os.path.join(r, n) for r, _, fs in os.walk(out_dir) for n in fs if n.lower().endswith(".zip")]
        todo = [z for z in zips if z not in done]
        if not todo:
            break
        for z in todo:
            try:
                with zipfile.ZipFile(z) as zf:
                    zf.extractall(os.path.splitext(z)[0])
            except zipfile.BadZipFile:
                print("  not a zip:", z)
            done.add(z)


def read_any(path, nrows=None):
    low = path.lower()
    if low.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, nrows=nrows)
    for sep in [",", ";", "\t", r"\s+"]:
        try:
            df = pd.read_csv(path, sep=sep, nrows=nrows, low_memory=False)
            if df.shape[1] > 1:
                return df
        except Exception:
            pass
    return None


def find(out_dir):
    tables = [os.path.join(r, n) for r, _, fs in os.walk(out_dir) for n in fs
              if n.lower().endswith((".csv", ".txt", ".xlsx", ".xls"))]
    print(f"\n{len(tables)} table files found")
    by_name = [p for p in tables if any(k in os.path.basename(p).lower() for k in BAITARANI)]
    print("Files whose name mentions a Baitarani station:", len(by_name))
    for p in by_name[:50]:
        print("  ", os.path.relpath(p, out_dir))

    # station lists / metadata: small tables that mention the names inside
    hits_meta = []
    for p in tables:
        if os.path.getsize(p) > 20e6:
            continue
        df = read_any(p)
        if df is None:
            continue
        txt = df.astype(str).apply(lambda c: c.str.lower())
        mask = txt.apply(lambda c: c.str.contains("|".join(BAITARANI), regex=True)).any(axis=1)
        if mask.any():
            hits_meta.append((p, df[mask]))
    print("\nTables that list Baitarani stations inside:", len(hits_meta))
    for p, rows in hits_meta[:10]:
        print("\n---", os.path.relpath(p, out_dir))
        print(rows.head(20).to_string()[:3000])
    return by_name, hits_meta


def summarise(paths, out_dir, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    rows = []
    for p in paths:
        df = read_any(p)
        if df is None or df.empty:
            continue
        tcol = next((c for c in df.columns if re.search(r"date|time", str(c), re.I)), df.columns[0])
        t = pd.to_datetime(df[tcol], errors="coerce", dayfirst=True)
        if t.notna().mean() < 0.8:
            continue
        df = df.assign(_t=t).dropna(subset=["_t"]).sort_values("_t")
        step = df["_t"].diff().median()
        per_year = df.groupby(df["_t"].dt.year).size().to_dict()
        num = [c for c in df.select_dtypes("number").columns]
        rows.append({"file": os.path.relpath(p, out_dir), "start": df["_t"].min(), "end": df["_t"].max(),
                     "median step": str(step), "records": len(df), "per year": per_year, "numeric columns": num[:6]})
        df.drop(columns="_t").to_csv(os.path.join(save_dir, os.path.basename(p).rsplit(".", 1)[0] + ".csv"), index=False)
    s = pd.DataFrame(rows)
    if len(s):
        print("\nSummary of Baitarani series:")
        print(s.to_string())
        s.to_csv(os.path.join(save_dir, "baitarani_series_summary.csv"), index=False)
    else:
        print("\nNo Baitarani time series could be read.")
    return s


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/guardian"
    save = sys.argv[2] if len(sys.argv) > 2 else "/kaggle/working/results/guardian_baitarani"
    download(out)
    by_name, meta = find(out)
    summarise(by_name, out, save)
