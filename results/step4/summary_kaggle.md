# Results on the test period (2016-01-01 to 2020-12-31)

Gauges compared: 194

Median across gauges (discharge, m3/s):

|                               |   NSE |   KGE |    RMSE |   PeakErr% |   P10-P90 coverage% |
|:------------------------------|------:|------:|--------:|-----------:|--------------------:|
| (1, 'CAMELS_LSTM_STEP3')      | 0.409 | 0.418 | 104.671 |    -27.036 |             nan     |
| (1, 'LSTM365_ALL_ENS_STEP3')  | 0.627 | 0.699 |  86.659 |    -21.927 |             nan     |
| (1, 'LSTM365_ALL_S0_STEP3')   | 0.615 | 0.691 |  86.936 |    -23.171 |             nan     |
| (1, 'LSTM365_ALL_S1_STEP3')   | 0.625 | 0.662 |  87.836 |    -27.859 |             nan     |
| (1, 'LSTM365_ALL_S2_STEP3')   | 0.591 | 0.668 |  89.384 |    -17.359 |             nan     |
| (1, 'LSTM_ALL_ENS_STEP3')     | 0.628 | 0.65  |  86.265 |    -26.482 |             nan     |
| (1, 'LSTM_ALL_S0_STEP3')      | 0.62  | 0.62  |  87.331 |    -31.015 |             nan     |
| (1, 'LSTM_ALL_S1_STEP3')      | 0.617 | 0.654 |  90.068 |    -26.665 |             nan     |
| (1, 'LSTM_ALL_S2_STEP3')      | 0.622 | 0.647 |  90.83  |    -23.172 |             nan     |
| (1, 'LSTM_ALL_STEP2_STEP3')   | 0.62  | 0.62  |  87.331 |    -31.015 |             nan     |
| (1, 'LSTM_ALL_UP_ENS')        | 0.599 | 0.654 |  92.411 |    -20.303 |             nan     |
| (1, 'LSTM_ALL_UP_S0')         | 0.585 | 0.663 |  95.016 |    -20.435 |             nan     |
| (1, 'LSTM_ALL_UP_S1')         | 0.566 | 0.643 |  94.014 |    -23.47  |             nan     |
| (1, 'LSTM_ALL_UP_S2')         | 0.576 | 0.626 |  94.531 |    -24.162 |             nan     |
| (1, 'LSTM_BASE_STEP2_STEP3')  | 0.567 | 0.546 |  98.582 |    -38.807 |             nan     |
| (1, 'LSTM_FRAIN_STEP2_STEP3') | 0.605 | 0.598 |  87.982 |    -33.119 |             nan     |
| (1, 'LSTM_PEAK_STEP2_STEP3')  | 0.562 | 0.654 |  95.886 |    -22.335 |             nan     |
| (1, 'LSTM_PHYS_STEP2_STEP3')  | 0.573 | 0.538 |  98.834 |    -38.802 |             nan     |
| (1, 'TFT_PHYS_STEP2_STEP3')   | 0.552 | 0.668 |  94.905 |    -19.769 |              64.412 |
| (1, 'TFT_V2_LONG_STEP3')      | 0.625 | 0.697 |  83.371 |    -18.557 |              62.457 |
| (1, 'TFT_V2_STEP2_STEP3')     | 0.587 | 0.682 |  84.98  |    -11.377 |              56.844 |
| (3, 'CAMELS_LSTM_STEP3')      | 0.384 | 0.412 | 101.833 |    -26.985 |             nan     |
| (3, 'LSTM365_ALL_ENS_STEP3')  | 0.509 | 0.62  |  90.695 |    -28.269 |             nan     |
| (3, 'LSTM365_ALL_S0_STEP3')   | 0.499 | 0.594 |  92.298 |    -31.42  |             nan     |
| (3, 'LSTM365_ALL_S1_STEP3')   | 0.492 | 0.607 |  89.226 |    -28.635 |             nan     |
| (3, 'LSTM365_ALL_S2_STEP3')   | 0.48  | 0.568 |  95.983 |    -25.783 |             nan     |
| (3, 'LSTM_ALL_ENS_STEP3')     | 0.509 | 0.587 |  92.308 |    -28.546 |             nan     |
| (3, 'LSTM_ALL_S0_STEP3')      | 0.513 | 0.576 |  96.642 |    -30.689 |             nan     |
| (3, 'LSTM_ALL_S1_STEP3')      | 0.486 | 0.584 | 101.709 |    -27.191 |             nan     |
| (3, 'LSTM_ALL_S2_STEP3')      | 0.503 | 0.567 |  92.386 |    -29.586 |             nan     |
| (3, 'LSTM_ALL_STEP2_STEP3')   | 0.513 | 0.576 |  96.642 |    -30.689 |             nan     |
| (3, 'LSTM_ALL_UP_ENS')        | 0.521 | 0.586 | 102.296 |    -32.034 |             nan     |
| (3, 'LSTM_ALL_UP_S0')         | 0.505 | 0.582 | 109.022 |    -28.954 |             nan     |
| (3, 'LSTM_ALL_UP_S1')         | 0.48  | 0.571 | 104.851 |    -34.679 |             nan     |
| (3, 'LSTM_ALL_UP_S2')         | 0.51  | 0.567 | 101.114 |    -33.269 |             nan     |
| (3, 'LSTM_BASE_STEP2_STEP3')  | 0.312 | 0.316 | 117.466 |    -59.783 |             nan     |
| (3, 'LSTM_FRAIN_STEP2_STEP3') | 0.521 | 0.506 |  95.738 |    -42.495 |             nan     |
| (3, 'LSTM_PEAK_STEP2_STEP3')  | 0.281 | 0.447 | 118.527 |    -44.473 |             nan     |
| (3, 'LSTM_PHYS_STEP2_STEP3')  | 0.316 | 0.29  | 119.486 |    -63.501 |             nan     |
| (3, 'TFT_PHYS_STEP2_STEP3')   | 0.28  | 0.436 | 116.8   |    -46.041 |              62.603 |
| (3, 'TFT_V2_LONG_STEP3')      | 0.497 | 0.632 |  88.968 |    -20.003 |              60.963 |
| (3, 'TFT_V2_STEP2_STEP3')     | 0.502 | 0.617 |  92.867 |    -22.93  |              56.926 |
| (7, 'CAMELS_LSTM_STEP3')      | 0.41  | 0.415 | 102.481 |    -28.028 |             nan     |
| (7, 'LSTM365_ALL_ENS_STEP3')  | 0.479 | 0.538 | 103.09  |    -32.142 |             nan     |
| (7, 'LSTM365_ALL_S0_STEP3')   | 0.461 | 0.555 | 103.238 |    -31.573 |             nan     |
| (7, 'LSTM365_ALL_S1_STEP3')   | 0.458 | 0.549 | 101.787 |    -31.302 |             nan     |
| (7, 'LSTM365_ALL_S2_STEP3')   | 0.468 | 0.513 | 104.746 |    -29.953 |             nan     |
| (7, 'LSTM_ALL_ENS_STEP3')     | 0.472 | 0.502 | 104.096 |    -31.129 |             nan     |
| (7, 'LSTM_ALL_S0_STEP3')      | 0.442 | 0.486 | 105.817 |    -31.998 |             nan     |
| (7, 'LSTM_ALL_S1_STEP3')      | 0.469 | 0.491 | 103.155 |    -34.71  |             nan     |
| (7, 'LSTM_ALL_S2_STEP3')      | 0.468 | 0.526 | 106.362 |    -30.657 |             nan     |
| (7, 'LSTM_ALL_STEP2_STEP3')   | 0.442 | 0.486 | 105.817 |    -31.998 |             nan     |
| (7, 'LSTM_ALL_UP_ENS')        | 0.495 | 0.54  | 109.865 |    -30.53  |             nan     |
| (7, 'LSTM_ALL_UP_S0')         | 0.486 | 0.518 | 111.421 |    -35.213 |             nan     |
| (7, 'LSTM_ALL_UP_S1')         | 0.468 | 0.523 | 108.237 |    -30.714 |             nan     |
| (7, 'LSTM_ALL_UP_S2')         | 0.456 | 0.532 | 109.586 |    -30.88  |             nan     |
| (7, 'LSTM_BASE_STEP2_STEP3')  | 0.182 | 0.059 | 139.844 |    -79.749 |             nan     |
| (7, 'LSTM_FRAIN_STEP2_STEP3') | 0.46  | 0.431 | 106.188 |    -47.787 |             nan     |
| (7, 'LSTM_PEAK_STEP2_STEP3')  | 0.168 | 0.28  | 139.658 |    -65.18  |             nan     |
| (7, 'LSTM_PHYS_STEP2_STEP3')  | 0.169 | 0.069 | 137.266 |    -79.528 |             nan     |
| (7, 'TFT_PHYS_STEP2_STEP3')   | 0.103 | 0.29  | 138.419 |    -60.928 |              62.765 |
| (7, 'TFT_V2_LONG_STEP3')      | 0.421 | 0.583 |  98.711 |    -22.381 |              60.71  |
| (7, 'TFT_V2_STEP2_STEP3')     | 0.43  | 0.532 | 101.697 |    -30.589 |              54.366 |

