# Sensibilidad e identificabilidad de un HMM para alertas tempranas de riesgo académico

**Actividad didáctica 2 — Módulo 2 — Curso de Simulación — 2026**

**Autor:** Juan Camilo Ríos Hernández  
**Profesor:** Julián Andrés Loaiza  
**Materia:** Simulación  
**Código:** PREICA2602B020045  
**Carrera:** Ingeniería de Desarrollo de Software y Datos  
**Fecha:** 09/11/2026  
**Repositorio:** <https://github.com/ANKARIUZ/S25---M-dulo-2.-Actividad-did-ctica-2>  
**Video pitch:** <https://drive.google.com/file/d/1ikG-yzzP3V0P0YI0nLtaEkDFP2RQaRB3/view?usp=sharing>

Este repositorio contiene un estudio de simulación reproducible sobre un Modelo Oculto de
Markov (HMM) aplicado a la detección temprana de riesgo académico en educación virtual. El
HMM tiene tres estados ocultos —comprometido (C), en riesgo (R) e inactivo (I)— y tres
observaciones semanales de actividad en el LMS: alta, media y baja. Se comparan cuatro
escenarios, se evalúa la recuperación de parámetros con Baum-Welch y se analiza la sensibilidad
global y local del sistema de alerta.

## Resultados principales

50 réplicas por escenario, 1.000 estudiantes por réplica, 16 semanas, semilla maestra 2025.

| Escenario | Detección a 4 semanas | AUC | Falsos positivos | Latencia (semanas) | Recuperación R→C |
|---|---:|---:|---:|---:|---:|
| A. Base | 0.382 [0.378, 0.386] | 0.837 [0.836, 0.838] | 0.111 | 3.74 | 0.220 |
| B. Señal débil | 0.078 [0.076, 0.081] | 0.723 [0.721, 0.724] | 0.038 | 5.62 | 0.220 |
| C. Intervención | 0.200 [0.196, 0.204] | 0.849 [0.848, 0.851] | 0.057 | 4.44 | 0.397 |
| D. Riesgo inicial alto | 0.489 [0.485, 0.494] | 0.832 [0.831, 0.833] | 0.134 | 3.06 | 0.221 |

Hallazgos centrales:

- La separabilidad de las emisiones es el límite de primer orden: pasar de δ = 1.0 a δ = 0.65
  reduce la detección de 38.2 % a 7.8 % y la AUC de 0.837 a 0.723.
- La persistencia del riesgo es el parámetro que más afecta la carga de alarmas: ±20 % produce
  cambios de +16.1 %/−15.3 % en detección y de +14.6 %/−17.0 % en falsos positivos.
- La intervención mejora la recuperación (39.7 %) y la AUC (0.849), pero reduce la detección a
  cuatro semanas (20.0 %) porque acorta los episodios de riesgo. Es la “paradoja de la
  intervención”.
- La distribución inicial cambia la prevalencia y la carga de alarmas, pero no la capacidad de
  discriminación por estudiante (AUC 0.832 vs. 0.837).

## Contenido del repositorio

```text
.
├── src/hmm_riesgo/          # Implementación y análisis
│   ├── hmm.py               # HMM discreto: Forward, Backward, Viterbi, Baum-Welch
│   ├── scenarios.py         # Estados, observaciones, matrices A, B y π
│   ├── simulation.py        # Simulación Monte Carlo y filtrado en línea
│   ├── metrics.py           # DR4, AUC, FPR, Brier, latencia, entropía, RMSE
│   ├── experiments.py       # E1-E4, recuperación y sensibilidad
│   ├── analysis.py          # IC95 %, Kruskal-Wallis, Mann-Whitney, Holm, Cliff
│   ├── figures.py           # Figuras 300 dpi (PNG y PDF)
│   ├── paper_tables.py      # Tablas del artículo desde los CSV
│   ├── paper_content.py     # Texto del artículo por bloques
│   └── paper_refs.py        # Referencias IEEE y citas numeradas
├── tests/test_hmm.py        # 11 pruebas unitarias
├── data/                    # Parámetros del modelo y referencias IEEE (JSON/CSV)
├── results/
│   ├── raw/                 # Réplicas, ROC, ejemplos, manifiesto
│   ├── tables/              # Descriptivos, pruebas, sensibilidad
│   └── figures/             # Figuras PNG 300 dpi y PDF
├── docs/
│   ├── Articulo_Actividad2_Modulo2.docx
│   ├── Articulo_Actividad2_Modulo2.pdf
│   └── Entrega_final.md    # Índice de entrega: documento, video y repositorio
├── run_all.py               # Reproduce experimentos y figuras
├── build_docx.py            # Construye el artículo en Word
├── requirements.txt
└── README.md
```

