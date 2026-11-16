"""Contenuti editoriali indipendenti dai renderer e verifiche dei rimandi reali."""
from .planning_schema import S, STRINGS, obj, array, validate, REVIEW

def block(kind, fields): return obj({"kind": {"type": "string", "enum": [kind]}, **fields})

BLOCK = {"anyOf": [
    block("paragraph", {"text": S}),
    block("definition", {"term": S, "text": S}),
    block("example", {"title": S, "steps": STRINGS, "conclusion": S}),
    block("code", {"language": S, "code": S, "explanation": S,
                   "execution": {"type": "string", "enum": ["check", "illustration"]},
                   "cases": array(obj({"stdin": STRINGS, "stdout": S}))}),
    block("list", {"items": STRINGS}),
    block("table", {"headers": STRINGS, "rows": array(STRINGS)}),
    block("callout", {"title": S, "text": S}),
    block("formula", {"expression": S, "explanation": S}),
]}
SECTION = obj({"id": S, "title": S, "objective_ids": STRINGS, "blocks": array(BLOCK)})
CONTENT = obj({
    "title": S, "lead": S, "objective_ids": STRINGS, "sections": array(SECTION),
    "summary": STRINGS, "self_check": array(obj({"question": S, "answer": S})),
    "terms": array(obj({"term": S, "definition": S})),
    "continuity": array(obj({"version_id": S, "section_id": S, "description": S})),
    "prerequisite_support": array(obj({"lesson_id": S, "explanation": S})),
    "source_ids": STRINGS, "teacher_notes": STRINGS,
})
OUTLINE = obj({"approach": S, "sections": array(obj({"id": S, "title": S,
    "objective_ids": STRINGS, "purpose": S})), "author_groups": array(STRINGS), "notes": STRINGS})
PART = obj({"sections": array(SECTION)})


def content_errors(data, context):
    try: validate(data, CONTENT)
    except (ValueError, TypeError) as error: return [str(error)]
    errors = []
    target = set(context["lesson"]["objective_ids"])
    if set(data["objective_ids"]) != target: errors.append("Gli obiettivi della lezione devono essere tutti coperti.")
    sections = data["sections"]
    ids = [s["id"] for s in sections]
    if not sections or len(ids) != len(set(ids)) or any(not i.strip() for i in ids):
        errors.append("Le sezioni devono esistere e avere codici univoci.")
    covered = set()
    for section in sections:
        if not section["title"].strip() or not section["blocks"]: errors.append("Una sezione è vuota.")
        goals = set(section["objective_ids"])
        if goals - target: errors.append("Una sezione richiama obiettivi estranei alla lezione.")
        covered |= goals
        for item in section["blocks"]:
            if item["kind"] == "table":
                if not item["headers"] or any(len(row) != len(item["headers"]) for row in item["rows"]): errors.append("Tabella con colonne incoerenti.")
            if item["kind"] == "formula" and "\\" in item["expression"]:
                errors.append("Le formule di questa versione richiedono notazione Unicode lineare, non comandi TeX.")
            if item["kind"] == "code" and item["execution"] == "check" and not item["cases"]:
                errors.append("Un esempio eseguibile deve avere almeno un caso con input e output atteso.")
    if covered != target: errors.append("Alcuni obiettivi non sono collegati alle sezioni effettive.")
    if not data["title"].strip(): errors.append("La lezione deve avere un titolo.")
    sources = {s["id"] for s in context["sources"]}
    if set(data["source_ids"]) - sources: errors.append("Sono citate fonti non fornite.")
    versions = {v["id"]: v for v in context["previous_materials"]}
    for ref in data["continuity"]:
        source = versions.get(ref["version_id"])
        if not source or ref["section_id"] not in {s["id"] for s in source["data"]["sections"]}:
            errors.append("Un richiamo rimanda a una versione o sezione inesistente.")
    used={ref['version_id'] for ref in data['continuity']}
    required={v['id'] for v in context['previous_materials'] if v['lesson_id'] in context['lesson']['prerequisite_lesson_ids']}
    if required-used: errors.append('La ripresa dei materiali propedeutici disponibili deve essere tracciabile in continuity.')
    missing = set(context["missing_prerequisites"])
    provided = {p["lesson_id"] for p in data["prerequisite_support"]}
    if provided != missing: errors.append("Occorre spiegare come sono sostenuti tutti i prerequisiti privi di contenuto.")
    return errors
