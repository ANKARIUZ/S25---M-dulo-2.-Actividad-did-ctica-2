"""Gestión de referencias IEEE y citas numeradas por orden de aparición."""

from __future__ import annotations

import json
import re
from pathlib import Path

CITATION_RE = re.compile(r"\[\[([A-Za-z0-9_]+)\]\]")


class CitationManager:
    def __init__(self, refs: dict[str, str]) -> None:
        self.refs = refs
        self.order: list[str] = []

    def cite(self, key: str) -> str:
        if key not in self.refs:
            raise KeyError(f"Referencia no registrada: {key}")
        if key not in self.order:
            self.order.append(key)
        return f"[{self.order.index(key) + 1}]"

    def render(self, text: str) -> str:
        return CITATION_RE.sub(lambda m: self.cite(m.group(1)), text)

    def reference_list(self) -> list[str]:
        return [f"[{i + 1}] {self.refs[key]}" for i, key in enumerate(self.order)]


def load_references() -> dict[str, str]:
    path = Path(__file__).resolve().parents[2] / "data" / "references.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    refs: dict[str, str] = {}
    for item in data:
        ieee = item["ieee"].strip()
        # Tipografía IEEE: rango de páginas con guion largo y acentos correctos.
        ieee = re.sub(r"pp\. (\d+)-(\d+)", r"pp. \1–\2", ieee)
        ieee = ieee.replace("avance en linea", "avance en línea")
        ieee = ieee.replace("en linea,", "en línea,")
        refs[item["key"]] = ieee
    return refs
