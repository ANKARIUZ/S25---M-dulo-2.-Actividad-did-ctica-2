"""
Contenido del artículo en formato de bloques.

Tipos de bloque:
    ("h1", texto), ("h2", texto), ("p", texto), ("eq", expresión),
    ("bullets", [textos]), ("table", id), ("figure", archivo, caption),
    ("code", texto), ("note", texto), ("pagebreak", None)
"""

from __future__ import annotations

TITLE = (
    "Sensibilidad e identificabilidad de un modelo oculto de Markov para "
    "alertas tempranas de riesgo académico en educación virtual"
)
AUTHORS = "Juan Camilo Ríos Hernández"
AFFILIATION = (
    "Ingeniería de Desarrollo de Software y Datos · Curso de Simulación — Módulo 2\n"
    "Profesor: Julián Andrés Loaiza · Código: PREICA2602B020045 · 09/11/2026"
)

ABSTRACT = (
    "La deserción en educación virtual exige alertas tempranas que detecten el riesgo antes de "
    "que se manifieste en el rendimiento. Los modelos ocultos de Markov (HMM) permiten separar "
    "estados latentes de compromiso de las observaciones semanales del sistema de gestión del "
    "aprendizaje (LMS), pero su desempeño depende de supuestos que rara vez se auditan con "
    "secuencias cortas y categóricas. Este artículo cuantifica, mediante simulación, la "
    "sensibilidad e identificabilidad de un HMM de tres estados (comprometido, en riesgo, "
    "inactivo) y tres niveles de actividad. Se diseñaron cuatro escenarios (base, señal débil, "
    "intervención temprana y riesgo inicial alto) y se ejecutaron 50 réplicas de 1.000 "
    "estudiantes durante 16 semanas, junto con una rejilla separabilidad×persistencia y "
    "perturbaciones one-at-a-time del 20 %. La detección se evaluó con la probabilidad filtrada, "
    "una regla de dos semanas y un umbral de 0.5. En el escenario base, la detección a cuatro "
    "semanas fue 38.2 % [IC95 %: 37.8–38.6] con AUC 0.837; la señal débil la redujo a 7.8 % y "
    "AUC 0.723, mientras que la intervención elevó la recuperación a 39.7 % pero bajó la "
    "detección a 20.0 %. La persistencia del riesgo fue el parámetro más influyente sobre la "
    "carga de alarmas: ±20 % produjo cambios de +16.1 %/−15.3 % en detección. La recuperación "
    "de parámetros empeoró con señales débiles (MAE de A: 0.017 vs. 0.041). Estos resultados "
    "ofrecen reglas de diseño y límites de identificabilidad para alertas tempranas basadas en HMM."
)
KEYWORDS = (
    "Palabras clave: modelo oculto de Markov; alertas tempranas; deserción en educación virtual; "
    "análisis de sensibilidad; identificabilidad; simulación Monte Carlo."
)


def front_matter() -> list[tuple]:
    return [
        ("title", TITLE),
        ("authors", AUTHORS),
        ("affiliation", AFFILIATION),
        ("abstract", ABSTRACT),
        ("keywords", KEYWORDS),
    ]


def introduction() -> list[tuple]:
    return [
        ("h1", "1. Introducción"),
        (
            "p",
            "La educación superior virtual dejó de ser una modalidad marginal y se consolidó como "
            "una alternativa masiva, flexible y global. Esa expansión también hizo visible un "
            "problema persistente: la deserción y el bajo rendimiento no son eventos súbitos, sino "
            "el desenlace de cambios graduales en la participación, la constancia y el uso de los "
            "recursos académicos [[desilva2022]]. Los sistemas de gestión del aprendizaje (LMS) "
            "registran semanalmente clics, entregas, lecturas y participación en foros; esas "
            "trazas contienen información temprana sobre el compromiso del estudiante, pero son "
            "ruidosas, incompletas y de gran dimensionalidad.",
        ),
        (
            "p",
            "El riesgo académico es un estado latente: no se observa directamente, solo se infiere "
            "a partir de señales observables. Un Modelo Oculto de Markov (HMM) formaliza esa "
            "intuición: la trayectoria de estados ocultos —por ejemplo, comprometido, en riesgo e "
            "inactivo— evoluciona como una cadena de Markov, y en cada semana emite una "
            "observación categórica o continua [[rabiner1989]], [[baum1966]]. La ventaja frente a "
            "un clasificador supervisado es que el HMM representa explícitamente la dinámica "
            "temporal y permite calcular, en línea, la probabilidad de que un estudiante esté en "
            "riesgo antes de que el resultado final se materialice.",
        ),
        (
            "p",
            "La literatura aplicada ha mostrado que los HMM son viables para la analítica del "
            "aprendizaje. Gupta et al. reportaron una exactitud de 87.67 %–94.83 % y un AUC de "
            "0.927–0.989 sobre 32 593 registros del corpus OULA, e identificaron la ventana óptima "
            "de alerta en el primer y segundo cuarto del curso [[gupta2022]]. Boumi y Vela "
            "usaron un HMM multiperiodo para relacionar los patrones de matrícula con el éxito "
            "académico [[boumi2021]]; Maqsood et al. modelaron el engagement con mezclas de "
            "modelos Markov [[maqsood2022]]; Bacci y Bertaccini minaron trayectorias curriculares "
            "con HMM de mezcla [[bacci2022]]; Wu y Xie predijeron contribuciones en foros de MOOC "
            "[[wu2026]]; y Tan y Yang combinaron clustering, análisis de secuencias y HMM para "
            "estudiar la resolución creativa de problemas [[tan2026]]. En conjunto, estos trabajos "
            "demuestran que el HMM captura estructura secuencial, pero suelen evaluar un solo "
            "corpus, con features y umbrales elegidos ad hoc, y rara vez auditan la estabilidad de "
            "las alertas frente a cambios en los parámetros.",
        ),
        (
            "p",
            "En paralelo, la estadística y la psicometría han avanzado en la teoría de "
            "identificabilidad de los HMM. Liu et al. propusieron condiciones genéricas más "
            "débiles que las clásicas para HMM discretos [[liu2023]]; David et al. extendieron el "
            "análisis a modelos con señales externas [[david2023]]; Liu y Culpepper estudiaron la "
            "identificabilidad de HMM heterogéneos en intervenciones educativas [[liu2025]]; y "
            "Wayman et al. analizaron modelos restringidos de clase latente con covariables "
            "[[wayman2026]]. También existen herramientas para estimar incertidumbre y errores "
            "estándar [[bacri2022]], para tratar datos faltantes y deserción [[pandolfi2023]] y "
            "para evaluar la sensibilidad a patrones de ausencia diseñados [[garnier2026]]. Sin "
            "embargo, ambos cuerpos de literatura casi no se tocan: los estudios aplicados "
            "reportan métricas predictivas, pero no traducen la incertidumbre paramétrica en "
            "estabilidad de las alertas; los estudios teóricos asumen secuencias largas o diseños "
            "con ítems controlados, no las secuencias semanales, cortas y categóricas de un LMS.",
        ),
        (
            "p",
            "Este artículo cierra esa brecha con un estudio de simulación. Plantea tres preguntas: "
            "P1) ¿cómo representar la evolución del riesgo académico en educación virtual mediante "
            "un HMM con estados, observaciones, matrices A, B y distribución π?; P2) ¿cómo "
            "influyen los parámetros del modelo y las distribuciones de probabilidad en la "
            "detección, la calibración y la carga de alarmas?; y P3) ¿qué tan reproducible y "
            "sensible es el modelo frente a cambios en las condiciones iniciales y en las matrices "
            "de transición y emisión?",
        ),
        (
            "p",
            "El objetivo general es diseñar, implementar y evaluar un HMM ejecutable que produzca "
            "resultados de simulación reproducibles y permita responder esas preguntas con "
            "evidencia cuantitativa. Los objetivos específicos son: (i) formalizar el modelo con "
            "notación rigurosa; (ii) implementar desde cero los algoritmos Forward, Viterbi y "
            "Baum-Welch, con pruebas de verificación; (iii) ejecutar cuatro escenarios y un "
            "análisis de sensibilidad global y local; y (iv) comunicar los hallazgos con "
            "estándares de artículo Q1, incluido un repositorio reproducible.",
        ),
        (
            "p",
            "El aporte es cuádruple: un HMM interpretable para alertas tempranas; un marco de "
            "simulación que separa los efectos de A, B y π; reglas de diseño que conectan la "
            "identificabilidad con la práctica; y un repositorio reproducible con semillas, pruebas "
            "y figuras a 300 dpi. La Sección 2 revisa el estado del arte; la 3 presenta el marco "
            "teórico; la 4 describe la metodología; la 5 reporta resultados; la 6 discute; y la 7 "
            "concluye.",
        ),
    ]