Share of gauges with higher 1-day NSE than LSTM_ALL_ENS_STEP3 (%):

| model                  |   % gauges |
|:-----------------------|-----------:|
| CAMELS_LSTM_STEP3      |         17 |
| LSTM365_ALL_ENS_STEP3  |         57 |
| LSTM365_ALL_S0_STEP3   |         47 |
| LSTM365_ALL_S1_STEP3   |         48 |
| LSTM365_ALL_S2_STEP3   |         36 |
| LSTM_ALL_S0_STEP3      |         40 |
| LSTM_ALL_S1_STEP3      |         41 |
| LSTM_ALL_S2_STEP3      |         31 |
| LSTM_ALL_STEP2_STEP3   |         40 |
| LSTM_ALL_UP_ENS        |         37 |
| LSTM_ALL_UP_S0         |         36 |
| LSTM_ALL_UP_S1         |         34 |
| LSTM_ALL_UP_S2         |         34 |
| LSTM_BASE_STEP2_STEP3  |         28 |
| LSTM_FRAIN_STEP2_STEP3 |         42 |
| LSTM_PEAK_STEP2_STEP3  |         28 |
| LSTM_PHYS_STEP2_STEP3  |         26 |
| TFT_PHYS_STEP2_STEP3   |         34 |
| TFT_V2_LONG_STEP3      |         54 |
| TFT_V2_STEP2_STEP3     |         42 |

