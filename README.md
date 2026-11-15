# AI-Based Flood Forecasting (BTP)

Physics-guided Graph Temporal Fusion Transformer (PG-GraphTFT) for flood forecasting on Indian rivers, with the Baitarani basin as the case study.

Everything runs on Google Colab. The code lives in this repository and the data is downloaded into the Colab session, so nothing needs to be stored on a laptop.

## Project steps

| Step | What | Status |
|---|---|---|
| 1 | Multi-basin LSTM and TFT on CAMELS-IND daily data, compared on 2016–2020 | Done ([results](results/step1/summary.md)) |
| 2 | Curve Number runoff and antecedent-rain features, flood-day weighting, future rainfall; LSTM ablation + TFT | Done ([results](results/step2/summary.md)) |
| 3 | Fair comparison: 3 seeds, 365-day look-back, longer TFT training, CAMELS-IND benchmark | Done ([results](results/step3/summary.md), [analysis](results/step3/analysis.md)) |
| 4 | River graph between gauges, flood travel time, upstream flow as input | Done: [results/step4](results/step4/analysis.md) (188 links, median flood speed ~100 km/day; upstream input gives no real gain at daily scale) |
| 2 | Request hourly CWC water levels for Baitarani; download DEM, river network, land cover, soil | Planned |
| 3 | Curve Number runoff module and graph routing module | Planned |
| 4 | Alert layer, dashboard, flood extent | Planned |

## Run Step 4 on Kaggle

Open [notebooks/step4_kaggle.ipynb on Kaggle](https://www.kaggle.com/kernels/welcome?src=https://github.com/yatharth7115/flood/blob/main/notebooks/step4_kaggle.ipynb), set GPU and Internet On, then Save Version → Save & Run All (Commit). About 30–40 minutes.

## Run Step 3 on Kaggle

Open [notebooks/step3_kaggle.ipynb on Kaggle](https://www.kaggle.com/kernels/welcome?src=https://github.com/yatharth7115/flood/blob/main/notebooks/step3_kaggle.ipynb), set GPU and Internet On, then Save Version → Save & Run All (Commit). About 5 hours.

## Run Step 2 on Kaggle

Open [notebooks/step2_kaggle.ipynb on Kaggle](https://www.kaggle.com/kernels/welcome?src=https://github.com/yatharth7115/flood/blob/main/notebooks/step2_kaggle.ipynb), set GPU and Internet On, then Save Version → Save & Run All (Commit). About 3–3.5 hours.

## Run Step 1 on Kaggle (recommended: keeps running after you close the browser)

1. Open: [notebooks/step1_kaggle.ipynb on Kaggle](https://www.kaggle.com/kernels/welcome?src=https://github.com/yatharth7115/flood/blob/main/notebooks/step1_kaggle.ipynb)
2. Right panel → Session options: Accelerator **GPU T4 x2**, Internet **On** (needs a phone-verified Kaggle account).
3. Click **Save Version → Save & Run All (Commit) → Save**. You can close the browser.
4. Later: open the notebook → **Output** tab for `summary.md`, the plots and `run_log.txt`.

## Run Step 1 on Colab

1. Open the notebook in Colab: [notebooks/step1_colab.ipynb](https://colab.research.google.com/github/yatharth7115/flood/blob/main/notebooks/step1_colab.ipynb)
2. Runtime → Change runtime type → T4 GPU.
3. Run the cells from top to bottom. Start with `QUICK_RUN = True` (40 gauges), then run all gauges.

Results (metrics tables and plots) are saved to Google Drive under `flood_btp/results_step1`.

## Step 1 setup

- **Data:** CAMELS-IND v2.2, streamflow-sufficient catchments ([Zenodo 14999580](https://zenodo.org/records/14999580)), daily 1981–2020.
- **Inputs:** rainfall, temperature, radiation, humidity, GLEAM PET and AET, soil moisture at four depths, past discharge; static topography, land cover, soil, geology and human-influence attributes. The hydrological-signature table is not used, because it is computed over all years, including the test years.
- **Split:** train 1981–2010, validation 2011–2015, test 2016–2020.
- **Models:** one LSTM and one TFT, each trained on all gauges together; 90-day look-back, 1–7 day forecast. The TFT gives P10, P50 and P90.
- **Metrics:** NSE, KGE, RMSE, peak-flow error, P10–P90 coverage; reported as the median over gauges and separately for Anandpur (Baitarani).

## Code

```
configs/step1.yaml     all settings
src/download.py        download and unzip CAMELS-IND into Colab
src/explore.py         print the data folder layout
src/dataset.py         build one clean table (gauge, date, inputs, discharge)
src/features.py        Step 2 features: Curve Number runoff, antecedent rain, future rain, flood weights
src/train_lstm.py      LSTM (options: --name, --extra, --peak-weight)
src/train_tft.py       Temporal Fusion Transformer (same options)
src/river_graph.py     Step 4: upstream/downstream links between gauges and flood travel time
src/benchmark_camels.py  CAMELS-IND's published LSTM predictions as a benchmark
src/evaluate.py        metrics, seed ensembles and plots
src/metrics.py         NSE, KGE, RMSE, peak error
notebooks/step1_colab.ipynb   runs everything in order
```
