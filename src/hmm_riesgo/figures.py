"""
Figuras del artículo, con estilo consistente y salida a 300 dpi (PNG y PDF).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, Patch, Rectangle

from .scenarios import SCENARIOS

SCENARIO_COLORS = {s.key: s.color for s in SCENARIOS}
SCENARIO_NAMES = {s.key: f"{s.key}. {s.name}" for s in SCENARIOS}
STATE_COLORS = {"C": "#2e7d32", "R": "#e07b00", "I": "#7b1fa2"}
STATE_NAMES = {"C": "Comprometido", "R": "En riesgo", "I": "Inactivo"}


def setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linewidth": 0.5,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
        }
    )


def _save(fig: plt.Figure, results_dir: Path, name: str) -> None:
    fig_dir = results_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_dir / f"{name}.png", dpi=300, facecolor="white")
    fig.savefig(fig_dir / f"{name}.pdf", facecolor="white")
    plt.close(fig)
    print(f"[fig] {fig_dir / (name + '.png')}")


# ----------------------------------------------------------------------
# Figura 1: diagrama del modelo
# ----------------------------------------------------------------------
def fig_model_diagram(results_dir: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.set_xlim(-1.7, 5.9)
    ax.set_ylim(-2.65, 1.55)
    ax.set_aspect("equal")
    ax.axis("off")

    pos = {"C": (0.0, 0.0), "R": (2.3, 0.0), "I": (4.6, 0.0)}
    radius = 0.62
    for key, (x, y) in pos.items():
        ax.add_patch(
            Circle((x, y), radius, facecolor=SCENARIO_COLORS["A"], alpha=0.12,
                   edgecolor=STATE_COLORS[key], linewidth=1.8, zorder=2)
        )
        ax.add_patch(
            Circle((x, y), radius, facecolor="none",
                   edgecolor=STATE_COLORS[key], linewidth=1.8, zorder=3)
        )
        ax.text(x, y, key, ha="center", va="center", fontsize=15,
                fontweight="bold", color=STATE_COLORS[key], zorder=4)

    def loop(x: float, y: float, color: str, label: str) -> None:
        ax.add_patch(
            FancyArrowPatch(
                (x - 0.10, y + 0.60),
                (x + 0.10, y + 0.60),
                connectionstyle="arc3,rad=-2.6",
                arrowstyle="-|>",
                mutation_scale=8,
                linewidth=1.1,
                color=color,
                zorder=3,
            )
        )
        ax.text(x, y + 1.18, label, ha="center", va="bottom", fontsize=7.5,
                color=color)

    loop(*pos["C"], STATE_COLORS["C"], "$a_{CC}$")
    loop(*pos["R"], STATE_COLORS["R"], "$a_{RR}$")
    loop(*pos["I"], STATE_COLORS["I"], "$a_{II}$")

    def arrow(start, end, rad, color, label, label_xy, style="-|>", ls="-"):
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle=style,
                mutation_scale=9,
                linewidth=1.2,
                linestyle=ls,
                color=color,
                zorder=2,
            )
        )
        ax.text(label_xy[0], label_xy[1], label, fontsize=7.4, ha="center",
                va="center", color=color)

    arrow((0.52, 0.10), (1.78, 0.10), -0.25, "#333333", "$a_{CR}$", (1.15, 0.34))
    arrow((1.78, -0.10), (0.52, -0.10), -0.25, "#333333", "$a_{RC}$", (1.15, -0.34))
    arrow((2.82, 0.10), (4.08, 0.10), -0.25, "#333333", "$a_{RI}$", (3.45, 0.34))
    arrow((4.08, -0.10), (2.82, -0.10), -0.25, "#333333", "$a_{IR}$", (3.45, -0.34))
    arrow((0.30, -0.48), (4.30, -0.48), 0.35, "#777777", "$a_{CI}$", (1.35, -0.72),
          ls="--")

    obs_y = -1.95
    ax.add_patch(
        Rectangle((0.65, obs_y - 0.28), 3.30, 0.56, facecolor="#f2f2f2",
                  edgecolor="#555555", linewidth=1.0, zorder=2)
    )
    ax.text(
        2.30,
        obs_y,
        r"$O_t \in \{\mathrm{Alta},\ \mathrm{Media},\ \mathrm{Baja}\}$",
        ha="center",
        va="center",
        fontsize=8.2,
        zorder=4,
    )
    for key, (x, y) in pos.items():
        target_x = {"C": 1.15, "R": 2.30, "I": 3.45}[key]
        ax.add_patch(
            FancyArrowPatch(
                (x, y - 0.58),
                (target_x, obs_y + 0.30),
                connectionstyle="arc3,rad=0.08",
                arrowstyle="-|>",
                mutation_scale=7,
                linewidth=0.9,
                linestyle=(0, (3, 2)),
                color=STATE_COLORS[key],
                alpha=0.8,
                zorder=1,
            )
        )
        ax.text((x + target_x) / 2 + 0.05, (y + obs_y) / 2 + 0.10,
                f"$b_{{{key}}}(o_t)$", fontsize=7.0, color=STATE_COLORS[key],
                ha="center")

    ax.text(2.30, 1.43, "Estados ocultos $S=\\{C,R,I\\}$", ha="center",
            fontsize=9, fontweight="bold")
    ax.text(2.30, -2.48, "Observaciones $V=\\{$Alta, Media, Baja$\\}$", ha="center",
            fontsize=9, fontweight="bold")
    ax.text(-1.60, 1.36, r"$\pi=(\pi_C,\pi_R,\pi_I)$", ha="left", va="center",
            fontsize=8.2, color="#444444")
    _save(fig, results_dir, "fig01_diagrama_hmm")


# ----------------------------------------------------------------------
# Figura 2: trayectorias individuales
# ----------------------------------------------------------------------
def fig_examples(results_dir: Path) -> None:
    setup_style()
    data = np.load(results_dir / "raw" / "example_trajectories.npz")
    fig, axes = plt.subplots(2, 1, figsize=(6.6, 4.9), sharex=True)
    titles = {
        "A": "(a) Escenario A: detección oportuna",
        "B": "(b) Escenario B: sin detección en 16 semanas",
    }
    for ax, key in zip(axes, ["A", "B"]):
        states = data[f"{key}_states"]
        risk = data[f"{key}_risk"]
        seed, student, onset, alarm, detected, pre_alarm, pre_week = data[f"{key}_meta"]
        weeks = np.arange(1, len(states) + 1)

        for t, s in enumerate(states):
            state_key = "CRI"[int(s)]
            ax.add_patch(
                Rectangle((weeks[t] - 0.5, 1.03), 1.0, 0.13,
                          facecolor=STATE_COLORS[state_key], edgecolor="white",
                          linewidth=0.3, clip_on=False)
            )
        ax.plot(weeks, risk, color=SCENARIO_COLORS[key], lw=1.8, marker="o",
                ms=3.2)
        ax.axhline(0.5, color="#555555", ls="--", lw=1.0)
        ax.axvline(onset + 1, color=STATE_COLORS["R"], ls=":", lw=1.1)
        ax.text(onset + 1.05, 0.04, "inicio R", fontsize=7,
                color=STATE_COLORS["R"], rotation=90, va="bottom")
        if detected:
            ax.plot(alarm + 1, risk[alarm], marker="v", ms=8, color="black",
                    zorder=5)
            ax.annotate(
                "detección",
                xy=(alarm + 1, risk[alarm]),
                xytext=(alarm + 1 + 0.4, min(0.97, risk[alarm] + 0.16)),
                fontsize=7,
                arrowprops=dict(arrowstyle="->", lw=0.8, color="black"),
            )
        elif pre_alarm and pre_week >= 0:
            ax.plot(pre_week + 1, risk[pre_week], marker="v", ms=7,
                    markerfacecolor="white", markeredgecolor="#b00020",
                    markeredgewidth=1.2, zorder=5)
            ax.annotate(
                "falsa alarma",
                xy=(pre_week + 1, risk[pre_week]),
                xytext=(pre_week + 1 + 0.55, min(0.80, risk[pre_week] + 0.18)),
                fontsize=7,
                color="#b00020",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#b00020"),
            )
        else:
            ax.text(12.0, 0.80, "sin alarma", fontsize=7, color="#666666")
        ax.set_ylim(0, 1.22)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_ylabel("Probabilidad filtrada de R")
        ax.set_title(titles[key], loc="left", fontsize=9.2)
    handles = [
        Line2D([0], [0], color=SCENARIO_COLORS["A"], lw=1.8,
               label="$P(S_t=R\\mid o_{1:t})$"),
        Line2D([0], [0], color="#555555", ls="--", lw=1.0,
               label="umbral $\\tau=0.5$"),
        Patch(color=STATE_COLORS["C"], label="C: comprometido"),
        Patch(color=STATE_COLORS["R"], label="R: en riesgo"),
        Patch(color=STATE_COLORS["I"], label="I: inactivo"),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=5,
        frameon=False,
        fontsize=7,
        bbox_to_anchor=(0.5, -0.01),
    )
    axes[-1].set_xlabel("Semana del semestre")
    axes[-1].set_xticks(range(1, 17))
    fig.align_ylabels(axes)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    _save(fig, results_dir, "fig02_trayectorias")


# ----------------------------------------------------------------------
# Figura 3: métricas principales por escenario
# ----------------------------------------------------------------------
def fig_main_metrics(results_dir: Path) -> None:
    setup_style()
    desc = pd.read_csv(results_dir / "tables" / "main_descriptives.csv")
    raw = pd.read_csv(results_dir / "raw" / "main_replications.csv")
    metrics = [
        ("detection_rate_4w", "Detección a 4 semanas", "Detección a 4 semanas", (0.0, 0.62)),
        ("auc", "AUC", "AUC", (0.68, 0.88)),
        ("fpr", "Tasa semanal de FP", "Falsos positivos", (0.0, 0.18)),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 3.05))
    rng = np.random.default_rng(7)
    for idx, (ax, (metric, ylabel, title, ylim)) in enumerate(zip(axes, metrics)):
        for i, key in enumerate(["A", "B", "C", "D"]):
            vals = raw.loc[raw.scenario == key, metric].to_numpy()
            jitter = rng.normal(0, 0.055, size=vals.size)
            ax.scatter(
                np.full(vals.size, i) + jitter,
                vals,
                s=7,
                alpha=0.18,
                color=SCENARIO_COLORS[key],
                edgecolors="none",
                zorder=1,
            )
            row = desc[(desc.scenario == key) & (desc.metric == metric)].iloc[0]
            ax.errorbar(
                i,
                row["mean"],
                yerr=[[row["mean"] - row["ci_low"]], [row["ci_high"] - row["mean"]]],
                fmt="o",
                color="black",
                ms=4,
                capsize=3,
                lw=1.1,
                zorder=4,
            )
            offset = 0.035 if metric == "detection_rate_4w" else (0.009 if metric == "auc" else 0.006)
            ax.text(i, row["mean"] + offset, f"{row['mean']:.3f}", ha="center",
                    va="bottom", fontsize=7.2, fontweight="bold")
        ax.set_xticks(range(4))
        ax.set_xticklabels(list("ABCD"), fontsize=8)
        ax.set_ylim(*ylim)
        ax.set_ylabel(ylabel)
        ax.set_title(f"({chr(97 + idx)}) {title}", loc="left", fontsize=8.8)
    fig.legend(
        handles=[Patch(color=SCENARIO_COLORS[k], label=SCENARIO_NAMES[k]) for k in "ABCD"],
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=6.8,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.tight_layout(rect=(0, 0.10, 1, 1), w_pad=1.2)
    _save(fig, results_dir, "fig03_metricas_escenarios")


# ----------------------------------------------------------------------
# Figura 4: curvas ROC
# ----------------------------------------------------------------------
def fig_roc(results_dir: Path) -> None:
    setup_style()
    roc = pd.read_csv(results_dir / "raw" / "roc_curves.csv")
    desc = pd.read_csv(results_dir / "tables" / "main_descriptives.csv")
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    for key in ["A", "B", "C", "D"]:
        sub = roc[roc.scenario == key]
        pivot = sub.pivot(index="fpr", columns="replication", values="tpr").sort_index()
        arr = np.maximum.accumulate(pivot.to_numpy(), axis=0)
        x = pivot.index.to_numpy()
        mean = arr.mean(axis=1)
        lo = np.percentile(arr, 2.5, axis=1)
        hi = np.percentile(arr, 97.5, axis=1)
        auc_row = desc[(desc.scenario == key) & (desc.metric == "auc")].iloc[0]
        ax.plot(x, mean, color=SCENARIO_COLORS[key], lw=1.8,
                label=f"{SCENARIO_NAMES[key]} (AUC={auc_row['mean']:.3f})")
        ax.fill_between(x, lo, hi, color=SCENARIO_COLORS[key], alpha=0.10,
                        linewidth=0)
    ax.plot([0, 1], [0, 1], color="#999999", ls=":", lw=1.0, label="Azar")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Tasa de falsos positivos (1 - especificidad)")
    ax.set_ylabel("Sensibilidad (recall)")
    ax.legend(loc="lower right", frameon=False, fontsize=7.3)
    ax.set_aspect("equal")
    fig.tight_layout()
    _save(fig, results_dir, "fig04_roc")


# ----------------------------------------------------------------------
# Figura 5: mapas de calor de sensibilidad
# ----------------------------------------------------------------------
def fig_sensitivity(results_dir: Path) -> None:
    setup_style()
    grid = pd.read_csv(results_dir / "tables" / "sensitivity_grid.csv")
    specs = [
        ("auc_mean", "AUC", "viridis", None),
        ("det4_mean", "Detección a 4 semanas", "viridis", (0, 0.85)),
        ("fpr_mean", "Falsos positivos semanales", "magma", (0, 0.5)),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.8))
    for ax, (metric, title, cmap, lim) in zip(axes, specs):
        pivot = grid.pivot(index="p_stay_risk", columns="delta", values=metric)
        pivot = pivot.sort_index(ascending=True)
        data = pivot.to_numpy()
        vmin, vmax = (lim if lim is not None else (np.nanmin(data), np.nanmax(data)))
        im = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap,
                       vmin=vmin, vmax=vmax)
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels([f"{x:.1f}" for x in pivot.columns], fontsize=7.2)
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels([f"{y:.2f}" for y in pivot.index], fontsize=7.2)
        ax.set_xlabel("Separabilidad de emisiones $\\delta$")
        if ax is axes[0]:
            ax.set_ylabel("Persistencia del riesgo $a_{RR}$")
        ax.set_title(title, loc="left", fontsize=8.8)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                val = data[i, j]
                color = "white" if (val - vmin) / max(vmax - vmin, 1e-9) < 0.55 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=6.9, color=color)
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.ax.tick_params(labelsize=6.5)
        cb.set_label(title, fontsize=7)
    fig.tight_layout(w_pad=1.4)
    _save(fig, results_dir, "fig05_sensibilidad")


# ----------------------------------------------------------------------
# Figura 6: tornado one-at-a-time
# ----------------------------------------------------------------------
def fig_oat(results_dir: Path) -> None:
    setup_style()
    oat = pd.read_csv(results_dir / "tables" / "sensitivity_oat.csv")
    labels = {
        "A_C": "Persistencia de C ($A$)",
        "A_R": "Persistencia de R ($A$)",
        "A_I": "Persistencia de I ($A$)",
        "B_C": "Emisión alta de C ($B$)",
        "B_R": "Emisión media de R ($B$)",
        "B_I": "Emisión baja de I ($B$)",
        "pi_R": "Peso inicial de R ($\\pi$)",
    }
    specs = [
        ("detection_rate_4w_delta_pct", "Detección a 4 semanas"),
        ("auc_delta_pct", "AUC"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.5), sharey=True)
    for ax, (metric, title) in zip(axes, specs):
        rows = []
        for group in labels:
            sub = oat[oat.group == group]
            lo = float(sub.loc[sub.factor == 0.8, metric].iloc[0])
            hi = float(sub.loc[sub.factor == 1.2, metric].iloc[0])
            rows.append((group, lo, hi))
        rows.sort(key=lambda r: max(abs(r[1]), abs(r[2])))
        y = np.arange(len(rows))
        for i, (group, lo, hi) in enumerate(rows):
            ax.barh(i, lo, height=0.55, color="#2b6cb0", alpha=0.85,
                    label="factor 0.8" if i == 0 else None)
            ax.barh(i, hi, height=0.55, color="#c53030", alpha=0.85,
                    label="factor 1.2" if i == 0 else None)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([labels[r[0]] for r in rows], fontsize=7.4)
        ax.set_xlabel("Cambio relativo (%)")
        ax.set_title(f"({'ab'[specs.index((metric, title))]}) {title}",
                     loc="left", fontsize=8.8)
        ax.grid(axis="x", alpha=0.25)
    axes[0].legend(loc="lower right", frameon=False, fontsize=7)
    fig.tight_layout()
    _save(fig, results_dir, "fig06_tornado_oat")


# ----------------------------------------------------------------------
# Figura 7: recuperación de parámetros
# ----------------------------------------------------------------------
def fig_recovery(results_dir: Path) -> None:
    setup_style()
    params = pd.read_csv(results_dir / "raw" / "estimation_parameters.csv")
    summary = pd.read_csv(results_dir / "tables" / "estimation_summary.csv")
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.6))
    for ax, matrix in zip(axes, ["A", "B", "pi"]):
        sub = params[params.matrix == matrix]
        for key in ["A", "B", "C", "D"]:
            s = sub[sub.scenario == key]
            ax.scatter(s["true"], s["estimated"], s=9, alpha=0.45,
                       color=SCENARIO_COLORS[key], edgecolors="none",
                       label=key if matrix == "A" else None)
        ax.plot([0, 1], [0, 1], color="#333333", ls="--", lw=0.9)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.set_xlabel("Valor verdadero")
        if matrix == "A":
            ax.set_ylabel("Valor estimado")
        mae_col = {"A": "mae_A_mean", "B": "mae_B_mean", "pi": "mae_pi_mean"}[matrix]
        mae = summary[mae_col].mean()
        matrix_label = "$\\pi$" if matrix == "pi" else matrix
        ax.set_title(f"({chr(97 + ['A','B','pi'].index(matrix))}) Matriz {matrix_label} "
                     f"(MAE={mae:.3f})", loc="left", fontsize=8.6)
    fig.legend(
        handles=[Patch(color=SCENARIO_COLORS[k], label=SCENARIO_NAMES[k]) for k in "ABCD"],
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=6.8,
        bbox_to_anchor=(0.5, -0.03),
    )
    fig.tight_layout(rect=(0, 0.10, 1, 1), w_pad=1.1)
    _save(fig, results_dir, "fig07_recuperacion")


# ----------------------------------------------------------------------
def make_all(results_dir: Path) -> None:
    results_dir = Path(results_dir)
    fig_model_diagram(results_dir)
    fig_examples(results_dir)
    fig_main_metrics(results_dir)
    fig_roc(results_dir)
    fig_sensitivity(results_dir)
    fig_oat(results_dir)
    fig_recovery(results_dir)
