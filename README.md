# AI-Based Flood Forecasting (BTP)

Physics-guided Graph Temporal Fusion Transformer (PG-GraphTFT) for flood forecasting on Indian rivers, with the Baitarani basin as the case study.

Everything runs on Google Colab. The code lives in this repository and the data is downloaded into the Colab session, so nothing needs to be stored on a laptop.

## Project steps

| Step | What | Status |
|---|---|---|
| 1 | Multi-basin LSTM and TFT on CAMELS-IND daily data, compared on 2016–2020 | In progress |
| 2 | Request hourly CWC water levels for Baitarani; download DEM, river network, land cover, soil | Planned |
| 3 | Curve Number runoff module and graph routing module | Planned |
| 4 | Alert layer, dashboard, flood extent | Planned |

## Run Step 1

1. Open `notebooks/step1_colab.ipynb` in Colab (File → Open notebook → GitHub → this repo).
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
src/train_lstm.py      LSTM baseline
src/train_tft.py       Temporal Fusion Transformer
src/evaluate.py        metrics and plots
src/metrics.py         NSE, KGE, RMSE, peak error
notebooks/step1_colab.ipynb   runs everything in order
```
