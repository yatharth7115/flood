"""Step 4: river network between CAMELS-IND gauges and flood-wave travel time.

1. Nesting: gauge A is upstream of gauge B when A's catchment lies inside B's catchment
   (catchment polygons from shapefiles_catchment/ in CAMELS-IND; >= 90 % of A's area inside B).
   Without geopandas or the shapefile, a fallback uses: same basin code, smaller area, and B's flow
   strongly correlated with A's.
2. Only direct links are kept (A -> B with no gauge C in between).
3. Travel time per link: the lag (0-5 days) that maximises the correlation between upstream and
   downstream monsoon flow (June-October, training years), and the median delay between matched flood peaks.
Output: <processed dir>/river_graph_edges.csv (+ a copy and a summary in results_dir).
"""
import glob
import math
import os
import sys

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from dataset import load_attributes, norm_id  # noqa: E402

MAX_LAG = 5


def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def pick(cols, *keys):
    for k in keys:
        for c in cols:
            if k in c.lower():
                return c
    return None


def gauge_table(data_dir):
    attrs, _ = load_attributes(data_dir, ["topo"])
    cols = list(attrs.columns)
    lat = pick(cols, "cwc_lat", "lat")
    lon = pick(cols, "cwc_lon", "lon")
    area = pick(cols, "cwc_area", "ghi_area", "area")
    t = pd.DataFrame({"lat": attrs[lat], "lon": attrs[lon], "area": attrs[area]}, index=attrs.index)
    print(f"Gauge table: {len(t)} gauges (lat={lat}, lon={lon}, area={area})")
    return t.dropna()


def nested_pairs_polygons(data_dir, gt):
    try:
        import geopandas as gpd
    except ImportError:
        print("geopandas not installed: using the fallback")
        return None
    shp = glob.glob(os.path.join(data_dir, "**", "*.shp"), recursive=True)
    shp = [s for s in shp if "catch" in os.path.basename(s).lower()] or shp
    if not shp:
        print("No catchment shapefile found: using the fallback")
        return None
    g = gpd.read_file(shp[0])
    ids = set(gt.index)
    idcol = max(g.columns.drop("geometry"), key=lambda c: g[c].map(norm_id).isin(ids).sum())
    g["gauge_id"] = g[idcol].map(norm_id)
    g = g[g.gauge_id.isin(ids)].dissolve(by="gauge_id")
    if g.crs is None or g.crs.is_geographic:
        g = g.set_crs(g.crs or "EPSG:4326").to_crs("EPSG:7755")  # India NSF LCC, metres
    g["a"] = g.geometry.area
    print(f"Catchment polygons: {len(g)} gauges from {os.path.basename(shp[0])} (id column '{idcol}')")
    pairs = []
    sidx = g.sindex
    for up, row in g.iterrows():
        for j in sidx.query(row.geometry, predicate="intersects"):
            down = g.index[j]
            if down == up or g.at[down, "a"] <= row["a"] * 1.02:
                continue
            inter = row.geometry.intersection(g.at[down, "geometry"]).area
            if inter / row["a"] >= 0.9:
                pairs.append((up, down))
    return pairs


def nested_pairs_fallback(gt, q):
    piv = q.pivot_table(index="date", columns="gauge_id", values="q")
    lq = np.log1p(piv)
    pairs = []
    for up in gt.index:
        for down in gt.index:
            if up == down or str(up)[:-3] != str(down)[:-3]:   # same basin code (id // 1000)
                continue
            if gt.at[down, "area"] <= gt.at[up, "area"] * 1.02:
                continue
            if up not in lq or down not in lq:
                continue
            if haversine(gt.at[up, "lat"], gt.at[up, "lon"], gt.at[down, "lat"], gt.at[down, "lon"]) > 2.5 * math.sqrt(gt.at[down, "area"]):
                continue
            c = max(lq[up].corr(lq[down].shift(-k)) for k in range(MAX_LAG + 1))
            if c > 0.75:
                pairs.append((up, down))
    return pairs


def direct_links(pairs, gt):
    s = set(pairs)
    direct = []
    for up, down in pairs:
        between = [c for (a, c) in s if a == up and c != down and (c, down) in s]
        if not between:
            direct.append((up, down))
    return direct