Variation across random seeds (median NSE over gauges):

| model       |   lead |   seeds |   median NSE mean |   std across seeds |
|:------------|-------:|--------:|------------------:|-------------------:|
| LSTM_ALL_UP |      1 |       3 |             0.576 |              0.009 |
| LSTM_ALL_UP |      3 |       3 |             0.498 |              0.016 |
| LSTM_ALL_UP |      7 |       3 |             0.47  |              0.015 |

Only with_upstream gauges (79): median across gauges

|                               |   NSE |   KGE |    RMSE |   PeakErr% |   P10-P90 coverage% |
|:------------------------------|------:|------:|--------:|-----------:|--------------------:|
| (1, 'CAMELS_LSTM_STEP3')      | 0.438 | 0.46  | 279.221 |    -18.089 |             nan     |
| (1, 'LSTM365_ALL_ENS_STEP3')  | 0.656 | 0.719 | 212.069 |    -22.491 |             nan     |
| (1, 'LSTM365_ALL_S0_STEP3')   | 0.649 | 0.711 | 217.788 |    -23.485 |             nan     |
| (1, 'LSTM365_ALL_S1_STEP3')   | 0.667 | 0.701 | 215.998 |    -28.397 |             nan     |
| (1, 'LSTM365_ALL_S2_STEP3')   | 0.617 | 0.701 | 208.264 |    -18.974 |             nan     |
| (1, 'LSTM_ALL_ENS_STEP3')     | 0.669 | 0.651 | 228.05  |    -28.483 |             nan     |
| (1, 'LSTM_ALL_S0_STEP3')      | 0.668 | 0.656 | 223.047 |    -30.418 |             nan     |
| (1, 'LSTM_ALL_S1_STEP3')      | 0.644 | 0.655 | 213.6   |    -27.61  |             nan     |
| (1, 'LSTM_ALL_S2_STEP3')      | 0.65  | 0.659 | 239.255 |    -26.029 |             nan     |
| (1, 'LSTM_ALL_STEP2_STEP3')   | 0.668 | 0.656 | 223.047 |    -30.418 |             nan     |
| (1, 'LSTM_ALL_UP_ENS')        | 0.63  | 0.663 | 226.654 |    -19.648 |             nan     |
| (1, 'LSTM_ALL_UP_S0')         | 0.605 | 0.668 | 230.262 |    -18.663 |             nan     |
| (1, 'LSTM_ALL_UP_S1')         | 0.598 | 0.646 | 230.12  |    -21.396 |             nan     |
| (1, 'LSTM_ALL_UP_S2')         | 0.608 | 0.658 | 239.483 |    -22.912 |             nan     |
| (1, 'LSTM_BASE_STEP2_STEP3')  | 0.609 | 0.591 | 241.117 |    -34.577 |             nan     |
| (1, 'LSTM_FRAIN_STEP2_STEP3') | 0.645 | 0.639 | 229.223 |    -31.847 |             nan     |
| (1, 'LSTM_PEAK_STEP2_STEP3')  | 0.623 | 0.707 | 234.581 |    -21.056 |             nan     |
| (1, 'LSTM_PHYS_STEP2_STEP3')  | 0.621 | 0.577 | 249.912 |    -36.733 |             nan     |
| (1, 'TFT_PHYS_STEP2_STEP3')   | 0.64  | 0.737 | 204.873 |    -17.785 |              75.915 |
| (1, 'TFT_V2_LONG_STEP3')      | 0.65  | 0.758 | 201.025 |    -16.082 |              72.618 |
| (1, 'TFT_V2_STEP2_STEP3')     | 0.653 | 0.722 | 209.005 |     -9.013 |              58.966 |
| (3, 'CAMELS_LSTM_STEP3')      | 0.418 | 0.426 | 273.952 |    -17.263 |             nan     |
| (3, 'LSTM365_ALL_ENS_STEP3')  | 0.532 | 0.634 | 224.613 |    -28.805 |             nan     |
| (3, 'LSTM365_ALL_S0_STEP3')   | 0.552 | 0.615 | 224.4   |    -32.972 |             nan     |
| (3, 'LSTM365_ALL_S1_STEP3')   | 0.528 | 0.638 | 229.314 |    -31.291 |             nan     |
| (3, 'LSTM365_ALL_S2_STEP3')   | 0.512 | 0.602 | 236.06  |    -23.135 |             nan     |
| (3, 'LSTM_ALL_ENS_STEP3')     | 0.515 | 0.603 | 242.687 |    -30.327 |             nan     |
| (3, 'LSTM_ALL_S0_STEP3')      | 0.524 | 0.595 | 246.06  |    -31.01  |             nan     |
| (3, 'LSTM_ALL_S1_STEP3')      | 0.485 | 0.575 | 238.211 |    -27.424 |             nan     |
| (3, 'LSTM_ALL_S2_STEP3')      | 0.525 | 0.602 | 240.337 |    -32.179 |             nan     |
| (3, 'LSTM_ALL_STEP2_STEP3')   | 0.524 | 0.595 | 246.06  |    -31.01  |             nan     |
| (3, 'LSTM_ALL_UP_ENS')        | 0.52  | 0.631 | 257.106 |    -31.937 |             nan     |
| (3, 'LSTM_ALL_UP_S0')         | 0.512 | 0.614 | 254.205 |    -28.651 |             nan     |
| (3, 'LSTM_ALL_UP_S1')         | 0.502 | 0.599 | 265.975 |    -33.37  |             nan     |
| (3, 'LSTM_ALL_UP_S2')         | 0.529 | 0.601 | 260.512 |    -32.582 |             nan     |
| (3, 'LSTM_BASE_STEP2_STEP3')  | 0.397 | 0.353 | 254.166 |    -56.666 |             nan     |
| (3, 'LSTM_FRAIN_STEP2_STEP3') | 0.536 | 0.536 | 232.967 |    -39.502 |             nan     |
| (3, 'LSTM_PEAK_STEP2_STEP3')  | 0.362 | 0.51  | 261.553 |    -39.862 |             nan     |
| (3, 'LSTM_PHYS_STEP2_STEP3')  | 0.378 | 0.34  | 253.269 |    -58.904 |             nan     |
| (3, 'TFT_PHYS_STEP2_STEP3')   | 0.416 | 0.556 | 275.237 |    -40.173 |              71.57  |
| (3, 'TFT_V2_LONG_STEP3')      | 0.53  | 0.661 | 221.127 |    -16.987 |              72.333 |
| (3, 'TFT_V2_STEP2_STEP3')     | 0.517 | 0.624 | 240.176 |    -20.5   |              63.094 |
| (7, 'CAMELS_LSTM_STEP3')      | 0.446 | 0.437 | 279.692 |    -17.499 |             nan     |
| (7, 'LSTM365_ALL_ENS_STEP3')  | 0.459 | 0.541 | 269.427 |    -32.739 |             nan     |
| (7, 'LSTM365_ALL_S0_STEP3')   | 0.428 | 0.577 | 278.745 |    -35.178 |             nan     |
| (7, 'LSTM365_ALL_S1_STEP3')   | 0.458 | 0.558 | 281.552 |    -35.515 |             nan     |
| (7, 'LSTM365_ALL_S2_STEP3')   | 0.442 | 0.493 | 291.902 |    -29.849 |             nan     |
| (7, 'LSTM_ALL_ENS_STEP3')     | 0.464 | 0.509 | 272.689 |    -32.775 |             nan     |
| (7, 'LSTM_ALL_S0_STEP3')      | 0.437 | 0.49  | 287.165 |    -30.02  |             nan     |
| (7, 'LSTM_ALL_S1_STEP3')      | 0.47  | 0.546 | 270.743 |    -33.484 |             nan     |
| (7, 'LSTM_ALL_S2_STEP3')      | 0.469 | 0.543 | 267.403 |    -35.098 |             nan     |
| (7, 'LSTM_ALL_STEP2_STEP3')   | 0.437 | 0.49  | 287.165 |    -30.02  |             nan     |
| (7, 'LSTM_ALL_UP_ENS')        | 0.498 | 0.583 | 264.554 |    -30.256 |             nan     |
| (7, 'LSTM_ALL_UP_S0')         | 0.49  | 0.596 | 268.239 |    -33.31  |             nan     |
| (7, 'LSTM_ALL_UP_S1')         | 0.471 | 0.557 | 282.929 |    -29.598 |             nan     |
| (7, 'LSTM_ALL_UP_S2')         | 0.457 | 0.533 | 263.137 |    -30.204 |             nan     |
| (7, 'LSTM_BASE_STEP2_STEP3')  | 0.182 | 0.047 | 339.085 |    -79.692 |             nan     |
| (7, 'LSTM_FRAIN_STEP2_STEP3') | 0.487 | 0.506 | 279.394 |    -47.965 |             nan     |
| (7, 'LSTM_PEAK_STEP2_STEP3')  | 0.18  | 0.318 | 338.57  |    -65.251 |             nan     |
| (7, 'LSTM_PHYS_STEP2_STEP3')  | 0.19  | 0.097 | 335.91  |    -78.628 |             nan     |
| (7, 'TFT_PHYS_STEP2_STEP3')   | 0.128 | 0.339 | 340.151 |    -59.141 |              69.697 |
| (7, 'TFT_V2_LONG_STEP3')      | 0.423 | 0.61  | 266.229 |    -22.383 |              71.539 |
| (7, 'TFT_V2_STEP2_STEP3')     | 0.421 | 0.56  | 275.187 |    -26.397 |              63.115 |

