"""Hierarchical Risk Parity (Lopez de Prado, 2016).

Allocates by clustering assets on correlation distance, reordering the
covariance so similar assets sit together, then splitting capital recursively
in inverse proportion to each cluster's variance. It never inverts the
covariance matrix, which is why it is robust when the matrix is ill-conditioned
- many assets, few observations.

It uses risk only and ignores expected returns entirely. That is a feature when
expected returns are noisy estimates, and a cost when they are published
contractual numbers, as SEC yields are.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform


def _quasi_diag(link):
    link = link.astype(int)
    order = pd.Series([link[-1, 0], link[-1, 1]])
    n = link[-1, 3]
    while order.max() >= n:
        order.index = range(0, order.shape[0] * 2, 2)
        df = order[order >= n]
        i, j = df.index, df.values - n
        order[i] = link[j, 0]
        order = pd.concat([order, pd.Series(link[j, 1], index=i + 1)])
        order = order.sort_index()
        order.index = range(order.shape[0])
    return order.tolist()


def _cluster_var(cov, items):
    c = cov.loc[items, items]
    ivp = 1.0 / np.diag(c)
    ivp /= ivp.sum()
    return float(ivp @ c.to_numpy() @ ivp)


def _recursive_bisection(cov, order):
    w = pd.Series(1.0, index=order)
    clusters = [order]
    while clusters:
        clusters = [c[k:m] for c in clusters for k, m in ((0, len(c) // 2), (len(c) // 2, len(c)))
                    if len(c) > 1]
        for i in range(0, len(clusters), 2):
            a, b = clusters[i], clusters[i + 1]
            va, vb = _cluster_var(cov, a), _cluster_var(cov, b)
            alpha = 1 - va / (va + vb)
            w[a] *= alpha
            w[b] *= 1 - alpha
    return w


def hrp_weights(returns: pd.DataFrame, cap: float | None = None) -> pd.Series:
    """HRP allocation, optionally re-normalised under a position cap."""
    cov = returns.cov()
    corr = returns.corr().fillna(0.0)
    dist = np.sqrt(np.clip(0.5 * (1 - corr), 0, None))
    link = linkage(squareform(dist.to_numpy(), checks=False), method="single")
    order = [returns.columns[i] for i in _quasi_diag(link)]
    w = _recursive_bisection(cov, order)
    w = (w / w.sum()).reindex(returns.columns).fillna(0.0)

    if cap:                       # water-fill the excess over the cap
        for _ in range(200):
            over = w > cap
            if not over.any():
                break
            excess = (w[over] - cap).sum()
            w[over] = cap
            room = w[~over]
            if room.sum() <= 0:
                break
            w[~over] = room + excess * room / room.sum()
        w = w / w.sum()
    return w
