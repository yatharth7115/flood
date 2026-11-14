# Note on the evaluation fix (14 Nov 2026)

The first versions of `summary.md` for Step 1 and Step 2 were computed with a bug in `src/evaluate.py`.
The TFT prediction files contain about 10% duplicate rows (two windows predicting the same date at the same
lead around filled data gaps). When the models were joined on (gauge, date, lead), these duplicates multiplied
and over-weighted a few periods, which distorted the TFT scores (e.g. median RMSE 12 instead of ~95 m3/s).

Fix: predictions are now reduced to one row per (gauge, date, lead) before comparing (`dedupe` in
`src/evaluate.py`, and in `src/train_tft.py` before saving). The tables in `step1/` and `step2/` were recomputed
from the same prediction files with the fixed code. Sanity check: LSTM_BASE in Step 2 reproduces Step 1's LSTM
exactly (median 1-day NSE 0.567), as expected for the same model and seed.