Share of these gauges with higher 1-day NSE than LSTM_ALL_ENS_STEP3 (%):

| model                  |   % gauges |
|:-----------------------|-----------:|
| CAMELS_LSTM_STEP3      |         14 |
| LSTM365_ALL_ENS_STEP3  |         58 |
| LSTM365_ALL_S0_STEP3   |         43 |
| LSTM365_ALL_S1_STEP3   |         54 |
| LSTM365_ALL_S2_STEP3   |         39 |
| LSTM_ALL_S0_STEP3      |         43 |
| LSTM_ALL_S1_STEP3      |         42 |
| LSTM_ALL_S2_STEP3      |         32 |
| LSTM_ALL_STEP2_STEP3   |         43 |
| LSTM_ALL_UP_ENS        |         42 |
| LSTM_ALL_UP_S0         |         37 |
| LSTM_ALL_UP_S1         |         37 |
| LSTM_ALL_UP_S2         |         35 |
| LSTM_BASE_STEP2_STEP3  |         25 |
| LSTM_FRAIN_STEP2_STEP3 |         34 |
| LSTM_PEAK_STEP2_STEP3  |         29 |
| LSTM_PHYS_STEP2_STEP3  |         20 |
| TFT_PHYS_STEP2_STEP3   |         38 |
| TFT_V2_LONG_STEP3      |         62 |
| TFT_V2_STEP2_STEP3     |         44 |

