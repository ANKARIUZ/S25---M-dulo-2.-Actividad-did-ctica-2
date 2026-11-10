"""Motores de simulación Monte Carlo y ejecución de réplicas."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
import pandas as pd

from .hmm import DiscreteHMM, logsumexp
from .metrics import recovery_rate, roc_curve, student_metrics
from .scenarios import Scenario


def _seed_from_key(master_seed: int, key: str, rep: int) -> int:
    """Semilla estable e independiente de la plataforma."""
    digest = hashlib.sha256(f"{master_seed}:{key}:{rep}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def run_replication(
    scenario: Scenario,
    n_students: int = 1000,
    T: int = 16,
    seed: int = 0,
    threshold: float = 0.5,
    consecutive: int = 2,
    horizon: int = 4,
    return_arrays: bool = False,
) -> dict:
    """Simula una cohorte, filtra en línea y calcula métricas."""
    rng = np.random.default_rng(seed)
    hmm = DiscreteHMM(**scenario.model_kwargs())
    states, obs = hmm.sample(T=T, n_sequences=n_students, rng=rng)

    log_alpha, loglik = hmm.forward(obs)
    post = np.exp(log_alpha - logsumexp(log_alpha, axis=2, keepdims=True))
    post /= post.sum(axis=2, keepdims=True)
    risk = post[:, :, 1]

    metrics, student = student_metrics(
        states,
        risk,
        threshold=threshold,
        consecutive=consecutive,
        horizon=horizon,
        posterior=post,
    )
    metrics.update(
        {
            "scenario": scenario.key,
            "scenario_name": scenario.name,
            "seed": int(seed),
            "T": int(T),
            "n_students": int(n_students),
            "recovery_rate": recovery_rate(states),
            "loglik_mean": float(np.mean(loglik)),
            "threshold": float(threshold),
            "consecutive": int(consecutive),
            "horizon": int(horizon),
        }
    )
    if return_arrays:
        return {
            "metrics": metrics,
            "student": student,
            "states": states,
            "obs": obs,
            "posterior": post,
            "risk": risk,
            "hmm": hmm,
        }
    return metrics


def run_scenario(
    scenario: Scenario,
    n_reps: int = 50,
    n_students: int = 1000,
    T: int = 16,
    master_seed: int = 2025,
    threshold: float = 0.5,
    consecutive: int = 2,
    horizon: int = 4,
    progress: bool = True,
    return_roc: bool = False,
    roc_points: int = 201,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    """Ejecuta ``n_reps`` réplicas independientes de un escenario.

    Si ``return_roc`` es True, devuelve además las curvas ROC interpoladas
    en una rejilla común de FPR, útiles para promediar curvas entre réplicas.
    """
    rows = []
    roc_rows = []
    t0 = time.perf_counter()
    for rep in range(n_reps):
        seed = _seed_from_key(master_seed, scenario.key, rep)
        if return_roc:
            result = run_replication(
                scenario,
                n_students=n_students,
                T=T,
                seed=seed,
                threshold=threshold,
                consecutive=consecutive,
                horizon=horizon,
                return_arrays=True,
            )
            row = result["metrics"]
            fpr, tpr, _ = roc_curve(
                (result["states"] == 1).ravel(), result["risk"].ravel()
            )
            grid = np.linspace(0.0, 1.0, roc_points)
            tpr_grid = np.interp(grid, fpr, tpr)
            for f, tp in zip(grid, tpr_grid):
                roc_rows.append(
                    {
                        "scenario": scenario.key,
                        "replication": rep,
                        "fpr": float(f),
                        "tpr": float(tp),
                    }
                )
        else:
            row = run_replication(
                scenario,
                n_students=n_students,
                T=T,
                seed=seed,
                threshold=threshold,
                consecutive=consecutive,
                horizon=horizon,
            )
        row["replication"] = rep
        rows.append(row)
        if progress and ((rep + 1) % 10 == 0 or rep == n_reps - 1):
            elapsed = time.perf_counter() - t0
            print(
                f"  [{scenario.key}] réplica {rep + 1}/{n_reps} "
                f"({elapsed:.1f} s)"
            )
    df = pd.DataFrame(rows)
    if return_roc:
        return df, pd.DataFrame(roc_rows)
    return df


def run_custom(
    A: np.ndarray,
    B: np.ndarray,
    pi: np.ndarray,
    n_reps: int = 20,
    n_students: int = 500,
    T: int = 16,
    master_seed: int = 2025,
    key: str = "X",
    name: str = "Personalizado",
    color: str = "#555555",
    threshold: float = 0.5,
    consecutive: int = 2,
    horizon: int = 4,
    progress: bool = False,
) -> pd.DataFrame:
    """Simula un modelo arbitrario (usado en el análisis de sensibilidad)."""
    sc = Scenario(
        key=key,
        name=name,
        description="Modelo personalizado para análisis de sensibilidad.",
        A=np.asarray(A, dtype=float),
        B=np.asarray(B, dtype=float),
        pi=np.asarray(pi, dtype=float),
        color=color,
    )
    return run_scenario(
        sc,
        n_reps=n_reps,
        n_students=n_students,
        T=T,
        master_seed=master_seed,
        threshold=threshold,
        consecutive=consecutive,
        horizon=horizon,
        progress=progress,
    )


def run_custom_once(
    A: np.ndarray,
    B: np.ndarray,
    pi: np.ndarray,
    n_students: int = 500,
    T: int = 16,
    seed: int = 0,
    key: str = "X",
    name: str = "Personalizado",
    color: str = "#555555",
) -> dict:
    """Una sola réplica de un modelo arbitrario (para curvas ROC y figuras)."""
    sc = Scenario(
        key=key,
        name=name,
        description="Modelo personalizado.",
        A=np.asarray(A, dtype=float),
        B=np.asarray(B, dtype=float),
        pi=np.asarray(pi, dtype=float),
        color=color,
    )
    return run_replication(
        sc, n_students=n_students, T=T, seed=seed, return_arrays=True
    )
