"""
Punto de entrada reproducible del proyecto.

Uso:
    python run_all.py --force
    python run_all.py --results-dir results

El script fija las semillas en ``experiments.py``, ejecuta los cuatro
experimentos, guarda un manifiesto de entorno y calcula hashes del código
para auditoría.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def code_hashes() -> dict[str, str]:
    files = sorted((SRC / "hmm_riesgo").glob("*.py")) + [
        ROOT / "run_all.py",
        ROOT / "tests" / "test_hmm.py",
    ]
    return {
        str(p.relative_to(ROOT)).replace("\\", "/"): sha256_file(p)
        for p in files
        if p.exists()
    }


def environment_manifest() -> dict:
    import matplotlib
    import numpy as np
    import pandas as pd
    import scipy

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=ROOT / "results",
        help="Carpeta de resultados (por defecto: ./results)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recalcula todo aunque existan resultados previos",
    )
    args = parser.parse_args()
    results_dir = args.results_dir.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "raw").mkdir(exist_ok=True)

    print("=" * 72)
    print("HMM de riesgo académico — ejecución reproducible")
    print("=" * 72)
    t0 = time.perf_counter()
    from hmm_riesgo.experiments import run_all
    from hmm_riesgo.figures import make_all

    manifest = run_all(results_dir, force=args.force)
    make_all(results_dir)
    manifest["environment"] = environment_manifest()
    manifest["code_sha256"] = code_hashes()
    manifest["runtime_seconds"] = round(time.perf_counter() - t0, 2)
    (results_dir / "raw" / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("-" * 72)
    print(f"Listo en {manifest['runtime_seconds']} s")
    print(f"Manifiesto: {results_dir / 'raw' / 'manifest.json'}")
    print(f"Tablas:    {results_dir / 'tables'}")
    print(f"Figuras:   {results_dir / 'figures'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
