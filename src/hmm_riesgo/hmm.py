"""
Implementación desde cero de un Modelo Oculto de Markov (HMM) discreto.

El módulo evita dependencias de terceros distintas de NumPy para que el
experimento sea reproducible y auditable. Incluye los tres problemas clásicos:

1. Evaluación   -> algoritmo Forward (y Forward-Backward para posteriores).
2. Decodificación -> Viterbi y posteriores filtradas/suavizadas.
3. Aprendizaje  -> Baum-Welch (EM) con suavizado de Dirichlet.

Convenciones
------------
- ``K`` estados ocultos, ``M`` símbolos observables.
- ``A`` matriz de transición ``(K, K)``, filas estocásticas.
- ``B`` matriz de emisión ``(K, M)``, filas estocásticas.
- ``pi`` distribución inicial ``(K,)``.
- ``obs`` arreglo entero ``(N, T)`` con N secuencias de igual longitud T.

Todas las operaciones se vectorizan sobre las N secuencias para que las
simulaciones Monte Carlo sean viables en un computador personal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


def logsumexp(x: np.ndarray, axis=None, keepdims: bool = False) -> np.ndarray:
    """log(sum(exp(x))) numéricamente estable, tolerante a -inf."""
    x = np.asarray(x, dtype=float)
    xmax = np.max(x, axis=axis, keepdims=True)
    xmax = np.where(np.isfinite(xmax), xmax, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.log(np.sum(np.exp(x - xmax), axis=axis, keepdims=True)) + xmax
    if not keepdims:
        out = np.squeeze(out, axis=axis)
    return out


def _as_2d_obs(obs: np.ndarray) -> np.ndarray:
    obs = np.asarray(obs)
    if obs.ndim == 1:
        obs = obs[None, :]
    if obs.ndim != 2:
        raise ValueError("obs debe tener forma (T,) o (N, T)")
    if not np.issubdtype(obs.dtype, np.integer):
        if not np.allclose(obs, np.round(obs)):
            raise ValueError("obs debe contener índices enteros")
        obs = obs.astype(int)
    if np.any(obs < 0):
        raise ValueError("obs no puede contener índices negativos")
    return obs


def _draw_categorical(probs: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Muestrea una categoría por fila de ``probs`` (n, K)."""
    n = probs.shape[0]
    cdf = np.cumsum(probs, axis=1)
    u = rng.random((n, 1))
    idx = np.sum(u > cdf, axis=1)
    return np.minimum(idx, probs.shape[1] - 1).astype(int)


@dataclass
class HMMFitHistory:
    """Historial de una estimación Baum-Welch."""

    loglik: list[float]
    iterations: int
    converged: bool
    parameter_delta: list[float]


