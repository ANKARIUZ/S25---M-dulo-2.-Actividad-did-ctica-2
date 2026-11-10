"""
Construye el artículo en Word a partir de los bloques de contenido y los CSV.

Uso:
    python build_docx.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hmm_riesgo.paper_content import AFFILIATION, AUTHORS, KEYWORDS, TITLE, all_blocks
from hmm_riesgo.paper_refs import CitationManager, load_references
from hmm_riesgo.paper_tables import all_tables

OUT = ROOT / "docs" / "Articulo_Actividad2_Modulo2.docx"
FIG_DIR = ROOT / "results" / "figures"

TABLE_LABELS = {
    "T1": "Tabla 1",
    "T2": "Tabla 2",
    "T3": "Tabla 3",
    "T4": "Tabla 4",
    "T5": "Tabla 5",
    "T6": "Tabla A2",
    "T7": "Tabla A3",
    "TA1": "Tabla A1",
    "TA2": "Tabla A4",
}
TABLE_ALIGN = {
    "T1": ["left"] * 5,
    "T2": ["center"] * 8,
    "T3": ["left", "center", "center", "center", "center", "left"],
    "T4": ["left", "left", "center", "center", "center", "center", "center"],
    "T5": ["left", "center", "center", "center", "center", "center", "center"],
    "T6": ["left", "center", "center", "center", "center"],
    "T7": ["left", "center", "center", "center", "center"],
    "TA1": ["left", "center", "center", "center", "center"],
    "TA2": ["left", "center"],
}


# ----------------------------------------------------------------------
# Utilidades de formato
# ----------------------------------------------------------------------
def _set_run_font(run, name: str = "Times New Roman", size: float = 11, bold=None,
                  italic=None, color=None) -> None:
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def _set_cell_shading(cell, fill: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def _set_cell_margins(table, top: int = 30, bottom: int = 30, left: int = 70,
                      right: int = 70) -> None:
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for name, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        node = OxmlElement(f"w:{name}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tblPr.append(mar)


def _set_table_borders(table) -> None:
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge, sz, color in (
        ("top", 12, "000000"),
        ("bottom", 12, "000000"),
        ("left", 0, "FFFFFF"),
        ("right", 0, "FFFFFF"),
        ("insideH", 4, "BFBFBF"),
        ("insideV", 0, "FFFFFF"),
    ):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:val"), "single" if sz else "nil")
        node.set(qn("w:sz"), str(sz))
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), color)
        borders.append(node)
    tblPr.append(borders)


def _repeat_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:tblHeader")
    node.set(qn("w:val"), "true")
    trPr.append(node)


def _cant_split(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:cantSplit")
    node.set(qn("w:val"), "true")
    trPr.append(node)


def _add_page_number_footer(section) -> None:
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    _set_run_font(run, size=9, color=(0x55, 0x55, 0x55))
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), tag)
            run._r.append(fld)
        else:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = text
            run._r.append(instr)


def _add_header(section) -> None:
    paragraph = section.header.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("HMM y alertas tempranas en educación virtual")
    _set_run_font(run, size=8, italic=True, color=(0x66, 0x66, 0x66))
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), "BFBFBF")
    pBdr.append(bottom)
    pPr.append(pBdr)


def setup_document() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.59)
    section.page_height = Cm(27.94)
    for attr in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(section, attr, Cm(2.3))
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)
    _add_header(section)
    _add_page_number_footer(section)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(10.5)
    pf = normal.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.widow_control = True
    return doc


# ----------------------------------------------------------------------
# Bloques
# ----------------------------------------------------------------------
def add_title(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    _set_run_font(run, size=15, bold=True)


def add_authors(doc: Document, authors: str, affiliation: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(authors)
    _set_run_font(run, size=11, bold=True)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_after = Pt(10)
    p2.paragraph_format.line_spacing = 1.0
    for i, line in enumerate(affiliation.split("\n")):
        run2 = p2.add_run(line)
        _set_run_font(run2, size=9, italic=True, color=(0x44, 0x44, 0x44))
        if i < len(affiliation.split("\n")) - 1:
            run2.add_break()
    _add_rule(p2, color="999999", size=6)


def _add_rule(paragraph, color: str = "999999", size: int = 6) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_abstract(doc: Document, text: str, keywords: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run("Resumen")
    _set_run_font(run, size=10, bold=True)
    body = doc.add_paragraph()
    body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    body.paragraph_format.line_spacing = 1.15
    body.paragraph_format.space_after = Pt(4)
    run = body.add_run(text)
    _set_run_font(run, size=9.8)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p2.paragraph_format.line_spacing = 1.0
    p2.paragraph_format.space_after = Pt(8)
    run2 = p2.add_run(keywords)
    _set_run_font(run2, size=9.5, italic=True)
    _add_rule(p2, color="BFBFBF", size=4)


def add_heading(doc: Document, text: str, level: int) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.15
    if level == 1:
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        size = 11.5
    else:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        size = 10.5
    run = p.add_run(text)
    _set_run_font(run, size=size, bold=True)


def add_body(doc: Document, text: str, citations: CitationManager) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    rendered = citations.render(text)
    # Renderiza `código` en una fuente monoespaciada.
    for i, chunk in enumerate(re.split(r"`([^`]+)`", rendered)):
        if not chunk:
            continue
        run = p.add_run(chunk)
        if i % 2 == 1:
            _set_run_font(run, name="Consolas", size=9.2)
        else:
            _set_run_font(run, size=10.5)


def _parse_math(paragraph, expr: str) -> None:
    tokens = re.split(r"(_\{[^}]*\}|\^\{[^}]*\}|_[A-Za-z0-9]|\^[A-Za-z0-9])", expr)
    for token in tokens:
        if not token:
            continue
        text = token
        sub = sup = False
        if token.startswith("_{") and token.endswith("}"):
            text, sub = token[2:-1], True
        elif token.startswith("^{") and token.endswith("}"):
            text, sup = token[2:-1], True
        elif token.startswith("_") and len(token) == 2:
            text, sub = token[1], True
        elif token.startswith("^") and len(token) == 2:
            text, sup = token[1], True
        run = paragraph.add_run(text)
        _set_run_font(run, name="Cambria Math", size=10.5)
        if sub:
            run.font.subscript = True
        if sup:
            run.font.superscript = True


def add_equation(doc: Document, expr: str, number: int) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Cm(0.0)
    p.paragraph_format.left_indent = Cm(0.0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.tab_stops.add_tab_stop(Cm(8.5), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16.9), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run("\t")
    _parse_math(p, expr)
    run = p.add_run(f"\t({number})")
    _set_run_font(run, size=9.8)


def _table_cell_text(cell, text: str, font_size: float, bold: bool = False,
                     align: str = "left") -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    _set_run_font(run, size=font_size, bold=bold)


def add_table(doc: Document, spec: dict, citations: CitationManager) -> None:
    table_id = spec["id"]
    label = TABLE_LABELS[table_id]
    caption = doc.add_paragraph()
    caption.paragraph_format.keep_with_next = True
    caption.paragraph_format.space_before = Pt(8)
    caption.paragraph_format.space_after = Pt(3)
    caption.paragraph_format.line_spacing = 1.0
    run = caption.add_run(f"{label}. ")
    _set_run_font(run, size=9, bold=True)
    run2 = caption.add_run(spec["caption"])
    _set_run_font(run2, size=9)

    headers = spec["headers"]
    rows = spec["rows"]
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_borders(table)
    _set_cell_margins(table)

    widths = spec["widths"]
    total = sum(widths)
    widths = [w / total * 16.0 for w in widths]
    for i, width in enumerate(widths):
        for cell in table.columns[i].cells:
            cell.width = Cm(width)

    font_size = spec.get("font_size", 8.0)
    aligns = TABLE_ALIGN.get(table_id, ["left"] * len(headers))
    header = table.rows[0]
    _repeat_header(header)
    for i, text in enumerate(headers):
        cell = header.cells[i]
        _table_cell_text(cell, text, font_size, bold=True, align="center")
        _set_cell_shading(cell, "E8E8E8")
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    _cant_split(header)

    for row in rows:
        tr = table.add_row()
        _cant_split(tr)
        for i, value in enumerate(row):
            text = citations.render(str(value))
            _table_cell_text(
                tr.cells[i],
                text,
                font_size,
                bold=False,
                align=aligns[i] if i < len(aligns) else "left",
            )
            tr.cells[i].width = Cm(widths[i])
            tr.cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    if spec.get("note"):
        note = doc.add_paragraph()
        note.paragraph_format.line_spacing = 1.0
        note.paragraph_format.space_before = Pt(2)
        note.paragraph_format.space_after = Pt(10)
        run = note.add_run("Nota. ")
        _set_run_font(run, size=8, bold=True, italic=True)
        run2 = note.add_run(citations.render(spec["note"]))
        _set_run_font(run2, size=8, italic=True, color=(0x33, 0x33, 0x33))

    if len(rows) <= 10:
        for row in table.rows[:-1]:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.keep_with_next = True


def add_figure(doc: Document, filename: str, caption: str) -> None:
    path = FIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    widths = {
        "fig01_diagrama_hmm.png": 13.0,
        "fig02_trayectorias.png": 14.8,
        "fig03_metricas_escenarios.png": 16.0,
        "fig04_roc.png": 12.5,
        "fig05_sensibilidad.png": 16.0,
        "fig06_tornado_oat.png": 14.5,
        "fig07_recuperacion.png": 16.0,
    }
    width = widths.get(filename, 16.0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cap.paragraph_format.line_spacing = 1.0
    cap.paragraph_format.space_after = Pt(10)
    prefix, _, rest = caption.partition(". ")
    run1 = cap.add_run(prefix + ". ")
    _set_run_font(run1, size=9, bold=True)
    run2 = cap.add_run(rest)
    _set_run_font(run2, size=9)


def add_code(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.left_indent = Cm(0.2)
    p.paragraph_format.right_indent = Cm(0.2)
    p.paragraph_format.keep_together = True
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F4F4F4")
    pPr.append(shd)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        run = p.add_run(line)
        _set_run_font(run, name="Courier New", size=7.4)
        if i < len(lines) - 1:
            run.add_break()


def add_references(doc: Document, citations: CitationManager) -> None:
    for ref in citations.reference_list():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.75)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(ref)
        _set_run_font(run, size=8.8)


# ----------------------------------------------------------------------
def build() -> Path:
    doc = setup_document()
    doc.core_properties.title = TITLE
    doc.core_properties.author = AUTHORS
    doc.core_properties.subject = "Actividad didáctica 2 — Módulo 2 — Simulación — PREICA2602B020045"
    doc.core_properties.keywords = KEYWORDS
    doc.core_properties.comments = "Artículo Q1 reproducible sobre HMM y alertas tempranas."
    citations = CitationManager(load_references())
    tables = all_tables()
    blocks = all_blocks()

    eq_number = 0
    references_added = False
    for block in blocks:
        kind = block[0]
        if kind == "title":
            add_title(doc, block[1])
        elif kind == "authors":
            add_authors(doc, block[1], AFFILIATION)
        elif kind == "affiliation":
            continue
        elif kind == "abstract":
            add_abstract(doc, block[1], KEYWORDS)
        elif kind == "keywords":
            continue
        elif kind == "h1":
            if block[1] == "Referencias":
                add_heading(doc, block[1], 1)
                add_references(doc, citations)
                references_added = True
            else:
                add_heading(doc, block[1], 1)
        elif kind == "h2":
            add_heading(doc, block[1], 2)
        elif kind == "p":
            add_body(doc, block[1], citations)
        elif kind == "eq":
            eq_number += 1
            add_equation(doc, block[1], eq_number)
        elif kind == "table":
            add_table(doc, tables[block[1]], citations)
        elif kind == "figure":
            add_figure(doc, block[1], block[2])
        elif kind == "code":
            add_code(doc, block[1])
        elif kind == "pagebreak":
            doc.add_page_break()
        elif kind == "note":
            p = doc.add_paragraph()
            run = p.add_run(block[1])
            _set_run_font(run, size=8.5, italic=True)
        else:
            raise ValueError(f"Bloque desconocido: {kind}")

    if not references_added:
        add_heading(doc, "Referencias", 1)
        add_references(doc, citations)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)

    words = sum(len(p.text.split()) for p in doc.paragraphs)
    print(f"Documento: {OUT}")
    print(f"Palabras aproximadas: {words}")
    print(f"Referencias citadas: {len(citations.order)}")
    print(f"Ecuaciones: {eq_number}")
    return OUT


if __name__ == "__main__":
    build()