def state_of_the_art() -> list[tuple]:
    return [
        ("h1", "2. Estado del arte"),
        ("h2", "2.1. HMM en educación y analítica del aprendizaje"),
        (
            "p",
            "El uso de HMM en educación se organiza en tres frentes. El primero es la predicción "
            "temprana de riesgo: Gupta et al. construyen un HMM interpretable sobre rasgos de "
            "desempeño derivados de evaluaciones ligeras y reportan exactitud de 87.67 %–94.83 % "
            "y AUC de 0.927–0.989 en OULA [[gupta2022]]. El segundo es la caracterización de "
            "trayectorias: Boumi y Vela relacionan la matrícula mixta con peores resultados "
            "[[boumi2021]]; Maqsood et al. segmentan subpoblaciones de engagement con mezclas de "
            "Markov [[maqsood2022]]; Bacci y Bertaccini clasifican currículos universitarios con "
            "HMM de mezcla [[bacci2022]]; y Tan y Yang usan HMM para agrupar procesos cognitivos "
            "en problemas creativos [[tan2026]]. El tercero es la predicción de conducta en "
            "plataformas: Wu y Xie muestran que un HMM supera a kNN, regresión logística, random "
            "forest, XGBoost y LSTM al predecir contribuciones en foros de MOOC [[wu2026]].",
        ),
        (
            "p",
            "Estos estudios comparten una fortaleza —modelan dependencia temporal— y una "
            "limitación recurrente: evalúan el desempeño predictivo en un corpus y no examinan "
            "cómo cambian las alertas cuando se modifican las emisiones, las transiciones o la "
            "distribución inicial. Tampoco reportan la recuperación de los parámetros ni la "
            "estabilidad de las decisiones ante perturbaciones pequeñas, que es precisamente el "
            "tipo de evidencia que un comité editorial Q1 exigiría para sostener que el modelo es "
            "robusto y no un artefacto de un conjunto de datos.",
        ),
        ("h2", "2.2. Alertas tempranas y analítica institucional"),
        (
            "p",
            "La literatura sobre alertas tempranas ha desplazado la atención desde el algoritmo "
            "hacia el sistema socio-técnico. De Silva et al. documentan que la brecha de la "
            "deserción no es solo predictiva sino organizacional: los actores institucionales "
            "necesitan protocolos, gobernanza de datos y capacidad de intervención [[desilva2022]]. "
            "Tancini et al. proponen un HMM bayesiano para alerta temprana y cuantifican la "
            "incertidumbre predictiva [[tancini2024]]. Urso et al. comparan criterios de selección "
            "de componentes en HMM de mezcla con clickstream y Monte Carlo [[urso2024]]. "
            "Garnier-Villarreal et al. evalúan la sensibilidad de las predicciones de un HMM a "
            "patrones de ausencia diseñados [[garnier2026]]. Estos trabajos confirman que la "
            "incertidumbre importa, pero no ofrecen un mapa cuantitativo de qué parámetros mueven "
            "las alertas en el régimen de secuencias cortas y clases desbalanceadas.",
        ),
        ("h2", "2.3. Identificabilidad, estimación y sensibilidad"),
        (
            "p",
            "La identificabilidad de un HMM es una condición necesaria para interpretar sus "
            "estados: sin ella, distintas matrices A, B y π pueden generar la misma distribución "
            "de observaciones. Liu et al. muestran que las condiciones clásicas son demasiado "
            "fuertes y proponen condiciones genéricas para HMM discretos [[liu2023]]. David et al. "
            "analizan modelos entrada-salida con señales externas [[david2023]]; Liu y Culpepper "
            "extienden el análisis a HMM heterogéneos en estudios de intervención [[liu2025]]; y "
            "Wayman et al. estudian modelos restringidos de clase latente con respuestas "
            "politómicas y covariables [[wayman2026]]. En el plano de la estimación, Bacri et al. "
            "ofrecen una guía para calcular errores estándar e intervalos de confianza [[bacri2022]]; "
            "Pandolfi et al. proponen un HMM para datos longitudinales continuos con respuestas "
            "faltantes y deserción [[pandolfi2023]].",
        ),
        ("h2", "2.4. Síntesis y vacío identificado"),
        (
            "p",
            "La Tabla 1 resume siete trabajos representativos. Se observa un patrón: los estudios "
            "aplicados reportan métricas predictivas altas, pero rara vez cuantifican la "
            "sensibilidad paramétrica; los estudios metodológicos aportan teoría de "
            "identificabilidad, pero no la evalúan con secuencias cortas, categóricas y "
            "desbalanceadas como las de un LMS. El vacío es, por tanto, metodológico: falta un "
            "estudio de simulación que (i) separe los efectos de A, B y π; (ii) mida la "
            "recuperación de parámetros con verdad conocida; y (iii) traduzca esos efectos en "
            "métricas de alerta —detección, falsos positivos, latencia y calibración— para emitir "
            "reglas de diseño.",
        ),
        ("table", "T1"),
        (
            "p",
            "Ese vacío justifica el diseño de cuatro escenarios y dos análisis de sensibilidad que "
            "se presentan en la Sección 4. La contribución no es un nuevo algoritmo, sino una "
            "auditoría cuantitativa de un modelo estándar en el régimen en que realmente se usa: "
            "secuencias de 16 semanas, tres estados, tres símbolos y una regla de alarma en línea.",
        ),
    ]