def travel_time(up, down, q, train_end):
    piv = q[q.gauge_id.isin([up, down])].pivot_table(index="date", columns="gauge_id", values="q")
    piv = piv[piv.index <= train_end]
    if up not in piv or down not in piv:
        return np.nan, np.nan, np.nan, 0
    mon = piv[piv.index.month.isin([6, 7, 8, 9, 10])]
    lu, ld = np.log1p(mon[up]), np.log1p(mon[down])
    cors = [ld.corr(lu.shift(k)) for k in range(MAX_LAG + 1)]
    best = int(np.nanargmax(cors)) if np.isfinite(cors).any() else np.nan
    # matched flood peaks: largest downstream peak per year, upstream peak within the 5 days before
    lags = []
    for _, yr in piv.groupby(piv.index.year):
        if yr[down].notna().sum() < 200 or yr[up].notna().sum() < 200:
            continue
        td = yr[down].idxmax()
        win = yr.loc[td - pd.Timedelta(days=MAX_LAG): td, up]
        if win.notna().any():
            lags.append((td - win.idxmax()).days)
    return best, float(np.nanmax(cors)) if np.isfinite(cors).any() else np.nan, float(np.median(lags)) if lags else np.nan, len(lags)


def run(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    d = cfg["data"]
    gt = gauge_table(d["data_dir"])
    q = pd.read_parquet(d["processed_file"].replace(".parquet", "_qall.parquet"))
    q["gauge_id"] = q["gauge_id"].astype(str)
    q["date"] = pd.to_datetime(q["date"])
    gt = gt[gt.index.isin(set(q.gauge_id))]

    pairs = nested_pairs_polygons(d["data_dir"], gt)
    method = "catchment polygons"
    if pairs is None:
        pairs = nested_pairs_fallback(gt, q)
        method = "fallback (basin code + area + flow correlation)"
    links = direct_links(pairs, gt)
    print(f"Nesting method: {method}; nested pairs {len(pairs)}, direct links {len(links)}")

    rows = []
    for up, down in links:
        lag, corr, peak_lag, n_peaks = travel_time(up, down, q, d["train"][1])
        dist = haversine(gt.at[up, "lat"], gt.at[up, "lon"], gt.at[down, "lat"], gt.at[down, "lon"])
        rows.append({"up": up, "down": down, "area_up": gt.at[up, "area"], "area_down": gt.at[down, "area"],
                     "distance_km": round(dist, 1), "lag_days_corr": lag, "corr": round(corr, 3) if corr == corr else np.nan,
                     "lag_days_peaks": peak_lag, "n_peaks": n_peaks})
    e = pd.DataFrame(rows)
    if len(e):
        # river length ~ 1.3 x straight-line distance; speed in km/day where a lag > 0 was found
        e["speed_km_per_day"] = np.where(e["lag_days_peaks"] > 0, 1.3 * e["distance_km"] / e["lag_days_peaks"], np.nan)
    base = os.path.dirname(d["processed_file"])
    e.to_csv(os.path.join(base, "river_graph_edges.csv"), index=False)
    os.makedirs(cfg["results_dir"], exist_ok=True)
    e.to_csv(os.path.join(cfg["results_dir"], "river_graph_edges.csv"), index=False)

    kept = set(pd.read_parquet(d["processed_file"], columns=["gauge_id"])["gauge_id"].astype(str))
    down_kept = sorted(set(e["down"]) & kept) if len(e) else []
    pd.Series(down_kept, name="gauge_id").to_csv(os.path.join(cfg["results_dir"], "gauges_with_upstream.csv"), index=False)

    lines = ["# River graph and travel time (CAMELS-IND)", "", f"Method: {method}", "",
             f"Direct upstream -> downstream links: {len(e)}; modelled gauges with an upstream gauge: {len(down_kept)}", ""]
    if len(e):
        lines += ["Lag (days) from flow correlation, monsoon:", "", e["lag_days_corr"].value_counts().sort_index().to_frame("links").to_markdown(), "",
                  "Lag (days) between matched annual flood peaks:", "", e["lag_days_peaks"].describe().round(2).to_frame().to_markdown(), "",
                  "All links:", "", e.sort_values(["down", "up"]).to_markdown(index=False), ""]
    open(os.path.join(cfg["results_dir"], "river_graph.md"), "w").write("\n".join(lines))
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
