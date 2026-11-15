"""Step 2 features: physics-based runoff (SCS Curve Number), antecedent rainfall, future rainfall,
and flood-day weights.

Feature groups (choose any with --extra):
  antecedent   prcp_3d, prcp_7d (rain totals), api (antecedent precipitation index, k = 0.9)
  cn           q_cn: SCS-CN direct runoff (mm/day) from today's rain, with the Curve Number set by
               land cover + soil group and adjusted for wetness (AMC from 5-day antecedent rain)
  upstream     up_q: log of the summed observed flow of the gauges directly upstream (from the river graph
               built by src/river_graph.py), has_up: 1 if the gauge has an upstream gauge, up_frac: share of
               the catchment area that drains through those upstream gauges
  future_rain  prcp_f1..prcp_f7: rainfall of the next 1..7 days. Here these are OBSERVED values
               (a "perfect forecast"), so results are an upper bound; in operation they would be
               replaced by IMD / NCMRWF forecast rainfall.
"""
import numpy as np
import pandas as pd

# SCS Curve Numbers (USDA TR-55) for hydrologic soil groups A, B, C, D
CN_TABLE = {
    "trees": (36, 60, 73, 79),
    "crops": (67, 78, 85, 89),
    "range": (49, 69, 79, 84),
    "built_area": (89, 92, 94, 95),
    "bare": (77, 86, 91, 94),
    "water": (98, 98, 98, 98),
    "flooded_veg": (98, 98, 98, 98),
}
GROUPS = ("antecedent", "cn", "future_rain", "upstream")
HORIZON = 7


def _frac(s):
    s = s.astype(float)
    return s / 100.0 if s.max() > 1.5 else s


def soil_group(static):
    """0..3 = A..D from topsoil sand and clay fractions."""
    clay = _frac(static["soil_clay_frac_top"]) if "soil_clay_frac_top" in static else pd.Series(0.25, static.index)
    sand = _frac(static["soil_sand_frac_top"]) if "soil_sand_frac_top" in static else pd.Series(0.40, static.index)
    g = np.where((sand > 0.7) & (clay < 0.1), 0, np.where(clay < 0.2, 1, np.where(clay < 0.4, 2, 3)))
    return pd.Series(g, index=static.index)


def curve_number(static):
    """Area-weighted Curve Number (normal wetness, AMC II) for each gauge."""
    hsg = soil_group(static)
    num = pd.Series(0.0, index=static.index)
    den = pd.Series(0.0, index=static.index)
    for cls, cns in CN_TABLE.items():
        col = f"land_{cls}_frac"
        if col not in static:
            continue
        f = _frac(static[col]).clip(lower=0).fillna(0)
        cn = hsg.map(lambda g: cns[g])
        num += f * cn
        den += f
    cn2 = (num / den.replace(0, np.nan)).fillna(75.0).clip(30, 98)
    return cn2


def scs_runoff(p, cn):
    s = 25400.0 / cn - 254.0
    ia = 0.2 * s
    return np.where(p > ia, (p - ia) ** 2 / (p - ia + s), 0.0)


def add_features(df, static, groups, peak_q=0.95, train_end=None, upstream=None):
    """Return df with the requested feature groups, a flood weight base column, and the new feature names."""
    groups = [g for g in groups if g in GROUPS]
    cn2 = curve_number(static)
    out, new = [], []
    for g, gd in df.groupby("gauge_id", sort=False):
        gd = gd.set_index("date").sort_index()
        full = gd.asfreq("D")
        p = full["prcp"].fillna(0.0)
        if "antecedent" in groups:
            full["prcp_3d"] = p.rolling(3, min_periods=1).sum()
            full["prcp_7d"] = p.rolling(7, min_periods=1).sum()
            api = np.zeros(len(p))
            pv = p.values
            for t in range(len(pv)):
                api[t] = (0.9 * api[t - 1] if t else 0.0) + pv[t]
            full["api"] = api
        if "cn" in groups:
            cn = float(cn2.get(g, 75.0))
            p5 = p.shift(1).rolling(5, min_periods=1).sum().fillna(0.0)
            cn_dry = 4.2 * cn / (10 - 0.058 * cn)
            cn_wet = 23 * cn / (10 + 0.13 * cn)
            cn_t = np.where(p5 < 35.6, cn_dry, np.where(p5 > 53.3, cn_wet, cn))
            full["q_cn"] = scs_runoff(p.values, cn_t)
        if "future_rain" in groups:
            for h in range(1, HORIZON + 1):
                full[f"prcp_f{h}"] = p.shift(-h)
        if "upstream" in groups:
            edges, qall = upstream
            ups = edges[edges["down"].astype(str) == str(g)]
            if len(ups):
                qs = qall[qall["gauge_id"].isin(ups["up"].astype(str))].pivot_table(index="date", columns="gauge_id", values="q")
                qs = qs.reindex(full.index).interpolate(limit=3, limit_direction="both")
                full["up_q"] = np.log1p(qs.sum(axis=1, min_count=1)).values
                full["has_up"] = 1.0
                full["up_frac"] = float(min(1.0, ups["area_up"].sum() / max(ups["area_down"].iloc[0], 1e-6)))
            else:
                full["up_q"], full["has_up"], full["up_frac"] = 0.0, 0.0, 0.0
        # flood threshold per gauge, from the training period only
        tr = full["q"] if train_end is None else full.loc[:train_end, "q"]
        full["q_thr"] = np.nanquantile(tr.values, peak_q) if tr.notna().any() else np.nan
        full = full.loc[gd.index]  # back to the original rows
        full["gauge_id"] = g
        out.append(full.reset_index())
    res = pd.concat(out, ignore_index=True)
    if "antecedent" in groups:
        new += ["prcp_3d", "prcp_7d", "api"]
    if "cn" in groups:
        new += ["q_cn"]
    if "future_rain" in groups:
        new += [f"prcp_f{h}" for h in range(1, HORIZON + 1)]
    if "upstream" in groups:
        new += ["up_q", "has_up", "up_frac"]
    for c in new:
        res[c] = res[c].fillna(0.0).astype("float32")
    return res, new, cn2