def theory() -> list[tuple]:
    return [
        ("h1", "3. Marco teórico"),
        ("h2", "3.1. Distribuciones de probabilidad y simulación"),
        (
            "p",
            "El modelo usa tres distribuciones discretas. La distribución inicial de estados es "
            "categórica: S₁ ~ Cat(π), con π_i ≥ 0 y Σ_i π_i = 1. Cada fila de la matriz de "
            "transición es una distribución categórica sobre los K estados, y cada fila de la "
            "matriz de emisión es una distribución categórica sobre los M símbolos. Para evitar "
            "probabilidades nulas durante la estimación se usa un prior de Dirichlet simétrico, "
            "cuyo modo coincide con los conteos observados y cuya versión MAP conduce al "
            "suavizado (13).",
        ),
        (
            "p",
            "El tiempo de permanencia en un estado es una variable discreta con distribución "
            "geométrica: si la probabilidad de quedarse es a_ii, entonces P(D_i = d) = "
            "a_ii^{d−1}(1 − a_ii) y E[D_i] = 1/(1 − a_ii) (14). Esta relación es clave para "
            "interpretar la persistencia: un aumento de a_RR alarga los episodios de riesgo, "
            "cambia la prevalencia estacionaria y, con ella, la carga de alarmas. La distribución "
            "estacionaria de la cadena se obtiene como el autovector izquierdo de A asociado al "
            "autovalor 1.",
        ),
        ("h2", "3.2. Cadenas de Markov"),
        (
            "p",
            "Una cadena de Markov de primer orden sobre un conjunto finito S = {1, …, K} satisface "
            "la propiedad de Markov: el estado futuro depende del pasado solo a través del estado "
            "presente. Formalmente, para todo t ≥ 1 y toda trayectoria s_{1:t},",
        ),
        ("eq", "P(S_t = j | S_{1:t−1} = s_{1:t−1}) = P(S_t = j | S_{t−1} = i) = a_{ij}."),
        (
            "p",
            "La matriz A = [a_ij] es estocástica por filas: a_ij ≥ 0 y Σ_{j∈S} a_ij = 1 para "
            "todo i. La cadena es homogénea porque A no depende de t. La distribución estacionaria "
            "π* satisface π* = π* A; su existencia y unicidad requieren irreducibilidad y "
            "aperiodicidad, supuestos que se cumplen en los escenarios de este estudio porque "
            "todas las entradas de A son estrictamente positivas.",
        ),
        ("h2", "3.3. Modelo oculto de Markov"),
        (
            "p",
            "Un HMM añade una capa de observaciones. Sea O_t ∈ V = {1, …, M} la observación en t. "
            "El modelo se define por λ = (A, B, π), donde B = [b_j(k)] es la matriz de emisión:",
        ),
        ("eq", "b_j(k) = P(O_t = k | S_t = j),   b_j(k) ≥ 0,   Σ_{k∈V} b_j(k) = 1."),
        (
            "p",
            "La distribución inicial π_i = P(S₁ = i) satisface π_i ≥ 0 y Σ_i π_i = 1. El HMM "
            "impone dos supuestos: (i) la cadena oculta es de Markov; (ii) las observaciones son "
            "condicionalmente independientes dado el estado, es decir, P(O_t | S_{1:T}, O_{1:t−1}) "
            "= P(O_t | S_t). Bajo esos supuestos, la verosimilitud conjunta de una trayectoria "
            "s_{1:T} y sus observaciones o_{1:T} es:",
        ),
        (
            "eq",
            "P(s_{1:T}, o_{1:T} | λ) = π_{s_1} b_{s_1}(o_1) ∏_{t=2}^{T} a_{s_{t−1}s_t} b_{s_t}(o_t).",
        ),
        ("h2", "3.4. Evaluación y filtrado en línea"),
        (
            "p",
            "El algoritmo Forward define α_t(j) = P(o_{1:t}, S_t = j | λ). La recursión es:",
        ),
        (
            "eq",
            "α_t(j) = b_j(o_t) Σ_{i∈S} α_{t−1}(i) a_{ij},   α_1(j) = π_j b_j(o_1).",
        ),
        (
            "p",
            "La verosimilitud de la secuencia es P(o_{1:T} | λ) = Σ_j α_T(j). La probabilidad "
            "filtrada que se usa para la alerta en línea es:",
        ),
        ("eq", "π̂_t(j) = P(S_t = j | o_{1:t}, λ) = α_t(j) / Σ_{i∈S} α_t(i)."),
        (
            "p",
            "A diferencia de la probabilidad suavizada, π̂_t(j) solo usa información hasta t y, "
            "por tanto, es la que estaría disponible al final de la semana t en un sistema real. "
            "Esta distinción evita una fuga de información habitual en evaluaciones retrospectivas.",
        ),
        ("h2", "3.5. Decodificación y suavizado"),
        (
            "p",
            "El algoritmo Forward-Backward define β_t(i) = P(o_{t+1:T} | S_t = i, λ). La recursión "
            "es β_T(i) = 1 y:",
        ),
        ("eq", "β_t(i) = Σ_{j∈S} a_{ij} b_j(o_{t+1}) β_{t+1}(j)."),
        (
            "p",
            "Las probabilidades suavizadas γ_t(i) y las probabilidades de transición ξ_t(i,j) son:",
        ),
        (
            "eq",
            "γ_t(i) = α_t(i) β_t(i) / P(o_{1:T} | λ),   ξ_t(i,j) = α_t(i) a_{ij} b_j(o_{t+1}) β_{t+1}(j) / P(o_{1:T} | λ).",
        ),
        (
            "p",
            "Viterbi obtiene la trayectoria más probable con programación dinámica. Sea δ_t(j) la "
            "log-probabilidad máxima de terminar en j en t; entonces:",
        ),
        (
            "eq",
            "δ_t(j) = [max_{i∈S} δ_{t−1}(i) a_{ij}] b_j(o_t),   δ_1(j) = π_j b_j(o_1).",
        ),
        ("h2", "3.6. Aprendizaje por Baum-Welch"),
        (
            "p",
            "Baum-Welch es una instancia de EM [[baum1970]]. En el paso E se calculan γ y ξ con los "
            "parámetros actuales; en el paso M se actualizan:",
        ),
        (
            "eq",
            "π_i = γ_1(i),   a_{ij} = Σ_{t=1}^{T−1} ξ_t(i,j) / Σ_{t=1}^{T−1} γ_t(i),   b_j(k) = Σ_{t:o_t=k} γ_t(j) / Σ_{t=1}^{T} γ_t(j).",
        ),
        (
            "p",
            "Para estabilizar secuencias cortas se añade un pseudo-conteo α > 0 a cada conteo. "
            "La actualización MAP de una fila de A queda:",
        ),
        ("eq", "a_{ij} = (N_{ij} + α) / (Σ_{j′∈S} N_{ij′} + αK),"),
        (
            "p",
            "y de forma análoga para B y π. Se usa α = 0.5 (prior de Jeffreys). El algoritmo "
            "maximiza la verosimilitud de forma monótona, pero puede converger a óptimos locales y "
            "es invariante ante permutaciones de estados (label switching). Por eso la recuperación "
            "de parámetros se evalúa después de emparejar los estados estimados con los verdaderos "
            "mediante el algoritmo húngaro, y se reportan el error absoluto medio (MAE) y la "
            "ganancia de log-verosimilitud.",
        ),
        ("h2", "3.7. Regla de detección y métricas"),
        (
            "p",
            "Sea τ ∈ (0, 1) el umbral y k el número de semanas consecutivas requeridas. La alarma "
            "en t se activa si:",
        ),
        ("eq", "A_t = 1[ Σ_{u=t−k+1}^{t} 1(π̂_u(R) ≥ τ) = k ]."),
        (
            "p",
            "Para cada estudiante i, t_i^R es la primera semana en el estado verdadero R y L_i es "
            "la latencia desde ese inicio hasta la primera alarma posterior: L_i = min{t ≥ t_i^R : "
            "A_t = 1} − t_i^R. Si no hay alarma, L_i se censura en T − t_i^R. La tasa de detección "
            "a cuatro semanas (DR4) se calcula sobre el conjunto de estudiantes elegibles "
            "E₄ = {i : t_i^R ≤ T − 4}:",
        ),
        (
            "eq",
            "DR4 = (1/|E₄|) Σ_{i∈E₄} 1(L_i < 4).",
        ),
        (
            "p",
            "También se reportan la tasa de falsos positivos semanal FPR = FP/(FP + TN), la "
            "sensibilidad (recall), la precisión, el F1, la puntuación de Brier —error cuadrático "
            "medio entre π̂_t(R) y el indicador verdadero—, el RMSE de la prevalencia semanal "
            "—comparación entre la prevalencia media estimada y la verdadera— y la entropía media "
            "de la posterior, que mide la incertidumbre del filtro. El AUC se calcula con el "
            "estadístico de Mann-Whitney sobre todos los pares estudiante-semana, con empates "
            "promediados.",
        ),
        ("h2", "3.8. Identificabilidad y estabilidad"),
        (
            "p",
            "Un HMM es identificable si la distribución de las observaciones determina λ salvo "
            "permutaciones de estados. La identificabilidad es genérica cuando el conjunto de "
            "parámetros no identificables tiene medida cero, pero en muestras finitas la "
            "distinción práctica depende de la separabilidad de las emisiones, de la longitud de "
            "la secuencia y de la persistencia. Si dos estados emiten distribuciones parecidas, "
            "el cociente de verosimilitudes se acerca a 1 y la posterior tarda en separarse; si "
            "las secuencias son cortas, el número de transiciones observadas es pequeño y A se "
            "estima con alta varianza. Este trabajo operationaliza esas ideas con dos parámetros: "
            "δ, que interpola entre emisiones confusas y separables, y a_RR, que controla la "
            "duración de los episodios de riesgo.",
        ),
    ]


