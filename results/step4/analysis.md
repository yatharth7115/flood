# Step 4 analysis: river graph, travel time, upstream flow as input

## 1. River graph (works well)

- Method: catchment polygons (CAMELS-IND shapefile). 675 nested pairs reduced to **188 direct upstream → downstream links**; 79 of the 194 modelled gauges have at least one upstream gauge.
- 124 links have a strong flow correlation (r ≥ 0.7). These are the reliable ones. The 64 weaker links are mostly small side tributaries joining a much bigger river (e.g. 5023 → 5029, 5025 → 5029 with r < 0.2); their lags and speeds should not be used.
- One link has the upstream area slightly larger than the downstream area (8035 → 8011, 30,761 vs 29,645 km²). This is a small mismatch in the CWC areas; the polygons still nest.

## 2. Travel time

| Reliable links (r ≥ 0.7) | count |
|---|---|
| flood arrives the same day (lag 0) | 66 |
| next day (lag 1) | 54 |
| 2+ days | 4 |

- Median flood-wave speed on links with lag ≥ 1 day: **~100 km/day (~4 km/h)**, middle half 68–156 km/day. This is a physically sensible range for Indian monsoon rivers.
- Lag from flow correlation and lag between matched annual peaks agree well (median 1 day for both).
- **Limit:** with daily data, more than half the reliable links show "0 days", meaning less than a day. Hour-level travel times need hourly water-level data (the Baitarani data check).
- **Anandpur (7002):** one upstream gauge in CAMELS, 7005 (1,710 km², 106 km upstream, r = 0.88, lag 0 days). The flood reaches Anandpur within the same day.

## 3. Upstream flow as a model input

**Correction to the Kaggle summary.** In `summary_kaggle.md`, the Step 3 models came from the reference CSV and were scored on slightly different rows (the rows the TFT also had) than the new LSTM_ALL_UP models. That made LSTM_ALL_UP look worse (1-day NSE 0.599 vs 0.628). Re-scored on exactly the same rows (`same_rows_metrics_per_gauge.csv`), median over gauges:

| lead | LSTM_ALL_ENS (Step 3) NSE / KGE | LSTM_ALL_UP_ENS NSE / KGE | paired test, NSE |
|---|---|---|---|
| 1 day | 0.628 / 0.650 | 0.633 / 0.693 | no difference (p = 0.78) |
| 3 days | 0.509 / 0.587 | 0.519 / 0.618 | no difference (p = 0.30) |
| 7 days | 0.472 / 0.502 | 0.490 / 0.541 | small gain on gauges with upstream (0.498 vs 0.464, wins at 58%, p = 0.04) |

- **NSE:** no real change at 1–5 days, and a small gain at 7 days only on gauges that have an upstream gauge. This is the one place we would expect upstream flow to help.
- **KGE:** higher at all leads (p < 0.01 at 1, 2 and 7 days). But it also rises on gauges *without* an upstream gauge, so this is mostly a training effect, not upstream information.
- **Why so little gain:** most links have lag 0–1 day. With daily steps, the downstream gauge's own flow yesterday plus the (perfect) rainfall forecast already carry almost the same information. Upstream flow should matter much more at hourly time steps.

### Blends (same rows)

| lead | LSTM + TFT | LSTM + UP + TFT |
|---|---|---|
| 1 | 0.645 | 0.646 |
| 3 | 0.541 | 0.554 |
| 7 | 0.520 | 0.506 |

Adding the upstream model to the blend changes nothing in a meaningful way (median per-gauge difference 0.000). Anandpur: LSTM+TFT 0.741 / 0.730 / 0.752; 3-way 0.736 / 0.729 / 0.750.

## Verdict

- The river graph and travel-time table are a valid result and go to the dashboard ("flood reaches the next station in about X days").
- Upstream flow as an input is **not worth it at daily resolution**. Keep **LSTM + TFT** as the final daily forecaster.
- Revisit upstream inputs only with hourly data.
- Evaluation fix: `evaluate.py` now saves `eval_keys.parquet` and, when that file sits next to a reference CSV, scores new models on the same rows.
