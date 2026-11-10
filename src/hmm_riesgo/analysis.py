"""Análisis estadístico de los resultados Monte Carlo."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, t

PRIMARY_METRICS = {
    "detection_rate_4w": "Tasa de detección a 4 semanas",
    "auc": "Área bajo la curva ROC (AUC)",
    "fpr": "Tasa de falsos positivos semanal",
    "latency_mean": "Latencia media de detección (semanas)",
    "brier": "Puntuación de Brier",
    "prevalence_rmse": "RMSE de prevalencia semanal",
    "entropy": "Entropía media de la posterior",
    "recovery_rate": "Tasa de recuperación R→C",
    "mean_time_risk": "Tiempo medio en riesgo",
    "alarm_student_rate": "Cobertura de alertas por estudiante",
}


def ci_mean(values: np.ndarray, confidence: float = 0.95) -> tuple[float, float]:
    """IC para la media basado en la distribución t de Student."""
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n < 2:
        return (float("nan"), float("nan"))
    se = x.std(ddof=1) / np.sqrt(n)
    crit = t.ppf(0.5 + confidence / 2.0, df=n - 1)
    m = x.mean()
    return (float(m - crit * se), float(m + crit * se))


def descriptive_table(df: pd.DataFrame, metrics: dict | None = None) -> pd.DataFrame:
    """Media, desviación, mínimo, máximo, mediana e IC95 % por escenario."""
    metrics = PRIMARY_METRICS if metrics is None else metrics
    rows = []
    for scenario, group in df.groupby("scenario", sort=True):
        for metric, label in metrics.items():
            if metric not in group:
                continue
            x = group[metric].to_numpy(dtype=float)
            finite = x[np.isfinite(x)]
            if finite.size == 0:
                continue
            lo, hi = ci_mean(finite)
            rows.append(
                {
                    "scenario": scenario,
                    "metric": metric,
                    "label": label,
                    "n": int(finite.size),
                    "mean": float(finite.mean()),
                    "sd": float(finite.std(ddof=1)) if finite.size > 1 else 0.0,
                    "min": float(finite.min()),
                    "max": float(finite.max()),
                    "median": float(np.median(finite)),
                    "ci_low": lo,
                    "ci_high": hi,
                    "se": float(finite.std(ddof=1) / np.sqrt(finite.size))
                    if finite.size > 1
                    else 0.0,
                }
            )
    return pd.DataFrame(rows)


def kruskal_by_scenario(df: pd.DataFrame, metric: str) -> dict:
    groups = [
        g[metric].dropna().to_numpy(dtype=float)
        for _, g in df.groupby("scenario", sort=True)
        if g[metric].notna().any()
    ]
    if len(groups) < 2:
        return {
            "metric": metric,
            "H": float("nan"),
            "df": 0,
            "p_value": float("nan"),
            "epsilon_squared": float("nan"),
        }
    H, p = kruskal(*groups)
    n = sum(g.size for g in groups)
    k = len(groups)
    eps = max(0.0, (H - k + 1.0) / (n - k)) if n > k else float("nan")
    return {
        "metric": metric,
        "H": float(H),
        "df": k - 1,
        "p_value": float(p),
        "epsilon_squared": float(eps),
    }


def holm_adjust(pvalues: list[float]) -> list[float]:
    """Corrección de Holm-Bonferroni."""
    m = len(pvalues)
    order = np.argsort(pvalues)
    adjusted = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        adj = (m - rank) * pvalues[idx]
        running = max(running, adj)
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()


def pairwise_table(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Mann-Whitney U con corrección de Holm y delta de Cliff."""
    scenarios = sorted(df["scenario"].unique())
    rows = []
    for a, b in combinations(scenarios, 2):
        xa = df.loc[df.scenario == a, metric].dropna().to_numpy(dtype=float)
        xb = df.loc[df.scenario == b, metric].dropna().to_numpy(dtype=float)
        if xa.size < 2 or xb.size < 2:
            continue
        res = mannwhitneyu(xa, xb, alternative="two-sided")
        delta = 2.0 * res.statistic / (xa.size * xb.size) - 1.0
        rows.append(
            {
                "metric": metric,
                "scenario_1": a,
                "scenario_2": b,
                "U": float(res.statistic),
                "p_raw": float(res.pvalue),
                "cliffs_delta": float(delta),
                "n_1": int(xa.size),
                "n_2": int(xb.size),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["p_holm"] = holm_adjust(out["p_raw"].tolist())
        out["significant_0.05"] = out["p_holm"] < 0.05
    return out


def tests_summary(df: pd.DataFrame, metrics: dict | None = None) -> pd.DataFrame:
    metrics = PRIMARY_METRICS if metrics is None else metrics
    rows = [kruskal_by_scenario(df, m) for m in metrics if m in df.columns]
    return pd.DataFrame(rows)


def pairwise_summary(df: pd.DataFrame, metrics: dict | None = None) -> pd.DataFrame:
    metrics = PRIMARY_METRICS if metrics is None else metrics
    frames = [pairwise_table(df, m) for m in metrics if m in df.columns]
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def format_ci(row: pd.Series, digits: int = 3) -> str:
    """Formato compacto 'media (IC)' para tablas del artículo."""
    return (
        f"{row['mean']:.{digits}f} "
        f"[{row['ci_low']:.{digits}f}, {row['ci_high']:.{digits}f}]"
    )


def scenario_labels(df: pd.DataFrame) -> dict[str, str]:
    return (
        df.drop_duplicates("scenario")
        .set_index("scenario")["scenario_name"]
        .to_dict()
    )