def methods() -> list[tuple]:
    return [
        ("h1", "4. Metodología"),
        ("h2", "4.1. Diseño del estudio"),
        (
            "p",
            "Se realizó un experimento de simulación factorial con cuatro escenarios, 50 réplicas "
            "por escenario y 1.000 estudiantes por réplica, seguidos durante T = 16 semanas. La "
            "unidad de análisis es el estudiante-semana; la unidad de replicación es la cohorte "
            "completa. La verdad latente se conoce porque los datos son generados por el propio "
            "modelo, lo que permite medir detección, latencia y recuperación de parámetros, algo "
            "imposible en una cohorte real. El diseño no pretende estimar parámetros de una "
            "población concreta, sino cartografiar cómo responden las alertas a cambios "
            "controlados en λ.",
        ),
        (
            "p",
            "Los estados ocultos son S = {C, R, I}: comprometido, en riesgo e inactivo. Las "
            "observaciones son V = {Alta, Media, Baja}, el nivel semanal de actividad en el LMS. "
            "La elección de tres estados y tres símbolos busca interpretabilidad y comparabilidad "
            "con la literatura; el marco se extiende a más estados o a emisiones gaussianas sin "
            "cambios conceptuales. La semana 1 es el inicio del semestre; no se modelan semanas "
            "previas ni vacaciones.",
        ),
        ("h2", "4.2. Especificación formal y escenarios"),
        (
            "p",
            "La Tabla 2 presenta la matriz A y la matriz B del escenario base, junto con la "
            "distribución inicial. La Tabla 3 describe los cuatro escenarios. El escenario A es la "
            "referencia; B reduce la separabilidad de emisiones a δ = 0.65; C aumenta la "
            "probabilidad de recuperación R→C de 0.22 a 0.40 y reduce R→I de 0.15 a 0.10; D eleva "
            "el peso inicial de R de 0.20 a 0.40. Así, B aísla el efecto de B, C el de A y D el de "
            "π.",
        ),
        ("table", "T2"),
        ("table", "T3"),
        (
            "p",
            "La emisión B(δ) se construye como una combinación convexa entre una matriz confusa "
            "B_conf y una separable B_sep: B(δ) = (1 − δ)B_conf + δB_sep. En δ = 0 las tres filas "
            "son casi idénticas y la observación no informa sobre el estado; en δ = 1 la "
            "separación es máxima. La persistencia se modifica reescalando las salidas de la fila "
            "R para que su suma sea 1 − a_RR, preservando la proporción relativa original. La "
            "distribución inicial se modifica multiplicando π_R y renormalizando.",
        ),
        ("h2", "4.3. Algoritmos y pseudocódigo"),
        (
            "p",
            "La implementación es propia, en Python y NumPy, sin depender de hmmlearn. Forward, "
            "Backward y Viterbi operan en espacio logarítmico y se vectorizan sobre las N "
            "secuencias; Baum-Welch usa la misma vectorización y actualiza A, B y π con suavizado "
            "de Dirichlet. El Algoritmo 1 resume una réplica.",
        ),
        (
            "code",
            "Algoritmo 1. Simulación y detección en línea\n"
            "Entrada: λ = (A, B, π), N, T, semilla s, umbral τ, persistencia k\n"
            "para n = 1..N:\n"
            "  S₁ ~ Cat(π); O₁ ~ Cat(B_{S₁})\n"
            "  para t = 2..T:\n"
            "    S_t ~ Cat(A_{S_{t−1}}); O_t ~ Cat(B_{S_t})\n"
            "  α₁ = π ⊙ B_{O₁}\n"
            "  para t = 2..T:\n"
            "    α_t = (α_{t−1}ᵀ A) ⊙ B_{O_t}\n"
            "  π̂_t = α_t / Σ_j α_t(j)\n"
            "  activar alarma si π̂_t(R) ≥ τ durante k semanas\n"
            "  calcular L_i, DR4, FPR, AUC, Brier y RMSE contra S_{1:T}\n"
            "fin para",
        ),
        (
            "p",
            "Las pruebas unitarias verifican Forward contra enumeración exhaustiva en modelos "
            "K = 2, M = 2, T = 5; Viterbi contra la ruta de máxima verosimilitud; la suma a 1 de "
            "las posteriores; la causalidad del filtro; la monotonía de Baum-Welch; la semejanza "
            "de las frecuencias simuladas con A y B; y la reproducibilidad con semillas fijas. "
            "También se verifica que la actualización de π use conteos, no probabilidades, un error "
            "fácil de introducir cuando se añade un pseudo-conteo.",
        ),
        ("h2", "4.4. Diseño experimental"),
        (
            "p",
            "Se ejecutaron cuatro experimentos. (E1) Comparación principal: 4 escenarios × 50 "
            "réplicas × 1.000 estudiantes × 16 semanas. (E2) Recuperación de parámetros: 4 "
            "escenarios × 10 réplicas × 300 estudiantes, con Baum-Welch inicializado en una "
            "versión perturbada de los parámetros verdaderos (ruido log-normal, σ = 0.35) y hasta "
            "120 iteraciones. (E3) Rejilla de sensibilidad: δ ∈ {0.2, 0.4, 0.6, 0.8, 1.0} × a_RR ∈ "
            "{0.60, 0.75, 0.90}, con 15 réplicas de 500 estudiantes por celda. (E4) Sensibilidad "
            "local one-at-a-time: 7 grupos de parámetros × 2 factores (0.8 y 1.2) × 20 réplicas de "
            "500 estudiantes, con números aleatorios comunes para reducir el ruido Monte Carlo.",
        ),
        (
            "p",
            "Los grupos de E4 son las filas de A (C, R, I), las filas de B (C, R, I) y π_R. En A se "
            "perturban las salidas del estado y se deja que la diagonal se ajuste, de modo que el "
            "factor modifica directamente la persistencia; en B se perturba la probabilidad del "
            "símbolo diagnóstico de cada estado (Alta para C, Media para R, Baja para I) y se "
            "renormaliza la fila; en π se multiplica π_R y se renormaliza. Esta parametrización "
            "evita el error de multiplicar una fila completa por un escalar y renormalizarla, lo "
            "que dejaría la fila idéntica.",
        ),
        ("h2", "4.5. Análisis estadístico"),
        (
            "p",
            "Para cada métrica se reportan media, desviación estándar, mínimo, máximo, mediana e "
            "intervalo de confianza del 95 % entre réplicas. Las diferencias entre escenarios se "
            "evalúan con Kruskal-Wallis; cuando el resultado es significativo, se aplican "
            "comparaciones por pares de Mann-Whitney con corrección de Holm y delta de Cliff. Se "
            "reporta ε² = (H − k + 1)/(n − k) como tamaño del efecto. Todos los contrastes usan "
            "α = 0.05 y se ejecutan en SciPy 1.18.1. Los valores se presentan con tres decimales; "
            "las latencias, con dos.",
        ),
        ("h2", "4.6. Reproducibilidad y entorno"),
        (
            "p",
            "El repositorio fija una semilla maestra (2025) y deriva semillas por réplica con "
            "SHA-256, de modo que el orden de ejecución no altera los resultados. Se documentan "
            "las versiones de Python (3.12.14), NumPy (2.3.5), pandas (3.0.1), SciPy (1.18.1) y "
            "Matplotlib (3.11.2), y se guardan hashes SHA-256 del código y un manifiesto de "
            "ejecución. El comando `python run_all.py --force` reproduce los 200 réplicas "
            "principales, los 40 ajustes de Baum-Welch, las 225 réplicas de la rejilla y las 280 "
            "réplicas OAT en aproximadamente 60 segundos en el entorno documentado. Las figuras se "
            "generan a 300 dpi en PNG y PDF.",
        ),
        (
            "p",
            "El estudio usa cohortes simuladas y no requiere aval ético, pero sus valores absolutos "
            "no son generalizables a una cohorte particular; la validez interna se refuerza con la "
            "verdad conocida, las semillas fijas y las pruebas unitarias.",
        ),
    ]