class DiscreteHMM:
    """HMM con emisiones categóricas y API vectorizada.

    Parámetros
    ----------
    A, B, pi:
        Matrices del modelo. Se valida que sean estocásticas por filas.
    states, symbols:
        Etiquetas legibles (opcionales) para reportes.
    pseudocount:
        Pseudo-conteo Dirichlet usado en Baum-Welch (0.5 = Jeffreys).
    """

    def __init__(
        self,
        A: Sequence[Sequence[float]],
        B: Sequence[Sequence[float]],
        pi: Sequence[float],
        states: Sequence[str] | None = None,
        symbols: Sequence[str] | None = None,
        pseudocount: float = 0.5,
    ) -> None:
        self.A = np.asarray(A, dtype=float)
        self.B = np.asarray(B, dtype=float)
        self.pi = np.asarray(pi, dtype=float).ravel()
        self.pseudocount = float(pseudocount)

        if self.A.ndim != 2 or self.A.shape[0] != self.A.shape[1]:
            raise ValueError("A debe ser cuadrada (K, K)")
        self.K = self.A.shape[0]
        if self.B.ndim != 2 or self.B.shape[0] != self.K:
            raise ValueError("B debe tener forma (K, M)")
        self.M = self.B.shape[1]
        if self.pi.shape != (self.K,):
            raise ValueError("pi debe tener forma (K,)")

        for name, arr in (("A", self.A), ("B", self.B)):
            if np.any(arr < 0):
                raise ValueError(f"{name} no puede tener entradas negativas")
            if not np.allclose(arr.sum(axis=1), 1.0, atol=1e-8):
                raise ValueError(f"las filas de {name} deben sumar 1")
        if np.any(self.pi < 0) or not np.isclose(self.pi.sum(), 1.0, atol=1e-8):
            raise ValueError("pi debe ser no negativa y sumar 1")

        self.states = list(states) if states is not None else [f"S{i}" for i in range(self.K)]
        self.symbols = list(symbols) if symbols is not None else [f"o{i}" for i in range(self.M)]
        if len(self.states) != self.K:
            raise ValueError("states debe tener K etiquetas")
        if len(self.symbols) != self.M:
            raise ValueError("symbols debe tener M etiquetas")

        with np.errstate(divide="ignore"):
            self._logA = np.log(self.A)
            self._logB = np.log(self.B)
            self._logpi = np.log(self.pi)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def copy(self) -> "DiscreteHMM":
        return DiscreteHMM(
            self.A.copy(),
            self.B.copy(),
            self.pi.copy(),
            states=self.states,
            symbols=self.symbols,
            pseudocount=self.pseudocount,
        )

    def _emission_loglik(self, obs: np.ndarray) -> np.ndarray:
        """log B[j, o_t] con forma (N, T, K)."""
        if np.any(obs >= self.M):
            raise ValueError("obs contiene un símbolo fuera de rango")
        return np.transpose(self._logB[:, obs], (1, 2, 0))

    def stationary_distribution(self) -> np.ndarray:
        """Distribución estacionaria de la cadena (autovector izquierdo)."""
        vals, vecs = np.linalg.eig(self.A.T)
        idx = int(np.argmin(np.abs(vals - 1.0)))
        vec = np.abs(np.real(vecs[:, idx]))
        return vec / vec.sum()

    def expected_dwell_times(self) -> np.ndarray:
        """Duración media (en semanas) de cada visita a un estado.

        Para una cadena de Markov homogénea, el tiempo de permanencia sigue
        una distribución geométrica con media 1 / (1 - a_jj).
        """
        diag = np.diag(self.A)
        with np.errstate(divide="ignore"):
            return np.where(diag < 1.0, 1.0 / (1.0 - diag), np.inf)

    # ------------------------------------------------------------------
    # Simulación
    # ------------------------------------------------------------------
    def sample(
        self,
        T: int,
        n_sequences: int = 1,
        rng: np.random.Generator | None = None,
        initial_states: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Genera trayectorias latentes y observaciones.

        Retorna ``states`` y ``obs`` de forma ``(N, T)``.
        """
        if T < 1 or n_sequences < 1:
            raise ValueError("T y n_sequences deben ser positivos")
        rng = np.random.default_rng() if rng is None else rng
        n = int(n_sequences)

        states = np.empty((n, T), dtype=int)
        obs = np.empty((n, T), dtype=int)

        if initial_states is None:
            states[:, 0] = rng.choice(self.K, size=n, p=self.pi)
        else:
            init = np.asarray(initial_states, dtype=int).ravel()
            if init.shape != (n,):
                raise ValueError("initial_states debe tener n elementos")
            states[:, 0] = init

        obs[:, 0] = _draw_categorical(self.B[states[:, 0]], rng)
        for t in range(1, T):
            states[:, t] = _draw_categorical(self.A[states[:, t - 1]], rng)
            obs[:, t] = _draw_categorical(self.B[states[:, t]], rng)
        return states, obs

    # ------------------------------------------------------------------
    # Forward / Backward
    # ------------------------------------------------------------------
    def forward(self, obs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """log alpha_t(j) = log P(o_1..o_t, S_t=j | lambda) y log-likelihood."""
        obs = _as_2d_obs(obs)
        n, T = obs.shape
        logB = self._emission_loglik(obs)
        log_alpha = np.empty((n, T, self.K), dtype=float)
        log_alpha[:, 0, :] = self._logpi[None, :] + logB[:, 0, :]
        for t in range(1, T):
            log_alpha[:, t, :] = (
                logsumexp(log_alpha[:, t - 1, :, None] + self._logA[None, :, :], axis=1)
                + logB[:, t, :]
            )
        loglik = logsumexp(log_alpha[:, -1, :], axis=1)
        return log_alpha, loglik

    def backward(self, obs: np.ndarray) -> np.ndarray:
        """log beta_t(j) = log P(o_{t+1}..o_T | S_t=j, lambda)."""
        obs = _as_2d_obs(obs)
        n, T = obs.shape
        logB = self._emission_loglik(obs)
        log_beta = np.empty((n, T, self.K), dtype=float)
        log_beta[:, -1, :] = 0.0
        for t in range(T - 2, -1, -1):
            log_beta[:, t, :] = logsumexp(
                self._logA[None, :, :]
                + logB[:, t + 1, None, :]
                + log_beta[:, t + 1, None, :],
                axis=2,
            )
        return log_beta

    def posterior(self, obs: np.ndarray, kind: str = "smoothed") -> np.ndarray:
        """Probabilidades de estado.

        kind='smoothed' usa toda la secuencia (forward-backward);
        kind='filtered' usa solo o_1..o_t (apto para alertas en línea).
        """
        obs = _as_2d_obs(obs)
        log_alpha, loglik = self.forward(obs)
        if kind == "filtered":
            log_post = log_alpha - logsumexp(log_alpha, axis=2, keepdims=True)
        elif kind == "smoothed":
            log_beta = self.backward(obs)
            log_post = log_alpha + log_beta - loglik[:, None, None]
        else:
            raise ValueError("kind debe ser 'filtered' o 'smoothed'")
        post = np.exp(log_post)
        post /= post.sum(axis=2, keepdims=True)
        return post

    def viterbi(self, obs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Ruta más probable y su log-probabilidad conjunta."""
        obs = _as_2d_obs(obs)
        n, T = obs.shape
        logB = self._emission_loglik(obs)
        delta = np.empty((n, T, self.K), dtype=float)
        psi = np.zeros((n, T, self.K), dtype=int)
        delta[:, 0, :] = self._logpi[None, :] + logB[:, 0, :]
        for t in range(1, T):
            scores = delta[:, t - 1, :, None] + self._logA[None, :, :]
            psi[:, t, :] = np.argmax(scores, axis=1)
            delta[:, t, :] = np.max(scores, axis=1) + logB[:, t, :]
        path = np.empty((n, T), dtype=int)
        path[:, -1] = np.argmax(delta[:, -1, :], axis=1)
        for t in range(T - 2, -1, -1):
            path[:, t] = np.take_along_axis(
                psi[:, t + 1, :], path[:, t + 1, None], axis=1
            )[:, 0]
        score = np.max(delta[:, -1, :], axis=1)
        return path, score

    # ------------------------------------------------------------------
    # Baum-Welch
    # ------------------------------------------------------------------
    def baum_welch(
        self,
        obs: np.ndarray,
        n_iter: int = 100,
        tol: float = 1e-6,
        pseudocount: float | None = None,
        init: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
        verbose: bool = False,
    ) -> HMMFitHistory:
        """Estima A, B y pi por máxima verosimilitud (EM).

        El suavizado Dirichlet evita probabilidades nulas y estabiliza la
        estimación en secuencias cortas. ``init`` permite reinicios
        deterministas para estudiar la recuperación de parámetros.
        """
        obs = _as_2d_obs(obs)
        if np.any(obs >= self.M):
            raise ValueError("obs contiene un símbolo fuera de rango")
        if init is not None:
            A0, B0, pi0 = (np.asarray(x, dtype=float) for x in init)
            if A0.shape != (self.K, self.K) or B0.shape != (self.K, self.M):
                raise ValueError("init contiene matrices con dimensiones incompatibles")
            if pi0.shape != (self.K,):
                raise ValueError("init[2] debe tener forma (K,)")
            if (
                np.any(A0 < 0)
                or np.any(B0 < 0)
                or np.any(pi0 < 0)
                or not np.allclose(A0.sum(axis=1), 1.0, atol=1e-8)
                or not np.allclose(B0.sum(axis=1), 1.0, atol=1e-8)
                or not np.isclose(pi0.sum(), 1.0, atol=1e-8)
            ):
                raise ValueError("init debe contener matrices estocásticas válidas")
            self.A, self.B, self.pi = A0.copy(), B0.copy(), pi0.copy()
            with np.errstate(divide="ignore"):
                self._logA = np.log(self.A)
                self._logB = np.log(self.B)
                self._logpi = np.log(self.pi)

        pc = self.pseudocount if pseudocount is None else float(pseudocount)
        n, T = obs.shape
        history: list[float] = []
        deltas: list[float] = []
        converged = False

        _, ll = self.forward(obs)
        ll = float(np.sum(ll))
        history.append(ll)

        for it in range(1, n_iter + 1):
            log_alpha, loglik = self.forward(obs)
            log_beta = self.backward(obs)
            log_gamma = log_alpha + log_beta - loglik[:, None, None]
            gamma = np.exp(log_gamma)
            logB = self._emission_loglik(obs)

            # xi acumulado sobre secuencias: (K, K)
            xi_sum = np.zeros((self.K, self.K), dtype=float)
            for t in range(T - 1):
                log_xi = (
                    log_alpha[:, t, :, None]
                    + self._logA[None, :, :]
                    + logB[:, t + 1, None, :]
                    + log_beta[:, t + 1, None, :]
                    - loglik[:, None, None]
                )
                xi_sum += np.exp(logsumexp(log_xi, axis=0))

            gamma_sum = gamma.sum(axis=0)  # (T, K)

            A_new = xi_sum + pc
            A_new /= A_new.sum(axis=1, keepdims=True)

            B_new = np.empty((self.K, self.M), dtype=float)
            for k in range(self.M):
                B_new[:, k] = gamma[obs == k].sum(axis=0)
            B_new += pc
            B_new /= B_new.sum(axis=1, keepdims=True)

            pi_new = gamma[:, 0, :].sum(axis=0) + pc
            pi_new /= pi_new.sum()

            delta = max(
                float(np.max(np.abs(A_new - self.A))),
                float(np.max(np.abs(B_new - self.B))),
                float(np.max(np.abs(pi_new - self.pi))),
            )
            deltas.append(delta)

            self.A, self.B, self.pi = A_new, B_new, pi_new
            with np.errstate(divide="ignore"):
                self._logA = np.log(self.A)
                self._logB = np.log(self.B)
                self._logpi = np.log(self.pi)

            new_ll = float(np.sum(self.forward(obs)[1]))
            history.append(new_ll)
            if verbose and (it == 1 or it % 10 == 0):
                print(f"  iter {it:3d}  loglik={new_ll:.4f}  delta={delta:.2e}")
            if abs(new_ll - ll) <= tol * max(1.0, abs(ll)):
                converged = True
                ll = new_ll
                break
            ll = new_ll

        return HMMFitHistory(
            loglik=history,
            iterations=len(history) - 1,
            converged=converged,
            parameter_delta=deltas,
        )

    # ------------------------------------------------------------------
    def score(self, obs: np.ndarray) -> np.ndarray:
        """Log-verosimilitud de cada secuencia."""
        return self.forward(obs)[1]

    def __repr__(self) -> str:  # pragma: no cover - cosmético
        return (
            f"DiscreteHMM(K={self.K}, M={self.M}, "
            f"states={self.states}, symbols={self.symbols})"
        )
