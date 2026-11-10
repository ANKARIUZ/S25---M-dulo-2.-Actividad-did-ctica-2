"""Paquete reproducible para el estudio de un HMM de riesgo académico."""

from .hmm import DiscreteHMM, HMMFitHistory, logsumexp
from .scenarios import (
    A_BASE,
    B_CONFUSABLE,
    B_SEPARABLE,
    PI_BASE,
    SCENARIOS,
    STATES,
    SYMBOLS,
    Scenario,
    emission_matrix,
    get_scenarios,
    transition_with_persistence,
)

__all__ = [
    "DiscreteHMM",
    "HMMFitHistory",
    "logsumexp",
    "Scenario",
    "SCENARIOS",
    "STATES",
    "SYMBOLS",
    "A_BASE",
    "B_SEPARABLE",
    "B_CONFUSABLE",
    "PI_BASE",
    "emission_matrix",
    "transition_with_persistence",
    "get_scenarios",
]

__version__ = "1.0.0"