def results() -> list[tuple]:
    return [
        ("h1", "5. Resultados"),
        ("h2", "5.1. Comportamiento del modelo y trayectorias"),
        (
            "p",
            "La Figura 1 resume la estructura del HMM: tres estados ocultos, transiciones "
            "posibles entre ellos, emisiones categóricas y distribución inicial. La Figura 2 "
            "ilustra dos trayectorias simuladas. En el panel (a), un estudiante del escenario A "
            "pasa a riesgo en la semana 5 y la probabilidad filtrada supera el umbral durante dos "
            "semanas consecutivas, por lo que la alarma se activa de inmediato; en el panel (b), "
            "un estudiante del escenario B entra en riesgo en la semana 5, pero la señal es tan "
            "débil que la probabilidad filtrada no se sostiene por encima de 0.5 y no hay "
            "detección en 16 semanas. El panel (b) también muestra una falsa alarma en la semana "
            "4, antes del inicio verdadero del riesgo: el filtro confunde una fluctuación de "
            "actividad con riesgo.",
        ),
        ("figure", "fig01_diagrama_hmm.png", "Figura 1. Estructura del HMM de riesgo académico: estados ocultos, transiciones, emisiones y distribución inicial."),
        ("figure", "fig02_trayectorias.png", "Figura 2. Trayectorias individuales simuladas: (a) detección oportuna en el escenario A; (b) ausencia de detección y falsa alarma previa en el escenario B."),
        ("h2", "5.2. Comparación de escenarios"),
        (
            "p",
            "La Tabla 4 reporta los estadísticos descriptivos y la Figura 3 compara las tres "
            "métricas principales. La detección a cuatro semanas fue 38.2 % en A, 7.8 % en B, "
            "20.0 % en C y 48.9 % en D. El escenario B, con emisiones menos separables, redujo la "
            "detección en 30.4 puntos porcentuales y la AUC de 0.837 a 0.723, mientras que la FPR "
            "también bajó de 0.111 a 0.038: el filtro se volvió conservador porque la señal no "
            "alcanzaba el umbral. El escenario C, con mayor recuperación, mejoró la AUC a 0.849 y "
            "redujo la prevalencia media de riesgo de 0.261 a 0.197, pero la detección cayó a "
            "20.0 % y la latencia subió a 4.44 semanas; la razón es que los episodios de riesgo "
            "son más cortos y, con una regla de dos semanas, hay menos oportunidades de activar la "
            "alarma. El escenario D, con mayor peso inicial de riesgo, elevó la prevalencia a "
            "0.283 y la detección a 48.9 %, pero también la FPR a 0.134 y la cobertura de alarmas "
            "a 0.659.",
        ),
        ("table", "T4"),
        ("figure", "fig03_metricas_escenarios.png", "Figura 3. Comparación de la detección a cuatro semanas, la AUC y la tasa de falsos positivos por escenario (puntos: réplicas; barras: IC 95 %)."),
        (
            "p",
            "Kruskal-Wallis rechazó la igualdad entre escenarios en las diez métricas (p < 0.001; "
            "RMSE de prevalencia p = 0.0004), con ε² entre 0.556 y 0.937 (Anexo C, Tabla A2). Las "
            "comparaciones por pares confirmaron A > B y D > A en detección, y C > A en AUC, con "
            "deltas de Cliff cercanos a ±1 (Anexo C). La excepción es A vs. D en AUC (δ = 0.58): "
            "π cambia la prevalencia y la carga de alarmas sin alterar sustancialmente la "
            "discriminación por estudiante.",
        ),
        (
            "p",
            "La curva ROC promedio (Anexo A) confirma el orden: C y A se separan poco entre sí y "
            "mucho de B; D queda ligeramente por debajo de A en AUC, aunque su detección sea mayor "
            "porque hay más estudiantes en riesgo. Esta disociación entre AUC y DR4 es una "
            "advertencia metodológica: comparar sistemas de alerta solo por DR4 favorece a las "
            "cohortes con mayor prevalencia, aunque su discriminación sea igual o peor.",
        ),
        ("h2", "5.3. Recuperación de parámetros"),
        (
            "p",
            "La Tabla 5 muestra que Baum-Welch recuperó razonablemente los parámetros cuando la "
            "señal era separable: MAE de A = 0.017 en A, 0.019 en D, 0.030 en C y 0.041 en B; MAE "
            "de B = 0.018, 0.018, 0.027 y 0.027, respectivamente; y MAE de π entre 0.033 y 0.046. "
            "La ganancia de log-verosimilitud fue positiva en los cuatro escenarios (5.55–6.02), "
            "lo que indica que el ajuste superó la verosimilitud de los parámetros generadores, "
            "como se espera de un máximo de verosimilitud. La convergencia fue completa en A y D, "
            "y del 80 % en B y C; B necesitó más iteraciones (93.4 en promedio) y C también "
            "(63.1), consistente con una superficie de verosimilitud más plana.",
        ),
        ("table", "T5"),
        (
            "p",
            "El deterioro de B es la evidencia más directa de identificabilidad práctica: con "
            "emisiones confundibles, las transiciones se estiman peor (MAE 0.041 vs. 0.017) y el "
            "algoritmo tarda más en converger. La Figura A2 muestra que la nube de puntos se "
            "ensancha en B, sobre todo en las entradas de A asociadas a la persistencia. En C, la "
            "mayor velocidad de las transiciones también aumenta la varianza de A, aunque B se "
            "recupera bien porque las emisiones siguen siendo separables.",
        ),
        ("h2", "5.4. Sensibilidad global"),
        (
            "p",
            "La Figura 4 resume la rejilla δ × a_RR. La AUC crece de forma monotónica con ambos "
            "parámetros: pasa de 0.572 (δ = 0.2, a_RR = 0.60) a 0.879 (δ = 1.0, a_RR = 0.90). La "
            "detección a cuatro semanas es prácticamente nula por debajo de δ = 0.6 y a_RR = 0.75, "
            "y alcanza 80.1 % en la esquina superior derecha. La FPR no es monótona: en la esquina "
            "inferior izquierda es 0 porque el filtro nunca supera el umbral; en la esquina "
            "superior izquierda (δ = 0.2, a_RR = 0.90) sube a 0.442, porque el filtro se vuelve "
            "casi un prior y la prevalencia de riesgo es alta; y en la esquina superior derecha "
            "(δ = 1.0, a_RR = 0.90) es 0.228, porque las alarmas son más específicas pero los "
            "episodios de riesgo son largos. Este patrón no monotónico es una advertencia para la "
            "práctica: reducir la sensibilidad del umbral no siempre reduce la carga de alarmas.",
        ),
        ("figure", "fig05_sensibilidad.png", "Figura 4. Sensibilidad global de la AUC, la detección a cuatro semanas y la tasa de falsos positivos a la separabilidad de emisiones (δ) y a la persistencia del riesgo (a_RR)."),
        (
            "p",
            "Las celdas intermedias delimitan una frontera útil. Con δ = 0.6 y a_RR = 0.75, la AUC "
            "es 0.723, la detección 27.0 % y la FPR 0.116; con δ = 0.8 y a_RR = 0.75, la AUC sube a "
            "0.786 y la detección a 40.3 %. En términos prácticos, un sistema con δ < 0.6 y a_RR < "
            "0.75 no debería esperar una detección temprana confiable con una regla de dos semanas "
            "y τ = 0.5; necesitaría más observaciones por semana, más estados o un umbral "
            "calibrado a un presupuesto de falsos positivos.",
        ),
        ("h2", "5.5. Sensibilidad local"),
        (
            "p",
            "La Figura A3 (Anexo D) ordena los parámetros por su efecto sobre la detección y la AUC. La "
            "persistencia del riesgo (a_RR) es el parámetro dominante: reducirla un 20 % aumenta "
            "la detección 16.1 % y la FPR 14.6 %; aumentarla un 20 % reduce la detección 15.3 % y "
            "la FPR 17.0 %. La persistencia de C también importa para la carga de alarmas: "
            "reducirla un 20 % baja la FPR 9.8 %; aumentarla un 20 % la sube 12.2 %. En emisiones, "
            "la probabilidad de actividad media en R es el parámetro más influyente sobre la AUC "
            "(+1.19 %/−1.34 %), seguida de la probabilidad de actividad alta en C (+1.10 %/−1.49 "
            "%). El peso inicial de R tiene un efecto pequeño sobre la detección (<1.2 %), aunque "
            "cambia la prevalencia y la cobertura de alarmas.",
        ),
        (
            "p",
            "El análisis OAT confirma que la AUC es relativamente robusta a perturbaciones del 20 % "
            "en A (cambios < 1 %), pero sensible a la emisión de R (>1 %). La detección y la FPR, en "
            "cambio, son mucho más sensibles a A que a B, porque la persistencia controla cuántas "
            "semanas consecutivas puede sostener el filtro por encima del umbral. Esta asimetría "
            "explica por qué dos estudios con AUC similar pueden reportar cargas de alarmas muy "
            "distintas.",
        ),
        ("h2", "5.6. Evidencia de reproducibilidad"),
        (
            "p",
            "Todos los valores reportados provienen de ejecuciones efectivas del código, no de "
            "valores ilustrativos. La repetición con `--force` reprodujo exactamente las 200 "
            "réplicas, los 40 ajustes y las 225 réplicas de la rejilla; las 11 pruebas unitarias "
            "pasaron. El manifiesto guarda semilla, versiones, hashes y tiempo de ejecución. El "
            "Anexo E lista los comandos.",
        ),
    ]


