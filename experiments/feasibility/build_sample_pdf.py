"""Impaginazione locale della prova; richiede reportlab e pypdf.

Il layout è dimostrativo e non definisce i template finali del prodotto.
"""

import argparse
from html import escape
import json
from pathlib import Path
import re

from pypdf import PdfReader
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String, Circle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, KeepTogether, Image

from probe_codex import save


INK = colors.HexColor("#172B3A")
ACCENT = colors.HexColor("#157D91")
PALE = colors.HexColor("#EDF5F6")


def inline(text):
    text = text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def map_drawing(graph):
    drawing = Drawing(470, 410)
    positions = {}
    for i, node in enumerate(graph["nodes"]):
        y = 346 - i * 100
        positions[node["id"]] = y
        drawing.add(Rect(80, y, 310, 48, rx=6, ry=6, fillColor=PALE, strokeColor=ACCENT))
        drawing.add(String(235, y + 19, node["label"], fontName="DX", fontSize=11, textAnchor="middle", fillColor=INK))
    for edge in graph["edges"]:
        start = positions[edge["source"]]
        end = positions[edge["target"]] + 48
        drawing.add(Line(235, start, 235, end + 8, strokeColor=ACCENT, strokeWidth=1.4))
        drawing.add(Polygon([231, end + 8, 239, end + 8, 235, end], fillColor=ACCENT, strokeColor=ACCENT))
        lines = simpleSplit(edge["label"], "DX", 8.6, 204)
        for index, label in enumerate(lines):
            y = (start + end) / 2 + (len(lines) - 1) * 5.5 - index * 11 - 3
            drawing.add(String(247, y, label, fontName="DX", fontSize=8.6, fillColor=INK))
    return drawing


