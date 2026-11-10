"""
Métricas de simulación y de detección en línea.

La verdad latente solo se conoce porque los datos son simulados; por eso se
pueden medir sensibilidad, falsos positivos y latencia de detección, algo
imposible de observar directamente en una cohorte real.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import rankdata


def roc_auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Área bajo la curva ROC por el estadístico de Mann-Whitney (con empates)."""
    y = np.asarray(y_true, dtype=bool).ravel()
    s = np.asarray(scores, dtype=float).ravel()
    if y.size != s.size:
        raise ValueError("y_true y scores deben tener el mismo tamaño")
    n_pos = int(y.sum())
    n_neg = int((~y).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = rankdata(s, method="average")
    return float((ranks[y].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def roc_curve(
    y_true: np.ndarray, scores: np.ndarray, n_points: int = 600
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Curva ROC y umbrales, submuestreada para graficar."""
    y = np.asarray(y_true, dtype=bool).ravel()
    s = np.asarray(scores, dtype=float).ravel()
    order = np.argsort(-s, kind="mergesort")
    s_sorted = s[order]
    y_sorted = y[order]

    tps = np.cumsum(y_sorted)
    fps = np.cumsum(~y_sorted)
    n_pos = max(int(y.sum()), 1)
    n_neg = max(int((~y).sum()), 1)

    # Conservar solo el último punto de cada umbral distinto.
    distinct = np.r_[np.flatnonzero(np.diff(s_sorted)), s_sorted.size - 1]
    tpr = np.r_[0.0, tps[distinct] / n_pos]
    fpr = np.r_[0.0, fps[distinct] / n_neg]
    thr = np.r_[np.inf, s_sorted[distinct]]

    if fpr.size > n_points:
        idx = np.linspace(0, fpr.size - 1, n_points).astype(int)
        fpr, tpr, thr = fpr[idx], tpr[idx], thr[idx]
    return fpr, tpr, thr


def brier_score(y_true: np.ndarray, prob: np.ndarray) -> float:
    y = np.asarray(y_true, dtype=float).ravel()
    p = np.asarray(prob, dtype=float).ravel()
    return float(np.mean((p - y) ** 2))


def _rolling_run(mask: np.ndarray) -> np.ndarray:
    """Longitud de la racha de True que termina en cada posición."""
    n, T = mask.shape
    run = np.zeros((n, T), dtype=int)
    run[:, 0] = mask[:, 0]
    for t in range(1, T):
        run[:, t] = np.where(mask[:, t], run[:, t - 1] + 1, 0)
    return run


def student_metrics(
    states: np.ndarray,
    risk: np.ndarray,
    threshold: float = 0.5,
    consecutive: int = 2,
    horizon: int = 4,
    posterior: np.ndarray | None = None,
) -> tuple[dict, dict]:
    """Calcula métricas por estudiante y las agrega a nivel de réplica.

    ``risk`` es P(S_t = R | o_1..o_t), es decir, la probabilidad filtrada que
    estaría disponible en línea al final de cada semana. ``posterior`` permite
    calcular la entropía completa de los tres estados.
    """
    states = np.asarray(states, dtype=int)
    risk = np.asarray(risk, dtype=float)
    if states.shape != risk.shape:
        raise ValueError("states y risk deben tener la misma forma (N, T)")
    n, T = states.shape
    true_r = states == 1
    flags = risk >= threshold
    runs = _rolling_run(flags)
    triggers = runs >= consecutive

    t_grid = np.arange(T)[None, :]
    has_onset = true_r.any(axis=1)
    onset = np.argmax(true_r, axis=1)  # primer índice en R (0 si no hay)

    after_onset = triggers & (t_grid >= onset[:, None])
    has_alarm_after = after_onset.any(axis=1)
    alarm_after = np.argmax(after_onset, axis=1)
    latency = np.where(has_alarm_after, alarm_after - onset, T - onset)

    eligible_4w = has_onset & (onset <= T - horizon)
    detected_4w = has_alarm_after & (latency < horizon)
    det_rate_4w = (
        float(detected_4w[eligible_4w].mean()) if eligible_4w.any() else float("nan")
    )

    detected_any = has_onset & has_alarm_after
    latency_detected = latency[detected_any]

    tp = int((flags & true_r).sum())
    fp = int((flags & ~true_r).sum())
    fn = int((~flags & true_r).sum())
    tn = int((~flags & ~true_r).sum())
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision == precision and recall == recall and (precision + recall) > 0
        else float("nan")
    )
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")

    # RMSE de prevalencia semanal: qué tan bien el filtro agregado sigue a la
    # proporción real de estudiantes en riesgo.
    prevalence_hat = risk.mean(axis=0)
    prevalence_true = true_r.mean(axis=0)
    prevalence_rmse = float(np.sqrt(np.mean((prevalence_hat - prevalence_true) ** 2)))

    # Entropía media de la posterior filtrada (incertidumbre del filtro).
    if posterior is None:
        all_post = np.stack([1.0 - risk, risk], axis=2)  # solo C/R para brevedad
    else:
        all_post = np.asarray(posterior, dtype=float)
        if all_post.shape != (n, T, 3):
            raise ValueError("posterior debe tener forma (N, T, 3)")
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -np.nansum(np.where(all_post > 0, all_post * np.log(all_post), 0.0), axis=2)
    entropy = float(np.mean(ent))

    student = {
        "onset": onset,
        "latency": latency,
        "detected_any": detected_any,
        "detected_4w": detected_4w,
        "eligible_4w": eligible_4w,
        "alarm_after": alarm_after,
        "has_alarm_after": has_alarm_after,
        "pre_alarm": (triggers & (t_grid < onset[:, None])).any(axis=1),
        "pre_alarm_week": np.where(
            (triggers & (t_grid < onset[:, None])).any(axis=1),
            np.argmax(triggers & (t_grid < onset[:, None]), axis=1),
            -1,
        ),
        "risk_mean": risk.mean(axis=1),
        "time_risk": true_r.mean(axis=1),
        "time_inactive": (states == 2).mean(axis=1),
    }

    summary = {
        "n_students": int(n),
        "n_onset": int(has_onset.sum()),
        "n_eligible_4w": int(eligible_4w.sum()),
        "detection_rate_4w": det_rate_4w,
        "detection_rate_any": (
            float(detected_any[has_onset].mean()) if has_onset.any() else float("nan")
        ),
        "censored_rate": (
            float((~has_alarm_after[has_onset]).mean()) if has_onset.any() else float("nan")
        ),
        "latency_mean": (
            float(latency_detected.mean()) if latency_detected.size else float("nan")
        ),
        "latency_median": (
            float(np.median(latency_detected)) if latency_detected.size else float("nan")
        ),
        "latency_p90": (
            float(np.percentile(latency_detected, 90)) if latency_detected.size else float("nan")
        ),
        "recall": float(recall),
        "precision": float(precision),
        "f1": float(f1),
        "fpr": float(fpr),
        "auc": roc_auc(true_r.ravel(), risk.ravel()),
        "brier": brier_score(true_r.ravel(), risk.ravel()),
        "prevalence_rmse": prevalence_rmse,
        "entropy": entropy,
        "prevalence_risk_true": float(true_r.mean()),
        "prevalence_risk_hat": float(risk.mean()),
        "mean_time_risk": float(true_r.mean(axis=1).mean()),
        "mean_time_inactive": float((states == 2).mean(axis=1).mean()),
        "alarm_student_rate": float(triggers.any(axis=1).mean()),
        "mean_flags_per_student": float(flags.sum(axis=1).mean()),
        "pre_alarm_student_rate": float(
            (triggers & (t_grid < onset[:, None])).any(axis=1).mean()
        ),
    }
    if latency_detected.size:
        summary["latency_sd"] = float(latency_detected.std(ddof=1))
    else:
        summary["latency_sd"] = float("nan")
    return summary, student


def recovery_rate(states: np.ndarray) -> float:
    """Proporción de transiciones R -> C entre todas las salidas de R."""
    states = np.asarray(states, dtype=int)
    if states.shape[1] < 2:
        return float("nan")
    origin = states[:, :-1]
    dest = states[:, 1:]
    out_r = origin == 1
    if not out_r.any():
        return float("nan")
    return float(((dest == 0) & out_r).sum() / out_r.sum())