def discussion() -> list[tuple]:
    return [
        ("h1", "6. Discusión"),
        ("h2", "6.1. Hallazgos principales"),
        (
            "p",
            "Tres resultados organizan la discusión. Primero, la separabilidad de las emisiones "
            "es el límite de primer orden para la detección temprana: cuando δ baja de 1.0 a 0.65, "
            "la AUC cae de 0.837 a 0.723 y la detección de 38.2 % a 7.8 %. No es solo una "
            "degradación gradual; es un cambio de régimen: el filtro deja de cruzar el umbral y la "
            "regla de dos semanas se vuelve inoperante. Segundo, la persistencia del riesgo "
            "controla la carga de alarmas y la detección de forma no trivial: más persistencia "
            "alarga los episodios y facilita la detección, pero también aumenta la FPR porque más "
            "estudiantes permanecen en la zona gris. Tercero, la intervención produce una paradoja "
            "aparente: mejora la recuperación y la AUC, pero reduce la detección a cuatro semanas, "
            "porque los episodios de riesgo son más cortos y la regla de dos semanas tiene menos "
            "oportunidades de activarse.",
        ),
        (
            "p",
            "La distribución inicial tiene un efecto distinto: cambia la prevalencia y la carga "
            "absoluta de alarmas, pero no la capacidad de discriminación por estudiante. En D, la "
            "AUC es 0.832, prácticamente igual a la de A (0.837), mientras que la detección y la "
            "FPR son mucho mayores. Esto implica que un sistema de alerta no puede evaluarse solo "
            "con DR4 o con número de alarmas: hay que reportar AUC, calibración y prevalencia, y "
            "comparar cohortes con el mismo punto de operación.",
        ),
        ("h2", "6.2. Comparación con la literatura"),
        (
            "p",
            "Los resultados son consistentes con la literatura aplicada en la dirección, aunque no "
            "en magnitud. Gupta et al. reportan AUC de 0.927–0.989 con features de desempeño y un "
            "corpus grande [[gupta2022]]; este estudio obtiene AUC de 0.837 con observaciones "
            "categóricas de actividad y secuencias de 16 semanas. La diferencia es informativa: "
            "las features de desempeño son más informativas que un único indicador semanal de "
            "actividad, y el corpus de OULA tiene más observaciones por estudiante. Wu y Xie "
            "encuentran que el HMM supera a baselines supervisados [[wu2026]]; aquí no se compara "
            "con baselines, porque el objetivo es auditar el HMM, no maximizar la predicción.",
        ),
        (
            "p",
            "La conexión con la teoría de identificabilidad es directa. Liu et al. advierten que "
            "las condiciones clásicas son demasiado fuertes [[liu2023]]; este estudio muestra que, "
            "incluso cuando el modelo es genéricamente identificable, la estimación práctica de A "
            "se deteriora con señales débiles (MAE 0.041 vs. 0.017). David et al. y Liu y "
            "Culpepper estudian modelos con señales externas y heterogeneidad [[david2023]], "
            "[[liu2025]]; aquí se aísla el mecanismo básico —emisiones, transiciones y π— para "
            "cuantificar su contribución. Garnier-Villarreal et al. evalúan la sensibilidad a "
            "datos faltantes [[garnier2026]]; este trabajo complementa esa agenda con sensibilidad "
            "a parámetros y a la regla de alarma.",
        ),
        ("h2", "6.3. Implicaciones para el diseño de alertas"),
        (
            "p",
            "Para un equipo que construye un sistema de alerta temprana, los resultados sugieren "
            "cinco reglas. (i) Antes de entrenar, estimar la separabilidad de las emisiones: si las "
            "distribuciones de actividad de C, R e I se solapan demasiado, el HMM no podrá detectar "
            "a tiempo con una regla simple. (ii) Calibrar el umbral a un presupuesto explícito de "
            "falsos positivos, no a 0.5 por defecto; la FPR depende de la prevalencia y de la "
            "persistencia. (iii) Reportar AUC, Brier, prevalencia y DR4 juntos, porque la DR4 "
            "favorece cohortes con más riesgo. (iv) Evaluar el sistema después de una intervención: "
            "si la intervención acorta los episodios, la detección a cuatro semanas puede caer "
            "aunque el modelo sea mejor. (v) Usar varias inicializaciones y emparejar estados antes "
            "de interpretar A y B; el label switching y los óptimos locales son riesgos reales.",
        ),
        ("h2", "6.4. Limitaciones y validez"),
        (
            "p",
            "La limitación principal es el uso de cohortes simuladas. Aunque los parámetros son "
            "plausibles y el diseño permite aislar mecanismos, los valores absolutos no son "
            "estimaciones de una cohorte real. La segunda limitación es la homogeneidad: A y B son "
            "constantes en el tiempo, no hay covariables, no hay datos faltantes informativos y no "
            "se modelan vacaciones ni cambios de curso. La tercera es la simplicidad: tres estados "
            "y tres símbolos pueden no capturar la riqueza de un LMS; sin embargo, esa simplicidad "
            "es deliberada para que los efectos sean interpretables. La cuarta es la regla de "
            "alarma: se fijaron τ = 0.5 y k = 2; otros umbrales cambiarían los niveles, aunque no "
            "la dirección de los efectos. La quinta es la estimación: Baum-Welch se inicializó "
            "cerca de la verdad, lo que favorece la convergencia; con inicializaciones aleatorias "
            "la recuperación sería peor.",
        ),
        (
            "p",
            "La validez interna es alta; la externa es condicional a secuencias cortas, categóricas "
            "y desbalanceadas. La validez de constructo depende de que la actividad semanal sea un "
            "proxy razonable del compromiso, que en un LMS real puede estar confundido por el "
            "diseño del curso.",
        ),
    ]