def svg_map(graph):
    positions = {node["id"]: 32 + i * 130 for i, node in enumerate(graph["nodes"])}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="500" viewBox="0 0 760 500" role="img">',
             '<title>' + escape(graph["title"]) + '</title>',
             '<rect width="760" height="500" fill="white"/>']
    for node in graph["nodes"]:
        y = positions[node["id"]]
        parts.append(f'<rect x="100" y="{y}" width="430" height="54" rx="6" fill="#EDF5F6" stroke="#157D91"/>')
        parts.append(f'<text x="315" y="{y+33}" text-anchor="middle" font-family="sans-serif" font-size="19" fill="#172B3A">{escape(node["label"])}</text>')
    for edge in graph["edges"]:
        start, end = positions[edge["source"]] + 54, positions[edge["target"]]
        parts.append(f'<path d="M315 {start} V{end-8}" stroke="#157D91" stroke-width="2" fill="none"/>')
        parts.append(f'<path d="M310 {end-8} L320 {end-8} L315 {end} Z" fill="#157D91"/>')
        lines = simpleSplit(edge["label"], "DX", 16, 410)
        for index, label in enumerate(lines):
            y = (start + end) / 2 - (len(lines) - 1) * 10 + index * 20 + 6
            parts.append(f'<text x="332" y="{y}" font-family="sans-serif" font-size="16" fill="#172B3A">{escape(label)}</text>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def balance_drawing():
    d = Drawing(470, 155)
    d.add(Polygon([219, 16, 251, 16, 235, 108], fillColor=PALE, strokeColor=INK))
    d.add(Line(75, 111, 395, 111, strokeColor=INK, strokeWidth=2))
    for center in (105, 365):
        d.add(Line(center, 111, center - 48, 54, strokeColor=INK))
        d.add(Line(center, 111, center + 48, 54, strokeColor=INK))
        d.add(Line(center - 50, 54, center + 50, 54, strokeColor=INK, strokeWidth=2))
    d.add(Rect(62, 58, 35, 30, fillColor=PALE, strokeColor=ACCENT))
    d.add(String(79, 68, "x", fontName="DXB", fontSize=17, textAnchor="middle", fillColor=INK))
    for x in (108, 122, 136):
        d.add(Circle(x, 65, 6, fillColor=ACCENT, strokeColor=ACCENT))
    for i in range(11):
        d.add(Circle(330 + (i % 6) * 13, 65 + (i // 6) * 15, 5, fillColor=ACCENT, strokeColor=ACCENT))
    d.add(String(105, 31, "x + 3", fontName="DX", fontSize=12, textAnchor="middle", fillColor=INK))
    d.add(String(365, 31, "11", fontName="DX", fontSize=12, textAnchor="middle", fillColor=INK))
    return d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("output/feasibility"))
    parser.add_argument("--font-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.input_dir.resolve()
    pdfmetrics.registerFont(TTFont("DX", str(args.font_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DXB", str(args.font_dir / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFontFamily("DX", normal="DX", bold="DXB", italic="DX", boldItalic="DXB")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("DXBody", fontName="DX", fontSize=10, leading=13.2, textColor=INK, spaceAfter=5))
    styles.add(ParagraphStyle("DXTitle", fontName="DXB", fontSize=19, leading=24, textColor=colors.black, spaceAfter=11, keepWithNext=True))
    styles.add(ParagraphStyle("DXHeading", fontName="DXB", fontSize=11.5, leading=15, textColor=colors.black, spaceBefore=8, spaceAfter=5, keepWithNext=True))
    styles.add(ParagraphStyle("DXSmall", fontName="DX", fontSize=8.5, leading=12, textColor=INK, spaceAfter=8))
    graph = json.loads((output / "concept_map.json").read_text())
    (output / "concept-map.svg").write_text(svg_map(graph), encoding="utf-8")
    story = []
    for index, filename in enumerate(("lesson1.json", "lesson2.json")):
        lesson = json.loads((output / filename).read_text())
        if index:
            story.append(PageBreak())
        story.append(Paragraph("DidactyX | Prova tecnica di generazione e PDF", styles["DXSmall"]))
        story.append(Paragraph(inline(lesson["title"]), styles["DXTitle"]))
        story.append(Paragraph("Obiettivi: " + inline("; ".join(lesson["objectives"])), styles["DXSmall"]))
        for section in lesson["sections"]:
            story.append(Paragraph(inline(section["heading"]), styles["DXHeading"]))
            for paragraph in section["text"].split("\n\n"):
                story.append(Paragraph(inline(paragraph).replace("\n", "<br/>"), styles["DXBody"]))
        example = lesson["worked_example"]
        worked = [Paragraph("Esempio svolto", styles["DXHeading"]), Paragraph(inline(example["problem"]), styles["DXBody"])]
        for i, step in enumerate(example["steps"], 1):
            worked.append(Paragraph(f"{i}. " + inline(step), styles["DXBody"]))
        worked.append(Paragraph("Risultato: " + inline(example["answer"]), styles["DXBody"]))
        story.append(KeepTogether(worked))
    story += [PageBreak(), Paragraph("Mappa e rappresentazione visiva", styles["DXTitle"]),
              Paragraph(inline(graph["title"]), styles["DXHeading"]), map_drawing(graph),
              Paragraph("Il significato dell’uguaglianza", styles["DXHeading"]), balance_drawing(),
              Paragraph("Nella prima lezione il costo del kit e i tre euro di trasporto hanno lo stesso valore del totale di undici euro. Per conservare l’uguaglianza si esegue la stessa operazione su entrambi i membri.", styles["DXBody"])]

    native_image = output / "native-illustration.png"
    if native_image.exists():
        from PIL import Image as PILImage
        width, height = PILImage.open(native_image).size
        story += [PageBreak(), Paragraph("Illustrazione generata con Codex", styles["DXTitle"]),
                  Paragraph("Una scatola e tre pesi equivalgono a undici pesi", styles["DXHeading"]),
                  Image(str(native_image), width=487, height=487 * height / width),
                  Paragraph("La scatola rappresenta il costo sconosciuto del kit. Ogni peso rappresenta un euro: a sinistra sono presenti tre pesi, a destra undici. La bilancia in equilibrio rappresenta l’uguaglianza x + 3 = 11.", styles["DXBody"]),
                  Paragraph("Togliendo tre pesi da entrambi i piatti, la scatola equivale agli otto pesi rimasti. È la stessa operazione eseguita nella prima lezione: x + 3 - 3 = 11 - 3, quindi x = 8.", styles["DXBody"]),
                  Paragraph("Questo campione verifica generazione raster, inserimento nel PDF e leggibilità. Il controllo di coerenza grafica su più lezioni rimane una verifica successiva.", styles["DXSmall"])]

    def footer(canvas, doc):
        canvas.setFont("DX", 8)
        canvas.setFillColor(INK)
        canvas.drawString(48, 26, "DidactyX · campione tecnico con dati fittizi")
        canvas.drawRightString(A4[0] - 48, 26, str(doc.page))

    target = output / "didactyx-feasibility-sample.pdf"
    SimpleDocTemplate(str(target), pagesize=A4, rightMargin=48, leftMargin=48,
                      topMargin=38, bottomMargin=44, title="DidactyX prova tecnica dei materiali",
                      author="DidactyX").build(story, onFirstPage=footer, onLaterPages=footer)
    reader = PdfReader(target)
    texts = [page.extract_text() for page in reader.pages]
    assert all(text.strip() for text in texts), "Pagina senza testo"
    assert "Faro" in "\n".join(texts)
    save(output / "pdf_results.json", {"pdf_created": True, "pages": len(reader.pages),
         "text_extractable": True, "svg_created": True, "vector_diagrams": True,
         "raster_image_embedded": native_image.exists(),
         "visual_inspection": "pending"})
    print(json.dumps({"pdf": target.name, "pages": len(reader.pages), "svg": "concept-map.svg"}))


if __name__ == "__main__":
    main()