## Inicio rápido

Requisitos: Python 3.12 (probado con 3.12.14) y las versiones de `requirements.txt`.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Pruebas
python -m unittest discover -s tests -v

# Reproducir todo (experimentos + figuras): ~60 s
python run_all.py --force

# Construir el artículo en Word
python build_docx.py
```

En Linux/macOS, cambie `.venv\Scripts\Activate.ps1` por `source .venv/bin/activate`.

## Reproducibilidad

- **Semilla maestra:** 2025. Cada réplica deriva su semilla con SHA-256 a partir de
  `(semilla maestra, escenario, réplica)`, de modo que el orden de ejecución no altera los
  resultados.
- **Volumen:** 200 réplicas principales (4 escenarios × 50), 40 ajustes Baum-Welch, 225
  réplicas de la rejilla de sensibilidad y 280 réplicas OAT.
- **Entorno verificado:** Python 3.12.14, NumPy 2.3.5, pandas 3.0.1, SciPy 1.18.1,
  Matplotlib 3.11.2.
- **Manifiesto:** `results/raw/manifest.json` guarda versiones, semilla, hashes SHA-256 del
  código, tiempo de ejecución y volúmenes.
- **Pruebas:** 11 pruebas unitarias, incluidas Forward contra enumeración exhaustiva, Viterbi
  contra fuerza bruta, causalidad del filtro y monotonía de Baum-Welch.

## Repositorio en GitHub

El repositorio está publicado en:

**<https://github.com/ANKARIUZ/S25---M-dulo-2.-Actividad-did-ctica-2>**

Para actualizarlo después de un cambio local:

```powershell
git add .
git commit -m "Descripción del cambio"
git push
```

No suba `.venv/`, `.vendor/`, `.tmp/` ni las carpetas de previsualización `.dsh-office-*`
(ya están en `.gitignore`). El video puede cerrar mostrando la URL del repositorio.

## Entregables

| Entregable | Archivo |
|---|---|
| Artículo Q1 (Word) | `docs/Articulo_Actividad2_Modulo2.docx` |
| Artículo Q1 (PDF) | `docs/Articulo_Actividad2_Modulo2.pdf` |
| Video pitch (Google Drive) | https://drive.google.com/file/d/1ikG-yzzP3V0P0YI0nLtaEkDFP2RQaRB3/view?usp=sharing |
| Índice único de entrega | `docs/Entrega_final.md` |
| Código y resultados | `src/`, `results/` |

## Video pitch

El video está publicado en Google Drive:

**<https://drive.google.com/file/d/1ikG-yzzP3V0P0YI0nLtaEkDFP2RQaRB3/view?usp=sharing>**

Duración objetivo: 2–3 minutos, MP4 1080p, 16:9 y audio claro.

## Limitaciones

Las cohortes son simuladas: el estudio aísla mecanismos y ofrece reglas de diseño, pero no
estima parámetros de una cohorte real. Las pruebas reportadas son ejecuciones efectivas del
código; lo simulado es la población de entrada, no los resultados. El modelo es homogéneo, sin
covariables ni datos faltantes informativos, y usa tres estados y tres símbolos. Los valores
absolutos no deben generalizarse sin una validación con datos de un LMS.

## Licencia

MIT. Los textos y figuras pueden reutilizarse con atribución.