def conclusions() -> list[tuple]:
    return [
        ("h1", "7. Conclusiones y trabajo futuro"),
        (
            "p",
            "P1. El riesgo académico en educación virtual puede representarse con un HMM discreto "
            "cuyos estados ocultos son C (comprometido), R (en riesgo) e I (inactivo), y cuyas "
            "observaciones son el nivel semanal de actividad Alta, Media o Baja. La formulación "
            "λ = (A, B, π) permite calcular la probabilidad filtrada π̂_t(R) en línea, sin usar "
            "información futura, y traducirla en una alarma cuando supera un umbral durante k "
            "semanas. El modelo captura lo no observable —el estado de riesgo— a partir de lo "
            "observable, y su estructura es interpretable para un equipo de acompañamiento "
            "académico.",
        ),
        (
            "p",
            "P2. Los parámetros y las distribuciones influyen de manera diferenciada. La "
            "separabilidad de emisiones (δ) es el límite de primer orden: con δ = 0.65 la AUC cae "
            "a 0.723 y la detección a 7.8 %, frente a 0.837 y 38.2 % con δ = 1.0. La persistencia "
            "del riesgo (a_RR) controla la carga de alarmas y la detección: ±20 % produce cambios "
            "de +16.1 %/−15.3 % en detección y de +14.6 %/−17.0 % en FPR. La distribución inicial "
            "cambia la prevalencia y la carga absoluta de alarmas, pero no la AUC. La intervención "
            "mejora la recuperación (39.7 %) y la AUC (0.849), pero reduce la detección a cuatro "
            "semanas (20.0 %) porque acorta los episodios de riesgo.",
        ),
        (
            "p",
            "P3. El modelo es reproducible: las semillas fijas, los hashes y las pruebas permiten "
            "repetir exactamente los 200 réplicas principales y los 40 ajustes. Es sensible a las "
            "condiciones iniciales y a las matrices: pequeñas perturbaciones del 20 % en A o B "
            "producen cambios de hasta 17 % en FPR y 16 % en detección, y la recuperación de A se "
            "degrada de MAE 0.017 a 0.041 cuando la señal es débil. La sensibilidad no es un "
            "defecto del modelo, sino una propiedad que debe reportarse y controlarse.",
        ),
        (
            "p",
            "El aporte principal es convertir la teoría de identificabilidad en un conjunto de "
            "reglas prácticas para el diseño de alertas tempranas: estimar la separabilidad antes "
            "de entrenar, calibrar el umbral a un presupuesto de falsos positivos, reportar AUC y "
            "calibración junto con la detección, y reevaluar el sistema después de una "
            "intervención. El repositorio y las figuras a 300 dpi permiten auditar cada número.",
        ),
        (
            "p",
            "El trabajo futuro debe validar el marco con datos reales de LMS, incorporar datos "
            "faltantes y covariables, comparar HMM gaussianos y bayesianos, y diseñar umbrales "
            "costo-sensibles que ponderen falsos positivos y falsos negativos.",
        ),
    ]


