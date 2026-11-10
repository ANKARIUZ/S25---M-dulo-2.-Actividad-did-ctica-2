"""
Escenarios de simulación del HMM de riesgo académico.

Estados ocultos (S):
    0 = Comprometido (C)
    1 = En riesgo (R)
    2 = Inactivo / desvinculado (I)

Observaciones (V), nivel semanal de actividad en el LMS:
    0 = Alta, 1 = Media, 2 = Baja

Los escenarios A-D modifican un componente distinto del modelo para aislar
su efecto: emisiones (B), transiciones (A) y distribución inicial (pi).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np

STATES = ["Comprometido", "En riesgo", "Inactivo"]
SYMBOLS = ["Alta", "Media", "Baja"]
STATE_SHORT = ["C", "R", "I"]
RISK_STATE = 1

# Matriz base: persistencia moderada y recuperación posible desde el riesgo.
A_BASE = np.array(
    [
        [0.82, 0.15, 0.03],
        [0.22, 0.63, 0.15],
        [0.04, 0.11, 0.85],
    ]
)
PI_BASE = np.array([0.70, 0.20, 0.10])

# Emisión "separable": la actividad distingue razonablemente los estados.
# El estado de riesgo se caracteriza por una mezcla de actividad media y baja,
# mientras que la inactividad se concentra en actividad baja.
B_SEPARABLE = np.array(
    [
        [0.80, 0.17, 0.03],
        [0.10, 0.50, 0.40],
        [0.02, 0.10, 0.88],
    ]
)

# Emisión "confusa": las tres distribuciones son parecidas (peor señal).
B_CONFUSABLE = np.array(
    [
        [0.40, 0.35, 0.25],
        [0.35, 0.35, 0.30],
        [0.30, 0.35, 0.35],
    ]
)

# Escenario de intervención: mayor probabilidad de retorno R -> C.
A_INTERVENCION = np.array(
    [
        [0.86, 0.11, 0.03],
        [0.40, 0.50, 0.10],
        [0.08, 0.17, 0.75],
    ]
)

PI_RIESGO_ALTO = np.array([0.45, 0.40, 0.15])


def emission_matrix(separability: float) -> np.ndarray:
    """Interpola entre la emisión confusa (0) y la separable (1).

    La combinación convexa conserva filas estocásticas, de modo que
    ``separability`` es un parámetro continuo de identificabilidad.
    """
    if not 0.0 <= separability <= 1.0:
        raise ValueError("separability debe estar en [0, 1]")
    return (1.0 - separability) * B_CONFUSABLE + separability * B_SEPARABLE


def transition_with_persistence(p_stay_risk: float) -> np.ndarray:
    """Matriz base con la persistencia del estado de riesgo modificada.

    Las probabilidades de salida de R se reescalan para que su suma sea
    ``1 - p_stay_risk``, preservando la proporción relativa original.
    """
    if not 0.0 < p_stay_risk < 1.0:
        raise ValueError("p_stay_risk debe estar en (0, 1)")
    A = A_BASE.copy()
    exits = A[RISK_STATE].copy()
    exits[RISK_STATE] = 0.0
    exits = exits / exits.sum()
    A[RISK_STATE] = exits * (1.0 - p_stay_risk)
    A[RISK_STATE, RISK_STATE] = p_stay_risk
    return A


@dataclass(frozen=True)
class Scenario:
    """Especificación completa de un escenario."""

    key: str
    name: str
    description: str
    A: np.ndarray
    B: np.ndarray
    pi: np.ndarray
    color: str
    changes: str = ""
    metadata: dict = field(default_factory=dict)

    def model_kwargs(self) -> dict:
        return {
            "A": self.A,
            "B": self.B,
            "pi": self.pi,
            "states": STATES,
            "symbols": SYMBOLS,
        }

    def to_record(self) -> dict:
        return {
            "scenario": self.key,
            "name": self.name,
            "description": self.description,
            "changes": self.changes,
            "A": self.A.tolist(),
            "B": self.B.tolist(),
            "pi": self.pi.tolist(),
        }


SCENARIOS: list[Scenario] = [
    Scenario(
        key="A",
        name="Base",
        description=(
            "Cohorte de referencia con persistencia moderada del riesgo y "
            "emisiones separables."
        ),
        A=A_BASE.copy(),
        B=B_SEPARABLE.copy(),
        pi=PI_BASE.copy(),
        color="#1f4e79",
        changes="Referencia",
    ),
    Scenario(
        key="B",
        name="Señal débil",
        description=(
            "Misma dinámica que A, pero con emisiones más confundibles: la "
            "actividad observada discrimina peor los estados ocultos."
        ),
        A=A_BASE.copy(),
        B=emission_matrix(0.65),
        pi=PI_BASE.copy(),
        color="#c55a11",
        changes="B (separabilidad 0.65)",
    ),
    Scenario(
        key="C",
        name="Intervención temprana",
        description=(
            "Mayor probabilidad de recuperación de R a C y menor tránsito "
            "directo de R a I, como efecto de un programa de acompañamiento."
        ),
        A=A_INTERVENCION.copy(),
        B=B_SEPARABLE.copy(),
        pi=PI_BASE.copy(),
        color="#2e7d32",
        changes="A (recuperación R→C = 0.40)",
    ),
    Scenario(
        key="D",
        name="Riesgo inicial alto",
        description=(
            "Cohorte que inicia el semestre con mayor proporción de estudiantes "
            "en riesgo; la dinámica y las emisiones son las de A."
        ),
        A=A_BASE.copy(),
        B=B_SEPARABLE.copy(),
        pi=PI_RIESGO_ALTO.copy(),
        color="#7b1fa2",
        changes="π (riesgo inicial 0.40)",
    ),
]

SCENARIO_BY_KEY = {s.key: s for s in SCENARIOS}


def get_scenarios(keys: Sequence[str] | None = None) -> list[Scenario]:
    if keys is None:
        return list(SCENARIOS)
    missing = set(keys) - set(SCENARIO_BY_KEY)
    if missing:
        raise KeyError(f"Escenarios desconocidos: {sorted(missing)}")
    return [SCENARIO_BY_KEY[k] for k in keys]


def parameter_records() -> list[dict]:
    """Tabla larga de parámetros para auditoría y anexos."""
    rows: list[dict] = []
    for sc in SCENARIOS:
        for i, origin in enumerate(STATES):
            for j, dest in enumerate(STATES):
                rows.append(
                    {
                        "scenario": sc.key,
                        "matrix": "A",
                        "origin": origin,
                        "destination": dest,
                        "value": float(sc.A[i, j]),
                    }
                )
        for j, state in enumerate(STATES):
            for k, symbol in enumerate(SYMBOLS):
                rows.append(
                    {
                        "scenario": sc.key,
                        "matrix": "B",
                        "origin": state,
                        "destination": symbol,
                        "value": float(sc.B[j, k]),
                    }
                )
        for j, state in enumerate(STATES):
            rows.append(
                {
                    "scenario": sc.key,
                    "matrix": "pi",
                    "origin": "inicio",
                    "destination": state,
                    "value": float(sc.pi[j]),
                }
            )
    return rows


def save_parameters(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "states": STATES,
        "symbols": SYMBOLS,
        "risk_state": RISK_STATE,
        "scenarios": [s.to_record() for s in SCENARIOS],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":  # pragma: no cover
    for sc in SCENARIOS:
        print(sc.key, sc.name)
        print("A=\n", np.round(sc.A, 4))
        print("B=\n", np.round(sc.B, 4))
        print("pi=", np.round(sc.pi, 4))
        print()
