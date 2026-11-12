import numpy as np


def _clean(obs, sim):
    obs, sim = np.asarray(obs, float), np.asarray(sim, float)
    m = np.isfinite(obs) & np.isfinite(sim)
    return obs[m], sim[m]


def nse(obs, sim):
    obs, sim = _clean(obs, sim)
    if len(obs) < 2 or np.var(obs) == 0:
        return np.nan
    return 1 - np.sum((sim - obs) ** 2) / np.sum((obs - obs.mean()) ** 2)


def kge(obs, sim):
    obs, sim = _clean(obs, sim)
    if len(obs) < 2 or obs.std() == 0 or obs.mean() == 0:
        return np.nan
    r = np.corrcoef(obs, sim)[0, 1]
    alpha = sim.std() / obs.std()
    beta = sim.mean() / obs.mean()
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)


def rmse(obs, sim):
    obs, sim = _clean(obs, sim)
    return np.sqrt(np.mean((sim - obs) ** 2)) if len(obs) else np.nan


def peak_error(obs, sim, top=0.02):
    """Mean relative error (%) on the highest `top` fraction of observed flows (flood days)."""
    obs, sim = _clean(obs, sim)
    if len(obs) < 50:
        return np.nan
    thr = np.quantile(obs, 1 - top)
    m = obs >= thr
    return 100 * np.mean((sim[m] - obs[m]) / np.maximum(obs[m], 1e-6))


def all_metrics(obs, sim):
    return {"NSE": nse(obs, sim), "KGE": kge(obs, sim), "RMSE": rmse(obs, sim), "PeakErr%": peak_error(obs, sim)}