Focus gauge (Anandpur, id 7002):

|                               |   NSE |   KGE |    RMSE |   PeakErr% |   P10-P90 coverage% |
|:------------------------------|------:|------:|--------:|-----------:|--------------------:|
| (1, 'CAMELS_LSTM_STEP3')      | 0.612 | 0.687 | 151.001 |     25.715 |             nan     |
| (1, 'LSTM365_ALL_ENS_STEP3')  | 0.724 | 0.856 | 127.529 |      0.991 |             nan     |
| (1, 'LSTM365_ALL_S0_STEP3')   | 0.726 | 0.854 | 127.016 |      0.859 |             nan     |
| (1, 'LSTM365_ALL_S1_STEP3')   | 0.739 | 0.818 | 124.014 |    -11.574 |             nan     |
| (1, 'LSTM365_ALL_S2_STEP3')   | 0.67  | 0.818 | 139.36  |     13.689 |             nan     |
| (1, 'LSTM_ALL_ENS_STEP3')     | 0.731 | 0.847 | 125.747 |     -4.455 |             nan     |
| (1, 'LSTM_ALL_S0_STEP3')      | 0.728 | 0.806 | 126.496 |    -11.45  |             nan     |
| (1, 'LSTM_ALL_S1_STEP3')      | 0.741 | 0.856 | 123.521 |     -3.322 |             nan     |
| (1, 'LSTM_ALL_S2_STEP3')      | 0.697 | 0.831 | 133.454 |      1.407 |             nan     |
| (1, 'LSTM_ALL_STEP2_STEP3')   | 0.728 | 0.806 | 126.496 |    -11.45  |             nan     |
| (1, 'LSTM_ALL_UP_ENS')        | 0.716 | 0.843 | 128.824 |     -0.538 |             nan     |
| (1, 'LSTM_ALL_UP_S0')         | 0.724 | 0.854 | 126.987 |     -1.867 |             nan     |
| (1, 'LSTM_ALL_UP_S1')         | 0.706 | 0.831 | 131.003 |     -4.736 |             nan     |
| (1, 'LSTM_ALL_UP_S2')         | 0.689 | 0.814 | 134.815 |      4.988 |             nan     |
| (1, 'LSTM_BASE_STEP2_STEP3')  | 0.705 | 0.695 | 131.787 |    -27.552 |             nan     |
| (1, 'LSTM_FRAIN_STEP2_STEP3') | 0.717 | 0.731 | 129.038 |    -19.28  |             nan     |
| (1, 'LSTM_PEAK_STEP2_STEP3')  | 0.708 | 0.808 | 131.172 |     -0.61  |             nan     |
| (1, 'LSTM_PHYS_STEP2_STEP3')  | 0.702 | 0.729 | 132.39  |    -23.13  |             nan     |
| (1, 'TFT_PHYS_STEP2_STEP3')   | 0.704 | 0.817 | 131.995 |    -14.256 |              94.532 |
| (1, 'TFT_V2_LONG_STEP3')      | 0.742 | 0.855 | 123.317 |     -4.766 |              94.995 |
| (1, 'TFT_V2_STEP2_STEP3')     | 0.676 | 0.78  | 137.999 |      5.049 |              87.952 |
| (3, 'CAMELS_LSTM_STEP3')      | 0.622 | 0.695 | 152.401 |     25.38  |             nan     |
| (3, 'LSTM365_ALL_ENS_STEP3')  | 0.737 | 0.853 | 127.019 |     -3.287 |             nan     |
| (3, 'LSTM365_ALL_S0_STEP3')   | 0.735 | 0.842 | 127.628 |     -6.267 |             nan     |
| (3, 'LSTM365_ALL_S1_STEP3')   | 0.725 | 0.842 | 129.809 |     -3.694 |             nan     |
| (3, 'LSTM365_ALL_S2_STEP3')   | 0.725 | 0.842 | 130.033 |      0.101 |             nan     |
| (3, 'LSTM_ALL_ENS_STEP3')     | 0.699 | 0.838 | 135.815 |     -1.234 |             nan     |
| (3, 'LSTM_ALL_S0_STEP3')      | 0.653 | 0.817 | 145.99  |      8.292 |             nan     |
| (3, 'LSTM_ALL_S1_STEP3')      | 0.737 | 0.849 | 127.063 |     -5.003 |             nan     |
| (3, 'LSTM_ALL_S2_STEP3')      | 0.673 | 0.81  | 141.626 |     -6.993 |             nan     |
| (3, 'LSTM_ALL_STEP2_STEP3')   | 0.653 | 0.817 | 145.99  |      8.292 |             nan     |
| (3, 'LSTM_ALL_UP_ENS')        | 0.713 | 0.813 | 130.943 |     -6.968 |             nan     |
| (3, 'LSTM_ALL_UP_S0')         | 0.715 | 0.82  | 130.494 |     -3.576 |             nan     |
| (3, 'LSTM_ALL_UP_S1')         | 0.679 | 0.817 | 138.472 |     -2.354 |             nan     |
| (3, 'LSTM_ALL_UP_S2')         | 0.718 | 0.786 | 129.611 |    -14.975 |             nan     |
| (3, 'LSTM_BASE_STEP2_STEP3')  | 0.433 | 0.468 | 186.476 |    -69.328 |             nan     |
| (3, 'LSTM_FRAIN_STEP2_STEP3') | 0.691 | 0.67  | 137.62  |    -25.084 |             nan     |
| (3, 'LSTM_PEAK_STEP2_STEP3')  | 0.398 | 0.609 | 192.189 |    -53.901 |             nan     |
| (3, 'LSTM_PHYS_STEP2_STEP3')  | 0.423 | 0.457 | 188.213 |    -70.198 |             nan     |
| (3, 'TFT_PHYS_STEP2_STEP3')   | 0.416 | 0.624 | 189.303 |    -57.473 |              93.314 |
| (3, 'TFT_V2_LONG_STEP3')      | 0.725 | 0.847 | 129.91  |     -2.218 |              95.415 |
| (3, 'TFT_V2_STEP2_STEP3')     | 0.678 | 0.821 | 140.64  |     -6.598 |              84.623 |
| (7, 'CAMELS_LSTM_STEP3')      | 0.62  | 0.688 | 151.205 |     27.935 |             nan     |
| (7, 'LSTM365_ALL_ENS_STEP3')  | 0.757 | 0.838 | 120.752 |    -11.403 |             nan     |
| (7, 'LSTM365_ALL_S0_STEP3')   | 0.731 | 0.849 | 127.158 |     -1.978 |             nan     |
| (7, 'LSTM365_ALL_S1_STEP3')   | 0.749 | 0.787 | 122.78  |    -18.463 |             nan     |
| (7, 'LSTM365_ALL_S2_STEP3')   | 0.755 | 0.849 | 121.329 |    -13.769 |             nan     |
| (7, 'LSTM_ALL_ENS_STEP3')     | 0.748 | 0.838 | 122.989 |    -10.818 |             nan     |
| (7, 'LSTM_ALL_S0_STEP3')      | 0.716 | 0.849 | 130.594 |      0.733 |             nan     |
| (7, 'LSTM_ALL_S1_STEP3')      | 0.753 | 0.781 | 121.773 |    -20.596 |             nan     |
| (7, 'LSTM_ALL_S2_STEP3')      | 0.717 | 0.821 | 130.384 |    -12.59  |             nan     |
| (7, 'LSTM_ALL_STEP2_STEP3')   | 0.716 | 0.849 | 130.594 |      0.733 |             nan     |
| (7, 'LSTM_ALL_UP_ENS')        | 0.728 | 0.836 | 127.928 |     -7.565 |             nan     |
| (7, 'LSTM_ALL_UP_S0')         | 0.727 | 0.697 | 128.05  |    -26.134 |             nan     |
| (7, 'LSTM_ALL_UP_S1')         | 0.698 | 0.828 | 134.647 |     -2.478 |             nan     |
| (7, 'LSTM_ALL_UP_S2')         | 0.672 | 0.794 | 140.335 |      5.917 |             nan     |
| (7, 'LSTM_BASE_STEP2_STEP3')  | 0.354 | 0.278 | 197.126 |    -79.824 |             nan     |
| (7, 'LSTM_FRAIN_STEP2_STEP3') | 0.687 | 0.624 | 137.235 |    -29.178 |             nan     |
| (7, 'LSTM_PEAK_STEP2_STEP3')  | 0.401 | 0.551 | 189.704 |    -66.455 |             nan     |
| (7, 'LSTM_PHYS_STEP2_STEP3')  | 0.358 | 0.303 | 196.492 |    -78.524 |             nan     |
| (7, 'TFT_PHYS_STEP2_STEP3')   | 0.406 | 0.582 | 188.982 |    -60.153 |              95.737 |
| (7, 'TFT_V2_LONG_STEP3')      | 0.721 | 0.822 | 129.484 |      2.249 |              94.532 |
| (7, 'TFT_V2_STEP2_STEP3')     | 0.694 | 0.825 | 135.732 |     -7.442 |              93.142 |
