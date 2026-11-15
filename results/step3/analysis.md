# Step 3 analysis (194 CAMELS-IND gauges, test 2016–2020)

Paired comparison per gauge (Wilcoxon signed-rank test on gauge-wise NSE):

| Comparison | Lead | Median NSE difference | Better at % gauges | p |
|---|---|---|---|---|
| TFT_V2_LONG vs LSTM_ALL_ENS | 1 day | +0.005 | 54% | 0.91 |
| TFT_V2_LONG vs LSTM_ALL_ENS | 7 days | −0.012 | 44% | 0.002 |
| TFT_V2_LONG vs LSTM_ALL_ENS (KGE) | 1 day | +0.034 | 63% | 0.0001 |
| LSTM365_ALL_ENS vs LSTM_ALL_ENS | 1 day | +0.003 | 57% | 0.06 |
| LSTM365_ALL_ENS vs LSTM_ALL_ENS | 7 days | +0.004 | 56% | 0.01 |
| TFT_V2_LONG vs TFT_V2 (Step 2) | 1 day | +0.015 | 63% | 0.0003 |

Combined ensemble (mean of LSTM_ALL seed ensemble and TFT_V2_LONG), median over gauges:

| Lead | LSTM_ALL_ENS | TFT_V2_LONG | LSTM+TFT |
|---|---|---|---|
| 1 day NSE | 0.628 | 0.625 | **0.645** |
| 3 days NSE | 0.509 | 0.497 | **0.541** |
| 7 days NSE | 0.472 | 0.421 | **0.520** |
| 1 day KGE | 0.650 | 0.697 | **0.709** |
| 1 day peak error | −26% | −19% | −23% |

LSTM+TFT beats the LSTM ensemble at 66% of gauges (1 day). Anandpur 1/3/7-day NSE: 0.741 / 0.730 / 0.752.
