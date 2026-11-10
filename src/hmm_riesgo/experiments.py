"""
Diseño experimental: escenarios principales, recuperación de parámetros y
análisis de sensibilidad.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from .analysis import (
    descriptive_table,
    pairwise_summary,
    tests_summary,
)
from .hmm import DiscreteHMM
from .scenarios import (
    A_BASE,
    B_SEPARABLE,
    PI_BASE,
    SCENARIOS,
    SCENARIO_BY_KEY,
    Scenario,
    emission_matrix,
    parameter_records,
    save_parameters,
    transition_with_persistence,
)
from .simulation import _seed_from_key, run_custom, run_replication, run_scenario

MASTER_SEED = 2025
N_REPS_MAIN = 50
N_STUDENTS_MAIN = 1000
T_WEEKS = 16

SENS_DELTAS = [0.2, 0.4, 0.6, 0.8, 1.0]
SENS_PSTAY = [0.60, 0.75, 0.90]
SENS_REPS = 15
SENS_STUDENTS = 500
SENS_SEED = 4242

OAT_FACTORS = [0.8, 1.2]
OAT_REPS = 20
OAT_STUDENTS = 500
OAT_SEED = 555


def _normalize_rows(M: np.ndarray) -> np.ndarray:
    M = np.clip(np.asarray(M, dtype=float), 1e-12, None)
    return M / M.sum(axis=1, keepdims=True)


def _perturb(M: np.ndarray, rng: np.random.Generator, sigma: float = 0.35) -> np.ndarray:
    """Multiplica por ruido log-normal y renormaliza filas."""
    return _normalize_rows(M * np.exp(rng.normal(0.0, sigma, size=M.shape)))


def _align_states(est: DiscreteHMM, true: DiscreteHMM) -> np.ndarray:
    """Empareja estados estimados con verdaderos minimizando una distancia mixta."""
    K = true.K
    cost = np.zeros((K, K), dtype=float)
    for i in range(K):
        for k in range(K):
            cost[i, k] = (
                2.0 * np.abs(est.B[k] - true.B[i]).sum()
                + np.abs(est.A[k] - true.A[i]).sum()
                + abs(est.pi[k] - true.pi[i])
            )
    rows, cols = linear_sum_assignment(cost)
    perm = np.empty(K, dtype=int)
    perm[rows] = cols
    return perm


def _reorder(hmm: DiscreteHMM, perm: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        hmm.A[np.ix_(perm, perm)],
        hmm.B[perm, :],
        hmm.pi[perm],
    )


# ----------------------------------------------------------------------
# Experimento principal
# ----------------------------------------------------------------------
def run_main(results_dir: Path, force: bool = False) -> pd.DataFrame:
    raw = results_dir / "raw" / "main_replications.csv"
    roc_path = results_dir / "raw" / "roc_curves.csv"
    if raw.exists() and not force:
        print(f"[main] existe {raw}; se reutiliza (use --force para recalcular)")
        return pd.read_csv(raw)

    print("[main] 4 escenarios x 50 réplicas x 1000 estudiantes")
    frames = []
    roc_frames = []
    t0 = time.perf_counter()
    for sc in SCENARIOS:
        df, roc = run_scenario(
            sc,
            n_reps=N_REPS_MAIN,
            n_students=N_STUDENTS_MAIN,
            T=T_WEEKS,
            master_seed=MASTER_SEED,
            return_roc=True,
            progress=True,
        )
        frames.append(df)
        roc_frames.append(roc)

    main = pd.concat(frames, ignore_index=True)
    roc = pd.concat(roc_frames, ignore_index=True)
    main.to_csv(raw, index=False)
    roc.to_csv(roc_path, index=False)

    desc = descriptive_table(main)
    desc.to_csv(results_dir / "tables" / "main_descriptives.csv", index=False)
    tests_summary(main).to_csv(results_dir / "tables" / "main_tests.csv", index=False)
    pairwise_summary(main).to_csv(
        results_dir / "tables" / "main_pairwise.csv", index=False
    )
    print(
        f"[main] listo en {time.perf_counter() - t0:.1f} s; "
        f"{len(main)} réplicas"
    )
    return main


# ----------------------------------------------------------------------
# Recuperación de parámetros (Baum-Welch)
# ----------------------------------------------------------------------
def run_estimation(results_dir: Path, force: bool = False) -> pd.DataFrame:
    raw = results_dir / "raw" / "estimation_replications.csv"
    if raw.exists() and not force:
        print(f"[estimation] existe {raw}; se reutiliza")
        return pd.read_csv(raw)

    print("[estimation] Baum-Welch con inicialización perturbada")
    rows = []
    param_rows = []
    t0 = time.perf_counter()
    for sc in SCENARIOS:
        for rep in range(10):
            seed = _seed_from_key(2026, "EST" + sc.key, rep)
            rng = np.random.default_rng(seed)
            true = DiscreteHMM(**sc.model_kwargs())
            _, obs = true.sample(T=T_WEEKS, n_sequences=300, rng=rng)

            init = (
                _perturb(sc.A, rng),
                _perturb(sc.B, rng),
                _normalize_rows(sc.pi[None, :])[0],
            )
            est = DiscreteHMM(**sc.model_kwargs())
            history = est.baum_welch(obs, n_iter=120, tol=1e-6, init=init)
            perm = _align_states(est, true)
            A_hat, B_hat, pi_hat = _reorder(est, perm)

            mae_A = float(np.abs(A_hat - sc.A).mean())
            mae_B = float(np.abs(B_hat - sc.B).mean())
            mae_pi = float(np.abs(pi_hat - sc.pi).mean())
            fro_A = float(np.linalg.norm(A_hat - sc.A, ord="fro"))
            fro_B = float(np.linalg.norm(B_hat - sc.B, ord="fro"))
            ll_true = float(np.sum(true.score(obs)))
            ll_hat = float(np.sum(est.score(obs)))

            rows.append(
                {
                    "scenario": sc.key,
                    "scenario_name": sc.name,
                    "replication": rep,
                    "seed": seed,
                    "mae_A": mae_A,
                    "mae_B": mae_B,
                    "mae_pi": mae_pi,
                    "fro_A": fro_A,
                    "fro_B": fro_B,
                    "ll_true": ll_true,
                    "ll_hat": ll_hat,
                    "ll_gain": ll_hat - ll_true,
                    "iterations": history.iterations,
                    "converged": int(history.converged),
                    "final_delta": history.parameter_delta[-1]
                    if history.parameter_delta
                    else float("nan"),
                    "permutation": "".join(str(x) for x in perm),
                }
            )
            for i in range(3):
                for j in range(3):
                    param_rows.append(
                        {
                            "scenario": sc.key,
                            "replication": rep,
                            "matrix": "A",
                            "row": i,
                            "col": j,
                            "true": float(sc.A[i, j]),
                            "estimated": float(A_hat[i, j]),
                        }
                    )
            for i in range(3):
                for j in range(3):
                    param_rows.append(
                        {
                            "scenario": sc.key,
                            "replication": rep,
                            "matrix": "B",
                            "row": i,
                            "col": j,
                            "true": float(sc.B[i, j]),
                            "estimated": float(B_hat[i, j]),
                        }
                    )
            for i in range(3):
                param_rows.append(
                    {
                        "scenario": sc.key,
                        "replication": rep,
                        "matrix": "pi",
                        "row": 0,
                        "col": i,
                        "true": float(sc.pi[i]),
                        "estimated": float(pi_hat[i]),
                    }
                )

    est_df = pd.DataFrame(rows)
    est_df.to_csv(raw, index=False)
    pd.DataFrame(param_rows).to_csv(
        results_dir / "raw" / "estimation_parameters.csv", index=False
    )

    summary = (
        est_df.groupby(["scenario", "scenario_name"])
        .agg(
            mae_A_mean=("mae_A", "mean"),
            mae_A_sd=("mae_A", "std"),
            mae_B_mean=("mae_B", "mean"),
            mae_B_sd=("mae_B", "std"),
            mae_pi_mean=("mae_pi", "mean"),
            mae_pi_sd=("mae_pi", "std"),
            ll_gain_mean=("ll_gain", "mean"),
            ll_gain_sd=("ll_gain", "std"),
            iterations_mean=("iterations", "mean"),
            convergence_rate=("converged", "mean"),
            n=("mae_A", "size"),
        )
        .reset_index()
    )
    summary.to_csv(results_dir / "tables" / "estimation_summary.csv", index=False)
    print(
        f"[estimation] listo en {time.perf_counter() - t0:.1f} s; "
        f"{len(est_df)} ajustes"
    )
    return est_df


# ----------------------------------------------------------------------
# Ejemplos individuales para la figura de trayectorias
# ----------------------------------------------------------------------
def make_examples(results_dir: Path) -> Path:
    """Selecciona dos estudiantes reales de la simulación para ilustrar.

    A: transición temprana a riesgo con detección en <= 2 semanas.
    B: transición temprana sin alarma en el horizonte de 16 semanas.
    """
    payload: dict[str, np.ndarray] = {}
    for key, mode in (("A", "early"), ("B", "missed")):
        chosen = None
        for seed in range(1, 40):
            res = run_replication(
                SCENARIO_BY_KEY[key],
                n_students=2000,
                T=T_WEEKS,
                seed=seed,
                return_arrays=True,
            )
            onset = res["student"]["onset"]
            latency = res["student"]["latency"]
            detected = res["student"]["detected_any"]
            alarm = res["student"]["alarm_after"]
            pre_alarm = res["student"]["pre_alarm"]
            if mode == "early":
                mask = (
                    (onset >= 1)
                    & (onset <= 5)
                    & detected
                    & (latency <= 2)
                    & (res["states"][np.arange(len(onset)), np.minimum(alarm, T_WEEKS - 1)] == 1)
                )
            else:
                mask = (onset >= 1) & (onset <= 5) & (~detected)
                if pre_alarm[mask].any():
                    mask = mask & pre_alarm
            idx = np.flatnonzero(mask)
            if idx.size:
                i = int(idx[0])
                chosen = {
                    "seed": seed,
                    "student": i,
                    "onset": int(onset[i]),
                    "alarm": int(alarm[i]) if detected[i] else -1,
                    "latency": float(latency[i]),
                    "detected": bool(detected[i]),
                    "pre_alarm": bool(pre_alarm[i]),
                    "pre_alarm_week": int(res["student"]["pre_alarm_week"][i]),
                    "states": res["states"][i],
                    "obs": res["obs"][i],
                    "risk": res["risk"][i],
                    "posterior": res["posterior"][i],
                }
                break
        if chosen is None:
            raise RuntimeError(f"No se encontró un ejemplo para el escenario {key}")
        payload[f"{key}_states"] = chosen["states"]
        payload[f"{key}_obs"] = chosen["obs"]
        payload[f"{key}_risk"] = chosen["risk"]
        payload[f"{key}_posterior"] = chosen["posterior"]
        payload[f"{key}_meta"] = np.array(
            [
                chosen["seed"],
                chosen["student"],
                chosen["onset"],
                chosen["alarm"],
                int(chosen["detected"]),
                int(chosen["pre_alarm"]),
                chosen["pre_alarm_week"],
            ]
        )
    path = results_dir / "raw" / "example_trajectories.npz"
    np.savez_compressed(path, **payload)
    return path


# ----------------------------------------------------------------------
# Sensibilidad global (rejilla separabilidad x persistencia)
# ----------------------------------------------------------------------
def run_sensitivity_grid(results_dir: Path, force: bool = False) -> pd.DataFrame:
    raw = results_dir / "raw" / "sensitivity_grid_replications.csv"
    summary_path = results_dir / "tables" / "sensitivity_grid.csv"
    if summary_path.exists() and not force:
        print(f"[sensitivity] existe {summary_path}; se reutiliza")
        return pd.read_csv(summary_path)

    print("[sensitivity] rejilla separabilidad x persistencia")
    frames = []
    t0 = time.perf_counter()
    for delta in SENS_DELTAS:
        for p_stay in SENS_PSTAY:
            A = transition_with_persistence(p_stay)
            B = emission_matrix(delta)
            key = f"d{delta:.2f}_p{p_stay:.2f}"
            df = run_custom(
                A,
                B,
                PI_BASE,
                n_reps=SENS_REPS,
                n_students=SENS_STUDENTS,
                T=T_WEEKS,
                master_seed=SENS_SEED,
                key=key,
                name=f"δ={delta:.2f}, p={p_stay:.2f}",
                progress=False,
            )
            df["delta"] = delta
            df["p_stay_risk"] = p_stay
            frames.append(df)

    reps = pd.concat(frames, ignore_index=True)
    reps.to_csv(raw, index=False)

    summary = (
        reps.groupby(["delta", "p_stay_risk"])
        .agg(
            auc_mean=("auc", "mean"),
            auc_sd=("auc", "std"),
            det4_mean=("detection_rate_4w", "mean"),
            det4_sd=("detection_rate_4w", "std"),
            fpr_mean=("fpr", "mean"),
            fpr_sd=("fpr", "std"),
            prevalence_mean=("prevalence_risk_true", "mean"),
            latency_mean=("latency_mean", "mean"),
            n_reps=("auc", "size"),
        )
        .reset_index()
    )
    summary.to_csv(summary_path, index=False)
    print(
        f"[sensitivity] listo en {time.perf_counter() - t0:.1f} s; "
        f"{len(reps)} réplicas"
    )
    return summary


# ----------------------------------------------------------------------
# Sensibilidad one-at-a-time (elasticidades)
# ----------------------------------------------------------------------
def _perturb_group(
    group: str,
    factor: float,
    A: np.ndarray,
    B: np.ndarray,
    pi: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    A2, B2, pi2 = A.copy(), B.copy(), pi.copy()
    if group.startswith("A_"):
        idx = {"A_C": 0, "A_R": 1, "A_I": 2}[group]
        # Perturbar las salidas del estado y dejar que la diagonal se ajuste:
        # así el factor modifica directamente la persistencia.
        exits = A2[idx].copy()
        exits[idx] = 0.0
        exits *= factor
        new_row = exits
        new_row[idx] = 1.0 - exits.sum()
        if new_row[idx] <= 0:
            raise ValueError("la perturbación produjo una probabilidad inválida")
        A2[idx] = new_row
    elif group.startswith("B_"):
        idx = {"B_C": 0, "B_R": 1, "B_I": 2}[group]
        target = {"B_C": 0, "B_R": 1, "B_I": 2}[group]  # Alta, Media, Baja
        row = B2[idx].copy()
        row[target] *= factor
        B2[idx] = row / row.sum()
    elif group == "pi_R":
        pi2[1] *= factor
        pi2 /= pi2.sum()
    else:
        raise ValueError(f"grupo desconocido: {group}")
    return A2, B2, pi2


def run_sensitivity_oat(results_dir: Path, force: bool = False) -> pd.DataFrame:
    path = results_dir / "tables" / "sensitivity_oat.csv"
    if path.exists() and not force:
        print(f"[oat] existe {path}; se reutiliza")
        return pd.read_csv(path)

    print("[oat] perturbaciones one-at-a-time (±20 %)")
    groups = {
        "A_C": "Fila C de A (permanencia en compromiso)",
        "A_R": "Fila R de A (persistencia del riesgo)",
        "A_I": "Fila I de A (permanencia en inactividad)",
        "B_C": "Emisiones de C",
        "B_R": "Emisiones de R",
        "B_I": "Emisiones de I",
        "pi_R": "Peso inicial del riesgo (π_R)",
    }
    t0 = time.perf_counter()
    base = run_custom(
        A_BASE,
        B_SEPARABLE,
        PI_BASE,
        n_reps=OAT_REPS,
        n_students=OAT_STUDENTS,
        T=T_WEEKS,
        master_seed=OAT_SEED,
        key="oat",
        name="Base OAT",
        progress=False,
    )
    base_means = {
        "auc": float(base["auc"].mean()),
        "detection_rate_4w": float(base["detection_rate_4w"].mean()),
        "fpr": float(base["fpr"].mean()),
        "prevalence_risk_true": float(base["prevalence_risk_true"].mean()),
    }

    rows = []
    for group, label in groups.items():
        for factor in OAT_FACTORS:
            A2, B2, pi2 = _perturb_group(group, factor, A_BASE, B_SEPARABLE, PI_BASE)
            df = run_custom(
                A2,
                B2,
                pi2,
                n_reps=OAT_REPS,
                n_students=OAT_STUDENTS,
                T=T_WEEKS,
                master_seed=OAT_SEED,
                key="oat",
                name=f"{group} x{factor}",
                progress=False,
            )
            row = {
                "group": group,
                "label": label,
                "factor": factor,
                "n_reps": len(df),
            }
            for metric in ("auc", "detection_rate_4w", "fpr", "prevalence_risk_true"):
                m = float(df[metric].mean())
                row[f"{metric}_mean"] = m
                row[f"{metric}_delta_pct"] = (
                    100.0 * (m - base_means[metric]) / base_means[metric]
                    if base_means[metric] != 0
                    else float("nan")
                )
            rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(path, index=False)
    print(f"[oat] listo en {time.perf_counter() - t0:.1f} s")
    return out


# ----------------------------------------------------------------------
def run_all(results_dir: Path, force: bool = False) -> dict:
    results_dir = Path(results_dir)
    (results_dir / "raw").mkdir(parents=True, exist_ok=True)
    (results_dir / "tables").mkdir(parents=True, exist_ok=True)
    save_parameters(results_dir.parent / "data" / "parameters.json")
    pd.DataFrame(parameter_records()).to_csv(
        results_dir.parent / "data" / "parameters.csv", index=False
    )
    main = run_main(results_dir, force=force)
    est = run_estimation(results_dir, force=force)
    grid = run_sensitivity_grid(results_dir, force=force)
    oat = run_sensitivity_oat(results_dir, force=force)
    examples = make_examples(results_dir)
    manifest = {
        "master_seed": MASTER_SEED,
        "n_reps_main": N_REPS_MAIN,
        "n_students_main": N_STUDENTS_MAIN,
        "T_weeks": T_WEEKS,
        "scenarios": [s.key for s in SCENARIOS],
        "sensitivity": {
            "deltas": SENS_DELTAS,
            "p_stay": SENS_PSTAY,
            "reps": SENS_REPS,
            "students": SENS_STUDENTS,
            "seed": SENS_SEED,
        },
        "oat": {"factors": OAT_FACTORS, "reps": OAT_REPS, "seed": OAT_SEED},
        "n_replications_main": int(len(main)),
        "n_estimation": int(len(est)),
        "n_sensitivity_cells": int(len(grid)),
        "n_oat_rows": int(len(oat)),
        "examples": str(examples.relative_to(results_dir)),
    }
    (results_dir / "raw" / "experiment_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest
