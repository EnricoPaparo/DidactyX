"""Export editoriale del programma completo, senza nuove richieste generative."""

from html import escape
from pathlib import Path
import re
import threading
import unicodedata
import uuid

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, KeepTogether

from .planning_schema import plan_errors
from .store import DomainError

FONT_LOCK = threading.Lock()
KIND = {"theory": "Teoria", "laboratory": "Laboratorio", "assessment": "Verifica"}


def export_plan(program, version, directory):
    plan = version["data"]
    errors = plan_errors(plan)
    if errors: raise DomainError(-32602, "Questa versione richiede un controllo prima dell'esportazione.")
    with FONT_LOCK:
        if "DidactyxText" not in pdfmetrics.getRegisteredFontNames():
            fonts = Path(__file__).parent / "assets" / "fonts"
            pdfmetrics.registerFont(TTFont("DidactyxText", str(fonts / "DejaVuSans.ttf")))
            pdfmetrics.registerFont(TTFont("DidactyxBold", str(fonts / "DejaVuSans-Bold.ttf")))
            pdfmetrics.registerFontFamily("DidactyxText", normal="DidactyxText", bold="DidactyxBold")
    styles = {
        "title": ParagraphStyle("title", fontName="DidactyxBold", fontSize=23, leading=28, spaceAfter=16, textColor=colors.black, keepWithNext=True),
        "heading": ParagraphStyle("heading", fontName="DidactyxBold", fontSize=15, leading=20, spaceBefore=15, spaceAfter=9, keepWithNext=True),
        "lesson": ParagraphStyle("lesson", fontName="DidactyxBold", fontSize=11, leading=15, spaceBefore=11, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("body", fontName="DidactyxText", fontSize=10, leading=14.5, spaceAfter=6),
        "small": ParagraphStyle("small", fontName="DidactyxText", fontSize=8.5, leading=12, spaceAfter=6),
    }
    def clean(value):
        return escape(str(value).replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")).replace("\n", "<br/>")
    def paragraph(value, style="body"): return Paragraph(clean(value), styles[style])
    def field(label, values, fallback=None):
        if isinstance(values, list): values = "; ".join(values)
        if not values: values = fallback
        if not values: return []
        return [Paragraph("<b>" + clean(label) + ":</b> " + clean(values), styles["body"])]
    def hours(value): return f"{value:g}".replace(".", ",")
    def duration(value): return hours(value) + (" ora" if value == 1 else " ore")

    story = [paragraph("Programma annuale", "small"), paragraph(program["title"], "title")]
    story += field("Classe", program["class_label"], "Da definire")
    story += field("Descrizione", program["description"])
    story += field("Disciplina", plan["context"]["subject"])
    story += field("Contesto scolastico", plan["context"]["school_context"])
    story += field("Profilo della classe", plan["context"]["class_profile"])
    story += field("Conoscenze iniziali", plan["context"]["starting_knowledge"])
    story += field("Versione", str(version["version"]))
    story += [paragraph("Obiettivi annuali", "heading")]
    for goal in plan["context"]["goals"]: story.append(paragraph("• " + goal["description"]))
    budget = plan["context"]["hours"]
    story += field("Monte ore", hours(plan["context"]["total_hours"]) + " ore")
    story += field("Ripartizione", "; ".join(f"{label}: {hours(budget[key])} ore" for key, label in
                     [("theory", "teoria"), ("laboratory", "laboratorio"), ("assessment", "verifiche"), ("recovery", "riserva recupero"), ("buffer", "margine")]))
    story += field("Argomenti essenziali", plan["context"]["required_topics"])
    story += field("Argomenti facoltativi", plan["context"]["optional_topics"])
    story += field("Indicazioni del docente", plan["context"]["preferences"])
    if plan["context"]["assumptions"]:
        story += [paragraph("Ipotesi di progettazione", "heading")]
        for item in plan["context"]["assumptions"]: story.append(paragraph("• " + item))
    story += field("Riferimenti curricolari forniti", plan["context"]["curriculum_references"], "Nessun documento curricolare fornito nel brief.")

    goal_names = {g["id"]: g["description"] for g in plan["context"]["goals"]}
    lesson_names = {lesson["id"]: lesson["title"] for uda in plan["udas"] for lesson in uda["lessons"]}
    uda_names = {uda["id"]: uda["title"] for uda in plan["udas"]}
    project_names = {project["id"]: project["title"] for project in plan["projects"]}
    for index, uda in enumerate(plan["udas"], 1):
        story += [PageBreak(), paragraph(f"UDA {index}", "small"), paragraph(uda["title"], "title"), paragraph(uda["description"])]
        story += field("Periodo", uda["period"])
        story += field("Ore", "; ".join(f"{KIND[key]}: {hours(value)}" for key, value in uda["hours"].items()))
        story += field("Prerequisiti", uda["prerequisites"], "Non richiesti oltre alle conoscenze iniziali.")
        story += field("Obiettivi annuali collegati", [goal_names[g] for g in uda["annual_goal_ids"]])
        for label, key in [("Conoscenze", "knowledge"), ("Abilità", "skills"), ("Competenze", "competences"),
                           ("Concetti da trattare", "topics"), ("Concetti facoltativi", "optional_topics"),
                           ("Metodologie", "methods"), ("Valutazione", "assessment")]:
            story += field(label, uda[key])
        objectives = {g["id"]: g["description"] for g in uda["objectives"]}
        story += [paragraph("Obiettivi dell’UDA", "heading")]
        for item in uda["objectives"]: story.append(paragraph("• " + item["description"]))
        story += [paragraph("Lezioni previste", "heading")]
        for number, lesson in enumerate(uda["lessons"], 1):
            lesson_block = [paragraph(f"{number}. {lesson['title']} ({lesson['id']})", "lesson"),
                                      paragraph(f"{KIND[lesson['kind']]} · {duration(lesson['duration_hours'])}", "small"),
                                      paragraph(lesson["description"])]
            lesson_block += field("Obiettivi", [objectives[o] for o in lesson["objective_ids"]])
            lesson_block += field("Concetti", lesson["concepts"])
            lesson_block += field("Lezioni propedeutiche", [lesson_names[o] for o in lesson["prerequisite_lesson_ids"]], "Nessuna lezione precedente richiesta.")
            lesson_block += field("Metodologie", lesson["methods"])
            lesson_block += field("Progetti", [project_names[o] for o in lesson["project_ids"]])
            story.append(KeepTogether(lesson_block))
    if plan["projects"]:
        story += [PageBreak(), paragraph("Progetti progressivi", "title")]
        for project in plan["projects"]:
            story += [paragraph(project["title"], "heading"), paragraph(project["description"])]
            story += field("Competenze", project["competences"])
            for milestone in project["milestones"]:
                story += field("Tappa in " + uda_names[milestone["uda_id"]], milestone["description"])
                story += field("Risultato atteso", milestone["deliverable"])

    directory = Path(directory).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    title = unicodedata.normalize("NFKD", program["title"]).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-")[:70] or "programma-annuale"
    destination = directory / f"{slug}_v{version['version']}_{uuid.uuid4().hex[:8]}.pdf"
    temporary = destination.with_suffix(".pdf.tmp")
    def footer(canvas, doc):
        canvas.setFont("DidactyxText", 8)
        canvas.drawString(46, 26, f"DidactyX · Programma annuale · versione {version['version']}")
        canvas.drawRightString(A4[0] - 46, 26, str(doc.page))
    try:
        SimpleDocTemplate(str(temporary), pagesize=A4, leftMargin=46, rightMargin=46, topMargin=42,
                          bottomMargin=46, title=program["title"], author="DidactyX").build(story, onFirstPage=footer, onLaterPages=footer)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {"path": str(destination), "filename": destination.name, "version": version["version"]}
