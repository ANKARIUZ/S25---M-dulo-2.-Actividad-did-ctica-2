"""Tablas del artículo, construidas a partir de los CSV de resultados."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path(__file__).resolve().parents[2] / "results"
TABLES = RESULTS / "tables"


def _fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def _p(value: float) -> str:
    if value < 0.001:
        return "< 0.001"
    return f"{value:.3f}"


def table_literature() -> dict:
    rows = [
        [
            "Gupta et al. (2022) [[gupta2022]]",
            "E-learning universitario (OULA)",
            "HMM interpretable; 32 593 registros",
            "Accuracy 87.67–94.83 % y AUC 0.927–0.989; ventana óptima en el 1.º–2.º cuarto",
            "Un corpus; sin sensibilidad paramétrica ni identificabilidad",
        ],
        [
            "Boumi y Vela (2021) [[boumi2021]]",
            "Educación superior presencial (UCF)",
            "HMM multiperiodo de matrícula",
            "La matrícula mixta se asocia con peores resultados",
            "Descriptivo; sin alerta en línea ni incertidumbre",
        ],
        [
            "Maqsood et al. (2022) [[maqsood2022]]",
            "Trazas de engagement",
            "Mezcla de modelos Markov",
            "Segmenta subpoblaciones con patrones diferenciados",
            "Sin identificabilidad; depende de trazas ricas",
        ],
        [
            "Bacci y Bertaccini (2022) [[bacci2022]]",
            "Currículos universitarios",
            "HMM de mezcla sobre exámenes",
            "Clasifica trayectorias y detecta cuellos de botella",
            "Datos administrativos; sin alerta ni robustez",
        ],
        [
            "Tancini et al. (2024) [[tancini2024]]",
            "Alerta temprana",
            "HMM bayesiano",
            "Cuantifica la incertidumbre de las predicciones",
            "Capítulo exploratorio; no educación virtual",
        ],
        [
            "Urso et al. (2024) [[urso2024]]",
            "Clickstream web",
            "MHMM con ICL y Monte Carlo",
            "Selección de componentes con secuencias cortas",
            "No educativo; no evalúa estabilidad de alertas",
        ],
        [
            "Liu et al. (2023) [[liu2023]]",
            "Diagnóstico cognitivo longitudinal",
            "HMM restringido con Q-matriz",
            "Condiciones de identificabilidad más débiles",
            "Supuestos fuertes; no usa datos LMS",
        ],
    ]
    return {
        "id": "T1",
        "caption": "Comparación de trabajos recientes sobre HMM, analítica del aprendizaje y alertas tempranas.",
        "headers": ["Estudio", "Contexto", "Modelo y datos", "Aporte principal", "Limitación o vacío"],
        "rows": rows,
        "widths": [3.1, 3.0, 3.2, 4.2, 3.0],
        "font_size": 7.6,
        "note": "Elaboración propia a partir de las fuentes verificadas. Los corchetes remiten a la lista de referencias.",
    }


def table_parameters() -> dict:
    rows = [
        ["C", "0.82", "0.15", "0.03", "C", "0.80", "0.17", "0.03"],
        ["R", "0.22", "0.63", "0.15", "R", "0.10", "0.50", "0.40"],
        ["I", "0.04", "0.11", "0.85", "I", "0.02", "0.10", "0.88"],
    ]
    return {
        "id": "T2",
        "caption": "Parámetros del escenario base: matriz de transición A (izquierda) y matriz de emisión B (derecha).",
        "headers": ["Estado", "a_C", "a_R", "a_I", "Estado", "b_Alta", "b_Media", "b_Baja"],
        "rows": rows,
        "widths": [3.5, 1.3, 1.3, 1.3, 2.1, 1.6, 1.6, 1.6],
        "font_size": 8.5,
        "note": "Distribución inicial del escenario base: π = (0.70, 0.20, 0.10). Cada fila suma 1. C = comprometido, R = en riesgo, I = inactivo.",
        "merge_header": [(0, 3, "Matriz A: transición"), (4, 7, "Matriz B: emisión")],
    }


def table_scenarios() -> dict:
    rows = [
        ["A. Base", "—", "A₀", "B separable", "π₀", "Referencia"],
        ["B. Señal débil", "B", "A₀", "B(δ = 0.65)", "π₀", "Aislar la separabilidad de emisiones"],
        ["C. Intervención", "A", "A_C", "B separable", "π₀", "Aislar la recuperación R→C"],
        ["D. Riesgo inicial", "π", "A₀", "B separable", "π_D", "Aislar la condición inicial"],
    ]
    return {
        "id": "T3",
        "caption": "Diseño de escenarios: cada uno modifica un componente distinto del modelo base.",
        "headers": ["Escenario", "Componente", "A", "B", "π", "Propósito"],
        "rows": rows,
        "widths": [2.8, 2.0, 2.2, 3.2, 1.8, 4.0],
        "font_size": 8.2,
        "note": "B(δ) interpola entre una emisión confusa (δ = 0) y una separable (δ = 1). A_C incrementa la recuperación R→C de 0.22 a 0.40. π_D eleva el peso inicial de R de 0.20 a 0.40.",
    }


def table_main() -> dict:
    desc = pd.read_csv(TABLES / "main_descriptives.csv")
    labels = {
        "detection_rate_4w": "Detección a 4 semanas",
        "auc": "AUC",
        "fpr": "Falsos positivos semanal",
        "latency_mean": "Latencia (semanas)",
        "brier": "Brier",
        "prevalence_rmse": "RMSE de prevalencia",
    }
    rows = []
    for key in ["A", "B", "C", "D"]:
        for metric, label in labels.items():
            row = desc[(desc.scenario == key) & (desc.metric == metric)].iloc[0]
            digits = 2 if metric == "latency_mean" else 3
            rows.append(
                [
                    f"{key}. {row.get('scenario_name', key)}" if "scenario_name" in row else key,
                    label,
                    _fmt(row["mean"], digits),
                    _fmt(row["sd"], digits),
                    _fmt(row["min"], digits),
                    _fmt(row["max"], digits),
                    f"{_fmt(row['ci_low'], digits)}–{_fmt(row['ci_high'], digits)}",
                ]
            )
    # scenario_name no está en el CSV de descriptivos: recuperarlo del raw.
    raw = pd.read_csv(RESULTS / "raw" / "main_replications.csv")
    names = raw.drop_duplicates("scenario").set_index("scenario")["scenario_name"].to_dict()
    for row in rows:
        key = row[0].split(".")[0]
        row[0] = f"{key}. {names[key]}"
    return {
        "id": "T4",
        "caption": "Estadísticos descriptivos de las métricas principales por escenario (50 réplicas de 1.000 estudiantes).",
        "headers": ["Escenario", "Métrica", "Media", "DE", "Mín.", "Máx.", "IC 95 %"],
        "rows": rows,
        "widths": [3.6, 4.8, 1.6, 1.4, 1.4, 1.4, 2.8],
        "font_size": 7.6,
        "note": "IC calculado con la distribución t de Student (n = 50). La latencia se mide en semanas desde el inicio del estado R y solo se promedia entre estudiantes detectados.",
    }


def table_recovery() -> dict:
    df = pd.read_csv(TABLES / "estimation_summary.csv")
    rows = []
    for _, r in df.iterrows():
        rows.append(
            [
                f"{r['scenario']}. {r['scenario_name']}",
                _fmt(r["mae_A_mean"]),
                _fmt(r["mae_B_mean"]),
                _fmt(r["mae_pi_mean"]),
                _fmt(r["ll_gain_mean"], 2),
                _fmt(r["iterations_mean"], 1),
                f"{100 * r['convergence_rate']:.0f} %",
            ]
        )
    return {
        "id": "T5",
        "caption": "Recuperación de parámetros mediante Baum-Welch (10 ajustes por escenario, 300 estudiantes por ajuste).",
        "headers": ["Escenario", "MAE A", "MAE B", "MAE π", "Δ log L", "Iteraciones", "Convergencia"],
        "rows": rows,
        "widths": [3.8, 1.8, 1.8, 1.8, 1.7, 1.9, 2.2],
        "font_size": 8.2,
        "note": "MAE: error absoluto medio tras emparejar estados con el algoritmo húngaro. Δ log L = log L estimado − log L verdadero; valores positivos indican que el ajuste supera la verosimilitud de los parámetros generadores. Convergencia: proporción de ajustes que alcanzaron la tolerancia antes de 120 iteraciones.",
    }


def table_tests() -> dict:
    df = pd.read_csv(TABLES / "main_tests.csv")
    labels = {
        "detection_rate_4w": "Detección a 4 semanas",
        "auc": "AUC",
        "fpr": "Falsos positivos",
        "latency_mean": "Latencia",
        "brier": "Brier",
        "prevalence_rmse": "RMSE de prevalencia",
        "entropy": "Entropía",
        "recovery_rate": "Recuperación R→C",
        "mean_time_risk": "Tiempo en riesgo",
        "alarm_student_rate": "Cobertura de alarmas",
    }
    rows = []
    for _, r in df.iterrows():
        rows.append(
            [
                labels.get(r["metric"], r["metric"]),
                _fmt(r["H"], 2),
                str(int(r["df"])),
                _p(r["p_value"]),
                _fmt(r["epsilon_squared"]),
            ]
        )
    return {
        "id": "T6",
        "caption": "Pruebas de Kruskal-Wallis para diferencias entre los cuatro escenarios.",
        "headers": ["Métrica", "H", "gl", "p", "ε²"],
        "rows": rows,
        "widths": [6.0, 2.2, 1.2, 2.4, 2.2],
        "font_size": 8.0,
        "note": "ε² es el tamaño del efecto para Kruskal-Wallis; valores cercanos a 1 indican que el escenario explica casi toda la variación entre réplicas.",
    }


def table_oat() -> dict:
    df = pd.read_csv(TABLES / "sensitivity_oat.csv")
    labels = {
        "A_C": "Persistencia de C (A)",
        "A_R": "Persistencia de R (A)",
        "A_I": "Persistencia de I (A)",
        "B_C": "Emisión alta de C (B)",
        "B_R": "Emisión media de R (B)",
        "B_I": "Emisión baja de I (B)",
        "pi_R": "Peso inicial de R (π)",
    }
    rows = []
    for _, r in df.iterrows():
        rows.append(
            [
                labels[r["group"]],
                _fmt(r["factor"], 1),
                f"{r['detection_rate_4w_delta_pct']:+.1f}",
                f"{r['auc_delta_pct']:+.1f}",
                f"{r['fpr_delta_pct']:+.1f}",
            ]
        )
    return {
        "id": "T7",
        "caption": "Sensibilidad one-at-a-time: cambio porcentual de las métricas al perturbar cada grupo de parámetros en ±20 %.",
        "headers": ["Parámetro", "Factor", "Δ detección 4 s (%)", "Δ AUC (%)", "Δ FP (%)"],
        "rows": rows,
        "widths": [5.4, 1.6, 3.2, 2.4, 2.2],
        "font_size": 7.8,
        "note": "Factor 0.8 reduce el parámetro un 20 %; 1.2 lo aumenta un 20 %. Cada fila resume 20 réplicas de 500 estudiantes con números aleatorios comunes.",
    }


def table_pairwise() -> dict:
    df = pd.read_csv(TABLES / "main_pairwise.csv")
    df = df[df.metric.isin(["detection_rate_4w", "auc", "fpr"])]
    labels = {"detection_rate_4w": "Detección", "auc": "AUC", "fpr": "Falsos positivos"}
    rows = []
    for _, r in df.iterrows():
        rows.append(
            [
                labels[r["metric"]],
                r["scenario_1"],
                r["scenario_2"],
                _p(r["p_holm"]),
                f"{r['cliffs_delta']:+.2f}",
            ]
        )
    return {
        "id": "TA1",
        "caption": "Comparaciones por pares (Mann-Whitney U, corrección de Holm) para las métricas de detección.",
        "headers": ["Métrica", "Escenario 1", "Escenario 2", "p Holm", "δ de Cliff"],
        "rows": rows,
        "widths": [3.2, 2.2, 2.2, 2.6, 2.6],
        "font_size": 8.0,
        "note": "δ de Cliff: ±1 indica separación completa; valores positivos favorecen al escenario 1. Todas las comparaciones de detección y falsos positivos son significativas tras la corrección de Holm.",
    }


def table_environment() -> dict:
    rows = [
        ["Python", "3.12.10"],
        ["NumPy", "2.3.5"],
        ["pandas", "3.0.1"],
        ["SciPy", "1.18.1"],
        ["Matplotlib", "3.11.2"],
        ["python-docx", "1.2.0"],
        ["Semilla maestra", "2025"],
        ["Réplicas principales", "200 (4 escenarios × 50)"],
        ["Ajustes Baum-Welch", "40 (4 escenarios × 10)"],
        ["Rejilla de sensibilidad", "225 réplicas (15 celdas × 15)"],
        ["Perturbaciones OAT", "280 réplicas (14 configuraciones × 20)"],
        ["Tiempo de ejecución", "36.4 s en el entorno documentado"],
    ]
    return {
        "id": "TA2",
        "caption": "Entorno computacional y volumen de simulación.",
        "headers": ["Componente", "Versión o valor"],
        "rows": rows,
        "widths": [7.0, 8.0],
        "font_size": 8.2,
        "note": "Los hashes SHA-256 del código y el manifiesto completo se guardan en results/raw/manifest.json.",
    }


def all_tables() -> dict:
    return {
        t["id"]: t
        for t in [
            table_literature(),
            table_parameters(),
            table_scenarios(),
            table_main(),
            table_recovery(),
            table_tests(),
            table_oat(),
            table_pairwise(),
            table_environment(),
        ]
    }