def appendix() -> list[tuple]:
    return [
        ("pagebreak", None),
        ("h1", "Anexos"),
        ("h2", "Anexo A. Curvas ROC"),
        (
            "p",
            "La Figura A1 presenta las curvas ROC promedio de las 50 réplicas por escenario, con "
            "bandas de percentiles 2.5–97.5 %. Las curvas se interpolan en una rejilla común de "
            "FPR y se fuerzan a ser monótonas antes de promediar. La separación entre C y A es "
            "pequeña; B queda claramente por debajo; D es ligeramente inferior a A en AUC, aunque "
            "su detección sea mayor por la mayor prevalencia.",
        ),
        ("figure", "fig04_roc.png", "Figura A1. Curvas ROC promedio por escenario (50 réplicas; banda 2.5–97.5 %)."),
        ("h2", "Anexo B. Recuperación de parámetros"),
        (
            "p",
            "La Figura A2 compara los valores verdaderos y estimados de A, B y π tras el "
            "emparejamiento húngaro. La nube se concentra alrededor de la identidad en A y D; en B "
            "se abre, sobre todo en las entradas de A. Los puntos de π se estiman con error "
            "moderado porque solo hay una observación inicial por secuencia y el estado inicial se "
            "confunde con las primeras emisiones.",
        ),
        ("figure", "fig07_recuperacion.png", "Figura A2. Recuperación de parámetros: valores verdaderos vs. estimados para A, B y π (40 ajustes)."),
        ("h2", "Anexo C. Comparaciones por pares y pruebas globales"),
        ("table", "TA1"),
        ("table", "T6"),
        ("h2", "Anexo D. Sensibilidad local completa"),
        ("figure", "fig06_tornado_oat.png", "Figura A3. Sensibilidad local one-at-a-time: cambio porcentual de la detección a cuatro semanas y de la AUC al perturbar cada grupo de parámetros en ±20 %."),
        ("table", "T7"),
        ("h2", "Anexo E. Reproducibilidad"),
        ("table", "TA2"),
        (
            "code",
            "# Instalación y ejecución\n"
            "python -m venv .venv\n"
            ".venv\\Scripts\\activate        # Windows\n"
            "pip install -r requirements.txt\n"
            "python -m unittest discover -s tests -v\n"
            "python run_all.py --force\n"
            "python build_docx.py\n"
            "\n"
            "# Estructura\n"
            "src/hmm_riesgo/     # HMM, escenarios, simulación, métricas, figuras\n"
            "tests/              # 11 pruebas unitarias\n"
            "results/raw/        # réplicas, curvas ROC, manifest\n"
            "results/tables/     # descriptivos, pruebas, sensibilidad\n"
            "results/figures/    # PNG 300 dpi y PDF\n"
            "docs/               # artículo, guion y diapositivas\n",
        ),
        (
            "p",
            "Los resultados crudos, las tablas y las figuras se regeneran con el comando anterior. "
            "El manifiesto `results/raw/manifest.json` contiene la semilla maestra, las versiones "
            "de las librerías, los hashes SHA-256 del código y el tiempo de ejecución. Cualquier "
            "diferencia numérica respecto de este documento indicaría una modificación del código "
            "o del entorno, no una fluctuación aleatoria.",
        ),
    ]


def all_blocks() -> list[tuple]:
    blocks: list[tuple] = []
    blocks += front_matter()
    blocks += introduction()
    blocks += state_of_the_art()
    blocks += theory()
    blocks += methods()
    blocks += results()
    blocks += discussion()
    blocks += conclusions()
    blocks += [("h1", "Referencias")]
    blocks += appendix()
    return blocks
