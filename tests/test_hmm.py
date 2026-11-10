"""Pruebas unitarias del HMM contra cálculos exhaustivos en modelos pequeños."""

from __future__ import annotations

import itertools
import unittest

import numpy as np

from hmm_riesgo.hmm import DiscreteHMM, logsumexp


def brute_force_loglik(hmm: DiscreteHMM, obs: np.ndarray) -> float:
    T = obs.size
    total = 0.0
    for path in itertools.product(range(hmm.K), repeat=T):
        prob = hmm.pi[path[0]] * hmm.B[path[0], obs[0]]
        for t in range(1, T):
            prob *= hmm.A[path[t - 1], path[t]] * hmm.B[path[t], obs[t]]
        total += prob
    return float(np.log(total))


def brute_force_viterbi(hmm: DiscreteHMM, obs: np.ndarray) -> tuple[float, tuple[int, ...]]:
    best = (-np.inf, None)
    for path in itertools.product(range(hmm.K), repeat=obs.size):
        prob = hmm.pi[path[0]] * hmm.B[path[0], obs[0]]
        for t in range(1, obs.size):
            prob *= hmm.A[path[t - 1], path[t]] * hmm.B[path[t], obs[t]]
        if prob > best[0]:
            best = (float(prob), path)
    return float(np.log(best[0])), best[1]


class TestForwardBackward(unittest.TestCase):
    def setUp(self):
        self.hmm = DiscreteHMM(
            A=[[0.7, 0.3], [0.4, 0.6]],
            B=[[0.9, 0.1], [0.2, 0.8]],
            pi=[0.6, 0.4],
            states=["C", "R"],
            symbols=["alto", "bajo"],
        )
        self.obs = np.array([[0, 1, 0, 0, 1]])

    def test_loglik_matches_bruteforce(self):
        _, ll = self.hmm.forward(self.obs)
        self.assertAlmostEqual(float(ll[0]), brute_force_loglik(self.hmm, self.obs[0]), places=10)

    def test_posterior_sums_to_one(self):
        post = self.hmm.posterior(self.obs)
        np.testing.assert_allclose(post.sum(axis=2), 1.0, atol=1e-12)

    def test_filtered_is_causal(self):
        post_full = self.hmm.posterior(self.obs, kind="filtered")
        post_prefix = self.hmm.posterior(self.obs[:, :3], kind="filtered")
        np.testing.assert_allclose(post_full[:, :3, :], post_prefix, atol=1e-12)

    def test_viterbi_matches_bruteforce(self):
        path, score = self.hmm.viterbi(self.obs)
        best_score, best_path = brute_force_viterbi(self.hmm, self.obs[0])
        self.assertAlmostEqual(float(score[0]), best_score, places=10)
        self.assertEqual(tuple(path[0]), best_path)

    def test_baum_welch_increases_loglik(self):
        rng = np.random.default_rng(7)
        _, obs = self.hmm.sample(T=40, n_sequences=8, rng=rng)
        est = DiscreteHMM(
            A=[[0.6, 0.4], [0.5, 0.5]],
            B=[[0.7, 0.3], [0.3, 0.7]],
            pi=[0.5, 0.5],
        )
        hist = est.baum_welch(obs, n_iter=15, tol=1e-9)
        self.assertGreater(hist.loglik[-1], hist.loglik[0])
        self.assertAlmostEqual(hist.loglik[-1], float(np.sum(est.score(obs))), places=6)

    def test_baum_welch_does_not_decrease_from_truth(self):
        rng = np.random.default_rng(21)
        _, obs = self.hmm.sample(T=30, n_sequences=12, rng=rng)
        est = DiscreteHMM(
            A=self.hmm.A.copy(),
            B=self.hmm.B.copy(),
            pi=self.hmm.pi.copy(),
        )
        hist = est.baum_welch(
            obs,
            n_iter=3,
            tol=1e-12,
            init=(self.hmm.A.copy(), self.hmm.B.copy(), self.hmm.pi.copy()),
        )
        self.assertGreaterEqual(hist.loglik[-1], hist.loglik[0] - 1e-9)

    def test_pi_uses_counts_not_probabilities(self):
        """El pseudo-conteo de pi debe operar sobre conteos, no sobre probabilidades."""
        rng = np.random.default_rng(31)
        _, obs = self.hmm.sample(T=20, n_sequences=500, rng=rng)
        est = DiscreteHMM(
            A=self.hmm.A.copy(),
            B=self.hmm.B.copy(),
            pi=self.hmm.pi.copy(),
        )
        hist = est.baum_welch(
            obs,
            n_iter=2,
            tol=1e-12,
            init=(self.hmm.A.copy(), self.hmm.B.copy(), self.hmm.pi.copy()),
        )
        # Con 500 secuencias, pi estimado debe parecerse a pi verdadero.
        np.testing.assert_allclose(est.pi, self.hmm.pi, atol=0.06)
        self.assertGreater(hist.loglik[-1], hist.loglik[0] - 1e-6)

    def test_simulation_frequencies(self):
        rng = np.random.default_rng(123)
        states, obs = self.hmm.sample(T=400, n_sequences=400, rng=rng)
        freq = np.zeros((2, 2))
        for t in range(1, 400):
            np.add.at(freq, (states[:, t - 1], states[:, t]), 1)
        freq /= freq.sum(axis=1, keepdims=True)
        np.testing.assert_allclose(freq, self.hmm.A, atol=0.04)

    def test_seed_reproducibility(self):
        s1, o1 = self.hmm.sample(T=20, n_sequences=5, rng=np.random.default_rng(99))
        s2, o2 = self.hmm.sample(T=20, n_sequences=5, rng=np.random.default_rng(99))
        np.testing.assert_array_equal(s1, s2)
        np.testing.assert_array_equal(o1, o2)


class TestValidation(unittest.TestCase):
    def test_invalid_rows(self):
        with self.assertRaises(ValueError):
            DiscreteHMM(A=[[0.5, 0.4], [0.2, 0.8]], B=[[0.5, 0.5], [0.5, 0.5]], pi=[0.5, 0.5])

    def test_logsumexp(self):
        x = np.array([[-np.inf, 0.0], [1.0, 2.0]])
        np.testing.assert_allclose(logsumexp(x, axis=1), [0.0, np.log1p(np.exp(1.0)) + 1.0])


if __name__ == "__main__":
    unittest.main()
